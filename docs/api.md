[azarashi](../README.md) / API

# API
azarashi をプログラムから使うための関数と例外です。コマンドの使い方は [CLI](cli.md) を見てください。
## decode()
```python
azarashi.decode(msg, msg_type='nmea', timestamp=None)
```
- `msg`: デコードするメッセージです。
- `msg_type`: メッセージの形式です。`nmea`、`hex`、`ublox` のどれかを指定します。デフォルトは `nmea` です。`nmea` と `hex` のメッセージは str 型でも bytes 型でも渡せます。pySerial の `readline()` が返すバイト列は、そのまま渡してください。`ublox` のメッセージは bytes 型です。
  - `spresense` は `nmea` の別名です。
  - `net` は、[receiver](network.md#receiver) が受け取る33バイトのデータグラム形式です。先頭の1バイトが衛星 ID で、残りがメッセージ本体です。
- `timestamp`: メッセージを受信した時刻です。デフォルトは現在時刻です。メッセージにない年や日付は、この時刻から補います。[記録しておいたメッセージ](cli.md#record-and-replay)をあとからデコードするときに指定してください。タイムゾーンのない datetime は、実行環境のローカル時刻として扱います。
### Example
`decode()` はレポートオブジェクトを返します。返るクラスとフィールド、デコードした例は [Reports](reports.md) を見てください。
```python
>>> import azarashi
>>> report = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')
>>> report.disaster_category, report.magnitude
('緊急地震速報', '7.2')
```
## decode_stream()
```python
azarashi.decode_stream(stream, msg_type='nmea', callback=None, callback_args=(), callback_kwargs=None, unique=False, ignore_dcr=False, ignore_dcx=True, timestamp=None)
```
- `stream`: メッセージを読み込むストリームです。シリアルデバイスは pySerial で開いて渡してください。ファイルは `open(path, 'rb')` のように、バイナリモードで開くことをおすすめします。
- `msg_type`: メッセージの形式です。`nmea`、`hex`、`ublox` のどれかを指定します。デフォルトは `nmea` です。`spresense` は `nmea` の別名です。
  `net` はストリームでは使えません。データグラムごとに `decode(data, 'net')` を呼んでください。型検査でもこの違いを確認します。
- `callback`: レポートを受け取る関数です。`None` のときは、メッセージを一つデコードして、そのレポートを返します。関数を指定したときは、例外が発生するまでデコードを繰り返し、レポートができるたびに関数を呼び出します。関数は次のように呼び出されます。
```python
callback(report, *callback_args, **callback_kwargs)
```
- `callback_args`: 関数に渡す位置引数です。
- `callback_kwargs`: 関数に渡すキーワード引数です。
- `unique`: 重複したメッセージを無視するかどうかです。
  - `False`: 重複を無視しません。デフォルトです。
  - `True`: 記憶している同じメッセージは、2回目以降を無視します。時間が経っても記憶は失効しません。
  - 秒数: 同じメッセージでも、最後に受信してからその秒数を過ぎていれば、もう一度通知します。通知済みとして記憶しているメッセージは、抑制したときも受信時刻を更新します。例えば `unique=60` では、30秒おきに届く同じメッセージを定期的に通知することはありません。最後の受信から60秒を超えて間が空いたときに通知します。

  どちらも記憶するのは直近256件です。容量を超えて記憶から外れたメッセージは、再び通知します。

  重複の記憶はストリームのオブジェクトごとです。別のオブジェクトなら、`==` で等しくても記憶は独立しています。デバイスを開き直すときは [AzarashiReopenStream](#azarashireopenstream) を見てください。

  重複判定に使う具象クラス・`raw`・受信時刻は、コールバックを呼ぶ前に確定します。通知後にレポートの属性を変更しても履歴には反映しません。レポート本体は履歴に保持しません。

  コールバックが正常に戻った後に、そのメッセージを通知済みとして記憶します。コールバックが失敗すると例外をそのまま呼び出し元へ伝え、後から届く同じメッセージを再び通知できます。通知中に別スレッドが読んだ重複は抑制しますが、この予約による抑制では履歴の受信時刻を更新しません。失敗後にそのコピーを配信し直す仕組みもありません。コールバックを指定しない場合は、レポートを返す前に記憶します。
- `ignore_dcr`: DCR メッセージを無視するときは `True` を指定します。デフォルトは `False` です。
- `ignore_dcx`: DCX メッセージを無視するかどうかです。デフォルトは `True` で、DCX メッセージを無視します。DCX メッセージも受け取るときは `False` を指定してください。
- `timestamp`: ストリームのデータを受信した時刻です。デフォルトは現在時刻です。[記録しておいたデータ](cli.md#record-and-replay)を読み込むときに、記録した時刻を指定してください。この時刻はすべてのレポートに使われるので、リアルタイムに受信するときは指定しないでください。

秒数での重複判定にも、レポートの `timestamp` を使います。固定の `timestamp` で再生すると、記憶しているコピーとの時刻差は進みません。時計が巻き戻った場合も、前の受信時刻との差が指定秒数を超えるまで抑制します。

`msg_type` の指定が非対応の場合や、その形式を読むメソッドが `stream` にない場合は、入力を読む前に `AzarashiInvalidMessageError` を送出します。この分類は以前の呼び出し側との互換性のために維持しています。これらは設定を修正する必要があり、同じ引数で再試行しても先へ進みません。`AzarashiReadOn` を捕捉して読み続けるループには、対応する形式とストリームを渡してください。
### Example
シリアルデバイスを pySerial で開いて読み込み、デコードしたレポートオブジェクトを `print()` に渡します。
```python
>>> import azarashi
>>> import serial
>>> ser = serial.Serial('/dev/ttyS0', 9600)
>>> azarashi.decode_stream(ser, msg_type='ublox', callback=print)
```
## reset_reading_state()

```python
azarashi.reset_reading_state(stream, msg_type='nmea')
```

同じオブジェクトを利用者の判断で開き直すとき、azarashi が保持する読みかけと未配信電文を
破棄します。重複履歴は残します。戻り値は `None` です。

`stream` と `msg_type` は `decode_stream()` と同じ選び方で読み取り元を指定します。
その所有者の部分行・抽出済み NMEA 文・UBX バッファを、形式やメソッドをまたいで捨てます。
`.buffer` を共有するラッパーでは、他のラッパーから読める未配信データにも影響します。
独立した所有者と、各ラッパーの重複履歴には影響しません。

**共有元を使う読み取りとコールバックが全て終了してから呼んでください。**
読み取りを中断する機能や、実行中の通知を取り消す機能ではありません。
停止・通知の完了待ち → 旧経路を指定してリセット → close/open → 読み取り再開、の順で使います。
通常の受信タイムアウトではリセットせず、次の読み取りで続きを受信してください。

I/O の開閉、read、seek、OS やデバイス側の受信バッファの消去は行いません。
未使用の対象や繰り返しの呼び出しでも抽出データを新たに作りませんが、排他用のロックは保持します。
弱参照できない対象の保持制約は変わらず、全管理情報を解放する操作ではありません。
メソッドや `.buffer` を差し替える場合は旧経路を先に処理し、新経路にも過去の状態があればリセットします。
未対応形式やメソッド不足は、消去前に `decode_stream()` と同じ例外で報告します。

`decode_stream()` とリセットのロック待機時間は、下位ストリームの読み取りタイムアウトに
含まれません。共有元の別の read がブロックしていれば、その timeout 設定を超えて待つ場合があります。

## AzarashiException
azarashi が送出する例外は、すべてこのクラスを継承しています。azarashi が報告する失敗を一箇所で受けたいとき、たとえばまとめてログに記録するときに捕捉してください。

このクラス自身は、次に何をすべきかを表しません。それを表すのは次の3つです。読み取りのループで捕捉するのは、この3つです。

| 捕捉するクラス | 何をすべきか |
| --- | --- |
| [AzarashiReadOn](#azarashireadon) | 次のメッセージを読む |
| [AzarashiReopenStream](#azarashireopenstream) | ストリームを開き直す |
| [AzarashiStopReading](#azarashistopreading) | 読み取りをやめる |

ここで言うソケットは、`decode_stream()` に渡す TCP のストリームです。pySerial の `socket://` がその例です。[Network](network.md) の transmitter と receiver は UDP で、`decode_stream()` を通らないので、これらの例外とは関係ありません。

この3つ自体は送出されません。送出されるのは、3つをそれぞれ継承した、何が起きたかを表すクラスです。つまりループで捕捉するのは3つのどれかで、ログに出るのは継承した側の名前です。

```
AzarashiException
├── AzarashiReadOn                  次のメッセージを読む
│   ├── AzarashiDecodeError
│   │   ├── AzarashiInvalidMessageError
│   │   └── AzarashiNotImplementedError
│   └── AzarashiTimeoutError
├── AzarashiReopenStream            ストリームを開き直す
│   ├── AzarashiDisconnectedError
│   └── AzarashiStreamClosedError
└── AzarashiStopReading             読み取りをやめる
    └── AzarashiNoMoreData
```

何が起きたかを表すクラスは、仕様の改訂や対応形式の追加で増えることがあります。3つのほうを捕捉しておけば、増えても書き換えは要りません。

失敗の理由は `.message` に入り、`.instance` には失敗したデコーダが入る場合があります。読み取り障害やタイムアウトなど、デコーダを伴わない例外では `None` です。`str()` は電文があればそれも付けます。
## AzarashiReadOn
メッセージが手に入らなかったことを表すクラスです。読めないメッセージ、azarashi が扱えないメッセージ、読み終えていないメッセージが、すべてこのクラスの下にあります。

ストリームは無事です。捕捉したら `decode_stream()` をもう一度呼んでください。読めないメッセージはそのまま失われますが、次のメッセージから読み込みが続きます。読み終えていないメッセージは、次の呼び出しで続きから読み込みます。

ただし、[decode_stream()](#decode_stream) の引数の設定ミスも、互換性のためこのグループに含まれます。その場合は引数を修正してください。

例は [Minimal Loop](#minimal-loop) にあります。
## AzarashiDecodeError
メッセージをレポートにできなかったことを表すクラスです。次の二つの親にあたります。デコードの失敗をまとめて捕捉したいときは、これを捕捉してください。

`ValueError` を継承しています。標準ライブラリでも `json.JSONDecodeError` と `UnicodeDecodeError` が `ValueError` なので、azarashi を知らないレイヤーまで上がっても「入力データが不正」と正しく読まれます。
## AzarashiInvalidMessageError
デコードに失敗したときに送出される例外クラスです。エラーメッセージに失敗の理由が書かれているので、表示すると原因を調べる手がかりになります。

送出されるのは、メッセージそのものを読めないときです。チェックサムや CRC が合わない、長さが足りない、中身が空、どのデコーダに渡すか決められない、といった場合です。空のメッセージを渡したときも、ストリームが終わったわけではないのでこのクラスになります。仕様にないコード値を受け取っただけでは送出しません。そのコード値は `火山(コード番号：999)` のような名前にしてレポートに入れます。仕様が改訂されて新しいコードが増えても、メッセージは読めるままです。
## AzarashiNotImplementedError
実験的な配信など、azarashi が対応していないメッセージを受け取ったときに送出されます。そうした配信が始まると頻繁に送出されるので、デバッグのとき以外は捕捉して無視してもよいでしょう。

**`NotImplementedError` は継承していません。** あちらと、その親の `RuntimeError` は「書かれていないコードが呼ばれた」という意味です。衛星が実際に送ってきたメッセージを、上位のレイヤーが自分の不具合と取り違えてしまいます。azarashi がまだデコードできないメッセージは、不具合ではなく通常の通信です。
## AzarashiTimeoutError
pySerial などで `timeout` を指定して開いたストリームの読み取りが、データを返さずに終わったときや、行の途中までを返したときに送出されます。読みかけのデータは残っているので、もう一度 `decode_stream()` を呼べば続きから読み込みます。

**ソケットを読むときは、`socket.makefile()` に `settimeout()` を組み合わせないでください。** この組み合わせは Python 自身が避けるよう述べているもので、一度タイムアウトするとそのファイルオブジェクトは二度と読めなくなります。待っていたデータが届いても読めません。azarashi はこれを [AzarashiReopenStream](#azarashireopenstream) として報告します。読み直しても同じなので、開き直すほかありません。

タイムアウト付きでソケットを読むときは、pySerial の `socket://` を使ってください。こちらは読めた分を渡してくれるので、続きから読み込めます。
```python
port = serial.serial_for_url('socket://192.168.1.10:2000', timeout=1)
azarashi.decode_stream(port, 'ublox', print)
```

**`Exception` は継承しますが、`TimeoutError`・`OSError`・`EOFError` は継承しません。** `EOFError` にすると、データが終わったと読み違えられます。`EOFError` で止めるコードが、生きているストリームを打ち切ってしまいます。`TimeoutError` も使えません。あちらは `OSError` の一種で、[AzarashiReopenStream](#azarashireopenstream) と同じ網に入ります。`except OSError` で開き直すコードが、健全なデバイスを開き直すことになります。

このクラスは `AzarashiDecodeError` を継承していません。デコードに失敗したわけではないからです。プログラムの例は [Timeout](#timeout) にあります。
## AzarashiReopenStream
ストリームの読み取りそのものが失敗したことを表すクラスです。USB のシリアルデバイスを引き抜いたときや、TCP の接続が切れたときに送出されます。

そのストリームはもう使えません。読み直しても同じエラーがすぐに返るので、読み直し続けると待ち時間のないループになり、CPU を使い切ります。閉じて開き直してください。

`AzarashiReadOn` も `EOFError` も継承していません。読み続けてはいけないので前者ではなく、ストリームが終わったわけでもないので後者でもありません。どちらの外にあるため、**捕捉する順序を気にする必要がありません**。どちらも捕捉していないコードは、この例外をそのまま受け取ります。

pySerial のデバイスを差し直して読み続けるときは、`close()` して `open()` で**同じオブジェクトを開き直してください**。`unique` の重複の記憶はストリームごとなので、同じオブジェクトなら記憶が残り、記憶している警報を通知しなおしません。`serial.Serial()` で別のオブジェクトを作ると、新しい記憶で読み始めるため同じ警報をもう一度通知します。プログラムの例は [Reconnect](#reconnect) にあります。

この再接続時の保持は、弱参照できるストリームで保証します。pySerial のストリームはこれに該当します。自作ストリームで `__slots__` を使う場合は、基底クラスから弱参照への対応を継承していなければ、`__weakref__` も含めてください。

弱参照できないストリームは、状態を管理するためにオブジェクト自体を保持します。解放できるように、後の状態検索で `closed=True` を確認したときに記憶を破棄します。そのため、同じオブジェクトを開き直しても記憶の保持は保証しません。閉じている間に状態検索が行われなければ残ることもありますが、そのタイミングに依存しないでください。`closed` の取得や真偽判定で通常の例外が起きた場合は、閉鎖を確認できないため状態を保持し、他のストリームの処理を続けます。

pySerial の `serial.SerialException` も `OSError` の一種です。このクラスも `OSError` を継承しているので、`OSError` を捕捉しているコードはそのまま動きます。`serial.SerialException` を名指しで捕捉しているコードは、このクラスに書き換えてください。

何が起きたかは、これを継承した次の2つが表します。どちらも開き直せば済むので、ループで分ける必要はありません。ログや監視で区別したいときに使ってください。
### AzarashiDisconnectedError
読み取り中にデバイスや相手が消えたときに送出されます。USB のシリアルデバイスの引き抜き、TCP 接続のリセット、そのほかストリームが `OSError` として報告した失敗です。現場では起こるものとして備えてください。
### AzarashiStreamClosedError
読み取り中にストリームが閉じられたときに送出されます。閉じた `io` オブジェクトは `OSError` ではなく `ValueError` を送出するので、azarashi がこのクラスに変換します。

再接続処理が閉じたのなら、開き直せば済みます。ただし、**自分のプログラムが閉じたストリームを読み続けている**ときもこれになります。無条件に開き直すループは、そのバグを隠します。
## AzarashiStopReading
データが尽きたことを表すクラスです。読むものがなく、開き直す先もありません。`EOFError` を継承しているので、`EOFError` で止めているコードはそのまま動きます。

何が起きたかは、これを継承した次のクラスが表します。
### AzarashiNoMoreData
ファイルが末尾に達したときや、TCP の接続を相手側が閉じたときに送出されます。

壊れたものはないので、直すものもありません。ただ取るものがないだけです。デバイスを引き抜いたときは [AzarashiDisconnectedError](#azarashidisconnectederror) です。あちらは開き直せますが、こちらは開き直しても何も来ません。

**尽きたことが重大かどうかは、azarashi からは分かりません。** 記録ファイルを最後まで読んだのなら正常終了で、`azarashi` コマンドは終了コード 0 を返します。生きたフィードが途切れたのなら、その配信は戻りません。このクラスは事実だけを伝えるので、重大さの判断は呼び出し側に残ります。
レポートの直接生成・属性変更・継承のサポート範囲は [Reports](reports.md#construction-mutation-and-subclassing) を参照してください。

## Earlier Names
次の名前も使えます。それぞれ右の名前と同じものです。以前から使っているコードは、書き換えなくてもそのまま動きます。

| 以前の名前 | 今の名前 |
| --- | --- |
| `azarashi.qzss_dc_report` | `azarashi.reports` |
| `QzssDcrDecoderException` | `AzarashiInvalidMessageError` |
| `QzssDcrDecoderNotImplementedError` | `AzarashiNotImplementedError` |

レポートのクラスも短くなりました。所属するモジュールで修飾して書きます。

| 以前の名前 | 今の名前 |
| --- | --- |
| `QzssDcReportJmaTsunami` | `reports.dcr.Tsunami` |
| `QzssDcxJAlert` | `reports.dcx.JAlert` |
| `QzssDcReportBase` | `reports.base.Base` |

分け方はメッセージ形式です。`reports.dcr` が MT43、`reports.dcx` が MT44、両方に共通するものが `reports.base` です。仕様書が2冊に分かれている境界と同じところで割っています。

その下は、それぞれの形式の作りに従います。MT43 は災害種別ごとに電文の構造が違うので、クラスも災害種別ごとです。MT44 は CAMF という1つの構造を全員が共有し、発信機関によって拡張領域の読み方が変わるので、クラスは発信機関ごとです。

全クラスの一覧は [Reports](reports.md) にあります。

名前を変えたのは、azarashi が DCR 以外も扱うようになったからです。DCX のメッセージが読めなかったときも、同じ例外を送出します。今後ほかの測位衛星システムに対応しても同じです。そのとき `reports.ewss` のように仲間が増えても、クラス名はぶつかりません。

ログやエラー出力に出るクラス名は、今の名前に変わります。以前の名前で出力を検索しているときは、書き換えてください。
## Type Hints
azarashi は型ヒント付きで配布しています。mypy や pyright を使うと、関数の引数と戻り値や、レポートのフィールドの型を検査できます。

`decode()` と `decode_stream()` が返すレポートの型は `azarashi.Report` です。これは次の二つのどちらかです。クラスとフィールドの一覧は [Reports](reports.md) にあります。

- JMA-DC Report のレポート: `dcr.Base` とそのサブクラス
- DCX のレポート: `dcx.Base` とそのサブクラス

災害の種類ごとのフィールドを参照するときは、先に `isinstance()` でレポートのクラスを確かめてください。
```python
import azarashi
from azarashi import reports


def handler(report: azarashi.Report) -> None:
    if isinstance(report, reports.dcr.Tsunami):
        for arrival in report.expected_tsunami_arrival_times:  # datetime | None
            print(arrival)
    elif isinstance(report, reports.dcx.AlertBase):
        print(report.a6a7_hazard_onset_datetime)  # datetime | None
```
DCX のレポートには、メッセージの種類や内容によって設定されないフィールドがあります。例えば `a12_ellipse_centre_latitude` は、楕円の情報を持たないメッセージでは `None` になります。型も `float | None` と宣言してあるので、型検査が `None` の確認を促します。A1 から A10 までと `dcx_version` は必ず設定されるので `None` になりません。

警報を持たない `dcx.NullMsg` は、これらのフィールドを一つも持ちません。そのため警報のフィールドを読むときは `dcx.AlertBase` で絞ってください。`dcx.Base` で絞ると `dcx.NullMsg` も通ってしまいます。
## Examples
### Minimal Loop
形式や読み取りメソッドの設定ミスは、入力を消費せず同じ例外を繰り返すため、このループでは解消しません。設定を修正してください。
ストリームから読み続けるときの、いちばん短い形です。捕捉する3つのクラスが、そのまま何をすべきかを表します。
```python
import azarashi
import sys
import serial

with serial.Serial('/dev/ttyS0', 9600) as ser:
    while True:
        try:
            azarashi.decode_stream(ser, 'ublox', print)
        except azarashi.AzarashiReadOn as e:
            print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
        except azarashi.AzarashiReopenStream as e:
            print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            break
        except azarashi.AzarashiNoMoreData:
            break
```
読めないメッセージと、azarashi が扱えないメッセージは、ここで読み飛ばされます。何を飛ばしたかを気にしないなら、`AzarashiReadOn` の節は `pass` だけでも構いません。

3つは互いに継承関係がないので、**どの順番に書いても同じように動きます**。デバイスを差し直して読み続けたいときは、`break` の代わりにポートを開き直してください。[Reconnect](#reconnect) にその例があります。

`timeout` を付けて開いたストリームでも、この形のまま動きます。タイムアウトも `AzarashiReadOn` の下にあるからです。タイムアウトの合間に別の仕事をしたいときだけ、[Timeout](#timeout) のように節を分けてください。
### I/O Stream
例外処理を加えた簡単なプログラムの例です。記録したファイルを読み込みます。
```python
import azarashi
import sys

def example():
    with open('qzss.ubx', mode='rb') as f:
        while True:
            try:
                azarashi.decode_stream(f, msg_type='ublox', callback=print)
            except azarashi.AzarashiDecodeError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.AzarashiStopReading as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
```
### pySerial
[pySerial](https://pyserial.readthedocs.io/en/latest/) でシリアルポートを開いて `decode_stream()` に渡す例です。
```python
import azarashi
import sys
import serial
import pprint

def handler(report):
    pprint.pprint(report.get_params())

def example():
    with serial.Serial('/dev/ttyS0', 9600) as ser:
        while True:
            try:
                azarashi.decode_stream(ser, 'ublox', handler, unique=True)
            except azarashi.AzarashiDecodeError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.AzarashiStopReading as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
```
### Reconnect
USB のシリアルデバイスを抜き差ししても読み続ける例です。`AzarashiReopenStream` を捕捉したら、閉じて開き直します。

開き直すのは**同じオブジェクト**です。`unique` の重複の記憶はストリームごとなので、同じオブジェクトなら記憶が残り、既に通知した警報を抜き差しのたびに通知しなおしません。`serial.Serial()` で別のオブジェクトを作ると、記憶は消えて同じ警報をもう一度通知します。

読みかけのデータは、ストリームが壊れた時点で捨てられます。消えたデバイスから来たバイト列が、差し直したあとの最初のメッセージに混ざることはありません。
```python
import azarashi
import sys
import time
import serial

def example():
    ser = serial.Serial('/dev/ttyS0', 9600)
    while True:
        try:
            azarashi.decode_stream(ser, 'ublox', print, unique=True)
        except azarashi.AzarashiReopenStream as e:
            print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            ser.close()
            time.sleep(1)  # デバイスが戻るのを待つ
            try:
                ser.open()  # 同じオブジェクトなので重複の記憶が残る
            except OSError as not_back_yet:
                print(f'# [{type(not_back_yet).__name__}] {not_back_yet}', file=sys.stderr)
        except azarashi.AzarashiReadOn as e:
            print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
        except azarashi.AzarashiStopReading as e:
            print(f'{e}', file=sys.stderr)
            return 0

exit(example())
```
### Timeout
シリアルポートを `timeout` 付きで開くと、読み取りがタイムアウトした際に `AzarashiTimeoutError` を捕捉して別の仕事ができます。以下は、その機会に終了の合図を確認する例です。

`timeout` は下位ストリームの個々の読み取りに適用され、`decode_stream()` 全体の実行時間を制限しません。データが流れ続ける場合は、通知対象外の電文や重複も含めて読み続けるため、タイムアウトせず終了の合図を確認できないことがあります。この例は停止までの時間を保証しません。

`AzarashiTimeoutError` は [AzarashiReadOn](#azarashireadon) の下にあります。タイムアウトの合間に別の仕事をしないのであれば、この節をやめて `AzarashiReadOn` にまとめても構いません。両方書くときは、`AzarashiTimeoutError` を先に書いてください。

読みかけのデータは残っています。もう一度 `decode_stream()` を呼べば、途中から読み続けます。
```python
import azarashi
import signal
import sys
import serial

stopping = False

def stop(signum, frame):
    global stopping
    stopping = True

signal.signal(signal.SIGTERM, stop)

def example():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        while True:
            try:
                azarashi.decode_stream(ser, 'ublox', print, unique=True)
            except azarashi.AzarashiTimeoutError:
                if stopping:
                    return 0
                continue  # 読み取りがタイムアウトした。読みかけの続きを待つ
            except azarashi.AzarashiDecodeError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.AzarashiStopReading as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
```
### Field Receiver
現場に置きっぱなしにする受信機のお手本です。ここまでの例を一つにまとめてあります。3つの行動、抜き差しからの復帰、終了の伝え方、そして**自分の失敗を読み取りループに混ぜないこと**を入れました。

```python
import logging
import signal
import sys
import time

import azarashi
import serial

#: 抜き差ししても変わらないパス。/dev/ttyUSB0 は差し直すと ttyUSB1 になることがある
PORT = '/dev/serial/by-id/usb-u-blox_AG_u-blox_GNSS_receiver-if00'
#: 開き直すまでに待つ秒数
BACKOFF = (1, 2, 5, 10, 30)

logger = logging.getLogger('receiver')
stopping = False


def stop(signum, frame):
    global stopping
    stopping = True


def wait(seconds):
    """停止の合図に早く気づくため、短く刻んで待つ"""
    for _ in range(seconds):
        if stopping:
            return
        time.sleep(1)


def deliver(report):
    """警報を渡す。ここでの失敗はこのプログラムのものなので、ここで始末する"""
    try:
        print(report, flush=True)
    except Exception:
        # 配信の失敗をログに残し、受信を続ける
        logger.exception('could not hand on the %s alert', report.message_type)


def read(port):
    """読めるものがなくなるまで読む。終了コードか、開き直しを求める None を返す"""
    while not stopping:
        try:
            azarashi.decode_stream(port, 'ublox', deliver, unique=3600 * 24, ignore_dcx=False)
        except azarashi.AzarashiTimeoutError:
            pass  # 時間内に届かなかった。stopping を見にいくために一周する
        except azarashi.AzarashiReadOn as e:
            logger.warning('[%s] %s', type(e).__name__, e)  # 1通落ちただけ。ストリームは無事
        except azarashi.AzarashiStopReading as e:
            logger.info('%s', e)
            return 0  # データが尽きた。開き直す先はない
        except azarashi.AzarashiStreamClosedError as e:
            logger.error('[%s] %s: このプログラムがポートを閉じた', type(e).__name__, e)
            return 1  # 自分の不具合。開き直すループはそれを隠す
        except azarashi.AzarashiReopenStream as e:
            logger.warning('[%s] %s', type(e).__name__, e)
            return None  # デバイスが消えた。呼び出し側が開き直す
    return 0


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    # ポートを指定せずに作る。1つのオブジェクトを開いて閉じて開き直すため
    port = serial.Serial(baudrate=9600, timeout=1)
    port.port = PORT

    attempt = 0
    while not stopping:
        try:
            port.open()
        except OSError as e:
            seconds = BACKOFF[min(attempt, len(BACKOFF) - 1)]
            logger.warning('[%s] %s: %d秒後に開き直す', type(e).__name__, e, seconds)
            attempt += 1
            wait(seconds)
            continue
        logger.info('reading %s', port.port)
        attempt = 0
        try:
            code = read(port)
        finally:
            port.close()
        if code is not None:
            return code
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

このコードが守っていることを、上から順に挙げます。

**捕捉の順序には規則があります。** 同じ枝の中では葉を先に書いてください。`AzarashiTimeoutError` は `AzarashiReadOn` の下、`AzarashiStreamClosedError` は `AzarashiReopenStream` の下にあるので、先に書かないと、親の節が先に捕まえてしまいます。一方、枝どうしにあたる `AzarashiReadOn`、`AzarashiReopenStream`、`AzarashiStopReading` の3つは互いに継承関係がないので、**どの順番でも構いません**。

**この例では、配信に失敗しても受信を続けます。** コールバックの例外は `decode_stream()` からそのまま伝わります。通常の `OSError` は `AzarashiReopenStream` に変換されず、この読み取りループでは捕捉されません。`deliver()` は失敗をログに残して正常に戻るので、`unique` の履歴には通知済みとして記録されます。この例には配信を再試行する処理はありません。

**開き直すのは同じオブジェクトです。** `unique` の重複の記憶はストリームごとなので、同じオブジェクトを `close()` して `open()` すれば、抜き差しをまたいでも既報の警報を通知しなおしません。`serial.Serial()` で作り直すと記憶が消えます。ポートを指定せずにオブジェクトを作っているのはこのためです。

**`timeout=1` は、入力が途絶えたときに停止の合図を確認するためです。** 読み取りがタイムアウトすると外側のループで `stopping` を確認します。ただし、データが流れ続ける間は `decode_stream()` が戻らないことがあります。ロック待ちやコールバックの実行時間も含め、`SIGTERM` を受けてから終了するまでの時間は保証しません。

**待ち時間は刻みます。** `time.sleep(30)` のまま待つと、停止を頼まれてから終わるまでに30秒かかります。`wait()` は1秒ずつ区切って確認します。

**終了コードは supervisor のためです。** データが尽きたときと停止を頼まれたときは 0 を返し、自分でポートを閉じてしまったときは 1 を返します。systemd で `Restart=on-failure` としておけば、再起動と通知の対象は後者だけになります。デバイスの抜き差しはどちらも返しません。プロセスの中で復帰するので、supervisor は関与しません。

**ログにはクラス名を出します。** 送出されるのは葉なので、`[AzarashiDisconnectedError]` のように**何が起きたか**が記録されます。`[AzarashiReopenStream]` のような対処法ではありません。監視で「切断回数」と「自分で閉じた回数」を別に数えられます。
