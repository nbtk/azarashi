[azarashi](../README.md) / API

# API
azarashi をプログラムから使うための関数と例外です。コマンドの使い方は [CLI](cli.md) を見てください。
## decode()
```python
azarashi.decode(msg, msg_type='nmea', timestamp=None)
```
- `msg`: デコードするメッセージです。
- `msg_type`: 入力の形式です。`nmea`、`hex`、`ublox` のどれかを指定します。デフォルトは `nmea` です。`nmea` と `hex` のメッセージは str 型でも bytes 型でも渡せます。pySerial の `readline()` が返すバイト列は、そのまま渡してください。`ublox` のメッセージは bytes 型です。
  - `spresense` は `nmea` の別名です。
  - `net` は、[receiver](network.md#receiver) が受け取る33バイトのデータグラム形式です。先頭の1バイトが衛星 ID で、残りがメッセージ本体です。
  - `l1s` は `decode()` では使えません。L1S アーカイブの衛星の PRN はファイルの先頭にしかないので、`decode_stream()` で読んでください。
- `timestamp`: メッセージを受信した時刻です。デフォルトは現在時刻です。メッセージにない年や日付は、この時刻から補います。[記録しておいたメッセージ](cli.md#record-and-replay)をあとからデコードするときに指定してください。タイムゾーンのない datetime は、実行環境のローカル時刻として扱います。

`decode()` がレポートを返すのは、災危通報のメッセージだけです。L1S の Message Type 43 の DCR と、44 の DCX です。測位を補強するメッセージなど、それ以外の L1S メッセージを渡すと、[AzarashiInvalidMessageError](#azarashiinvalidmessageerror) を送出します。u-blox のフレームでは、QZSS の L1S 信号でないフレームも同じです。受信機が出すフレームをすべて読むときは、`decode_stream()` を使ってください。災危通報でないフレームを読み飛ばします。
### Example
`decode()` はレポートを返します。返るクラスとフィールド、デコードした例は [Reports](reports.md) を見てください。
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
- `msg_type`: 入力の形式です。`nmea`、`hex`、`ublox`、`l1s` のどれかを指定します。デフォルトは `nmea` です。`spresense` は `nmea` の別名です。
  `ublox` は、QZSS の L1S 信号の災危通報だけを読みます。ほかのフレームは読み飛ばします。
  `l1s` は、拡張子が `.l1s` の L1S アーカイブです。受信時刻は記録ごとの GPS 時刻から決まるので、`timestamp` は指定できません。災危通報でない記録は読み飛ばします。
  `nmea` と `hex` は、災危通報でないメッセージに AzarashiInvalidMessageError を送出します。
  `net` はストリームでは使えません。データグラムごとに `decode(data, 'net')` を呼んでください。
- `callback`: レポートを受け取る関数です。`None` のときは、メッセージを一つデコードして、そのレポートを返します。関数を指定したときは、例外が発生するまでデコードを繰り返し、レポートができるたびに関数を呼び出します。関数は次のように呼び出されます。
```python
callback(report, *callback_args, **callback_kwargs)
```
- `callback_args`: 関数に渡す位置引数です。
- `callback_kwargs`: 関数に渡すキーワード引数です。
- `unique`: `==` で等しいレポートを重複とみなし、無視するかどうかです。
  - `False`: 重複を無視しません。デフォルトです。
  - `True`: 記憶している同じメッセージは、2回目以降を無視します。時間が経っても記憶は失効しません。
  - 秒数: 同じメッセージでも、最後に受信してからその秒数を過ぎていれば、もう一度通知します。通知済みとして記憶しているメッセージは、抑制したときも受信時刻を更新します。例えば `unique=60` では、30秒おきに届く同じメッセージを定期的に通知することはありません。最後の受信から60秒を超えて間が空いたときに通知します。

  どちらも記憶するのは直近256件です。容量を超えて記憶から外れたメッセージは、再び通知します。

  重複の記憶はストリームのオブジェクトごとです。別のオブジェクトなら、`==` で等しくても記憶は独立しています。デバイスを開き直すときは [AzarashiReopenStream](#azarashireopenstream) を見てください。

  コールバックが正常に戻った後に、そのメッセージを通知済みとして記憶します。コールバックが失敗すると例外をそのまま呼び出し元へ伝え、後から届く同じメッセージを再び通知します。コールバックを指定しない場合は、レポートを返す前に記憶します。
- `ignore_dcr`: DCR メッセージを無視するときは `True` を指定します。デフォルトは `False` です。
- `ignore_dcx`: DCX メッセージを無視するかどうかです。デフォルトは `True` で、DCX メッセージを無視します。DCX メッセージも受け取るときは `False` を指定してください。
- `timestamp`: ストリームのデータを受信した時刻です。デフォルトは現在時刻です。[記録しておいたデータ](cli.md#record-and-replay)を読み込むときに、記録した時刻を指定してください。この時刻はすべてのレポートに使われるので、リアルタイムに受信するときは指定しないでください。

秒数での重複判定は、レポートの `timestamp` で経過を測ります。`timestamp` を指定して読むと時刻が進まないので、秒数を指定しても同じメッセージを再び通知しません。

引数が間違っているときは、[AzarashiFixTheCall](#azarashifixthecall) の下の例外を送出します。
### Example
シリアルデバイスを pySerial で開いて読み込み、デコードしたレポートを `print()` に渡します。
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

azarashi が保持している読みかけのデータと、まだ通知していないメッセージを破棄します。重複の記憶は残します。戻り値は `None` です。
[AzarashiReopenStream](#azarashireopenstream) を受けずに、自分の判断で同じストリームを開き直すときに使います。AzarashiReopenStream のときは、ストリームが壊れた時点で読みかけのデータを捨てています。

`stream` と `msg_type` は `decode_stream()` と同じ選び方で読み取り元を指定します。
その読み取り元に保存された行の途中のデータ・抽出済み NMEA センテンス・UBX バッファ・L1S アーカイブの読みかけの記録を、形式や読み取りメソッドにかかわらず破棄します。
L1S アーカイブから読んだ衛星の PRN と GPS 時刻も破棄します。次の読み取りは、アーカイブの先頭の PRN から読みます。
`.buffer` を共有するラッパーでは、他のラッパーから読める未配信データにも影響します。
読み取り元が異なるストリームや、各ラッパーの重複履歴には影響しません。

**同じ読み取り元を使う読み取りとコールバックがすべて終わってから呼んでください。**
開き直す前のストリームを指定してリセットし、そのあと `close()` と `open()` をして読み取りを再開してください。
通常の受信タイムアウトではリセットせず、次の読み取りで続きを受信してください。

読み取りメソッドや `.buffer` を差し替える場合は、差し替え前にリセットしてください。差し替え先にも以前の読み取り状態が残っている場合は、そちらもリセットします。
形式やストリームのメソッドが合わないときは、何も破棄する前に、`decode_stream()` と同じ例外を送出します。

`decode_stream()` とリセットのロック待機時間は、下位ストリームの読み取りタイムアウトに
含まれません。共有元の別の read がブロックしていれば、その timeout 設定を超えて待つ場合があります。

## JSON Output

レポートの `to_json_dict()` は JSON 用の辞書、`to_ndjson()` は改行付きの1件分の文字列を返します。
`json_schema()` は配布スキーマの辞書を、`json_code_tables()` は JSON が参照するコード表の辞書を返します。
詳しくは [JSON Output](json.md) を参照してください。

## AzarashiException
azarashi が送出する例外は、すべてこのクラスを継承しています。azarashi が報告する失敗を一箇所で受けたいとき、たとえばまとめてログに記録するときに捕捉してください。

このクラス自身は、次に何をすべきかを表しません。それを表すのは次の4つです。読み取りのループで捕捉するのは、はじめの3つです。4つ目は読み取りでは直らないので、捕捉せずに外へ出します。

| 捕捉するクラス | 何をすべきか |
| --- | --- |
| [AzarashiReadOn](#azarashireadon) | 次のメッセージを読む |
| [AzarashiReopenStream](#azarashireopenstream) | ストリームを開き直す |
| [AzarashiStopReading](#azarashistopreading) | 読み取りをやめる |
| [AzarashiFixTheCall](#azarashifixthecall) | 呼び出しを直す。ループでは捕捉しない |

この4つ自体は送出されません。送出されるのは、4つをそれぞれ継承した、何が起きたかを表すクラスです。ログに出るのは継承した側の名前です。

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
├── AzarashiStopReading             読み取りをやめる
│   └── AzarashiNoMoreData
└── AzarashiFixTheCall              呼び出しを直す
    ├── AzarashiUnsupportedFormatError
    └── AzarashiArgumentTypeError
```

何が起きたかを表すクラスは、仕様の改訂や対応形式の追加で増えることがあります。4つのほうを捕捉しておけば、増えても書き換えは要りません。

失敗の理由は `.message` に入り、`.instance` には失敗したデコーダーが入る場合があります。読み取り障害やタイムアウトなど、デコーダーを伴わない例外では `None` です。`str()` は、受け取ったメッセージがあればそれも付けます。
## AzarashiReadOn
メッセージが手に入らなかったことを表すクラスです。読めないメッセージ、azarashi が扱えないメッセージ、読み終えていないメッセージが、すべてこのクラスの下にあります。

ストリームは無事です。捕捉したら `decode_stream()` をもう一度呼んでください。読めないメッセージはそのまま失われますが、次のメッセージから読み込みが続きます。読み終えていないメッセージは、次の呼び出しで続きから読み込みます。

例は [Minimal Loop](#minimal-loop) にあります。
## AzarashiDecodeError
メッセージをレポートにできなかったことを表すクラスです。次の二つの親にあたります。デコードの失敗をまとめて捕捉したいときは、これを捕捉してください。

`ValueError` を継承しているので、`except ValueError` でも捕捉できます。
## AzarashiInvalidMessageError
メッセージそのものを読めないときに送出されます。チェックサムや CRC が合わない、長さが足りない、中身が空、災危通報のメッセージでない、どのデコーダーに渡すか決められない、といった場合です。空のメッセージを渡したときも、ストリームが終わったわけではないのでこのクラスになります。仕様にないコード値を受け取っただけでは送出しません。そのコード値は `火山(コード番号：999)` のような名前にしてレポートに入れます。
## AzarashiNotImplementedError
実験的な配信など、azarashi が対応していないメッセージを受け取ったときに送出されます。そうした配信が始まると頻繁に送出されるので、デバッグのとき以外は捕捉して無視してもよいでしょう。

**`NotImplementedError` は継承していません。** `except NotImplementedError` や `except RuntimeError` では捕まりません。
## AzarashiTimeoutError
pySerial などで `timeout` を指定して開いたストリームの読み取りが、データを返さずに終わったときや、行の途中までを返したときに送出されます。読みかけのデータは残っているので、もう一度 `decode_stream()` を呼べば続きから読み込みます。

**ソケットを読むときは、`socket.makefile()` に `settimeout()` を組み合わせないでください。** 一度タイムアウトすると、そのファイルオブジェクトは二度と読めなくなります。azarashi はこれを [AzarashiReopenStream](#azarashireopenstream) として報告します。

タイムアウト付きでソケットを読むときは、pySerial の `socket://` を使ってください。こちらは読めた分を渡してくれるので、続きから読み込めます。
```python
port = serial.serial_for_url('socket://192.168.1.10:2000', timeout=1)
azarashi.decode_stream(port, 'ublox', print)
```

**`TimeoutError`・`OSError`・`EOFError` は継承しません。** `except OSError` で再接続するコードは、タイムアウトでは開き直しません。

`except AzarashiDecodeError` でも捕まりません。プログラムの例は [Timeout](#timeout) にあります。
## AzarashiReopenStream
ストリームの読み取りそのものが失敗したことを表すクラスです。USB のシリアルデバイスを引き抜いたときや、TCP の接続が切れたときに送出されます。

そのストリームはもう使えません。読み直しても同じエラーがすぐに返るので、読み直し続けると待ち時間のないループになり、CPU を使い切ります。閉じて開き直してください。

`AzarashiReadOn` も `EOFError` も継承していません。

pySerial のデバイスを差し直して読み続けるときは、`close()` して `open()` で**同じオブジェクトを開き直してください**。`unique` の重複の記憶はストリームごとなので、同じオブジェクトなら記憶が残り、記憶している警報を通知しなおしません。`serial.Serial()` で別のオブジェクトを作ると、新しい記憶で読み始めるため同じ警報をもう一度通知します。プログラムの例は [Reconnect](#reconnect) にあります。

記憶が残るのは、弱参照できるストリームだけです。pySerial のストリームは弱参照できます。自作のストリームで `__slots__` を使うときは、基底クラスが弱参照に対応していなければ `__weakref__` も含めてください。

pySerial の `serial.SerialException` も `OSError` の一種です。このクラスも `OSError` を継承しているので、`OSError` を捕捉しているコードはそのまま動きます。`serial.SerialException` を名指しで捕捉しているコードは、このクラスに書き換えてください。

何が起きたかは、これを継承した次の2つが表します。どちらも開き直せば済むので、ループで分ける必要はありません。ログや監視で区別したいときに使ってください。
### AzarashiDisconnectedError
読み取り中にデバイスや相手が消えたときに送出されます。USB のシリアルデバイスの引き抜き、TCP 接続のリセット、そのほかストリームが `OSError` として報告した失敗です。
### AzarashiStreamClosedError
読み取り中にストリームが閉じられたときに送出されます。

再接続処理が閉じたのなら、開き直せば済みます。ただし、**自分のプログラムが閉じたストリームを読み続けている**ときもこれになります。無条件に開き直すループは、そのバグを隠します。
## AzarashiStopReading
データが尽きたことを表すクラスです。読むものがなく、開き直す先もありません。`EOFError` を継承しているので、`EOFError` で止めているコードはそのまま動きます。

何が起きたかは、これを継承した次のクラスが表します。
### AzarashiNoMoreData
ファイルが末尾に達したときや、TCP の接続を相手側が閉じたときに送出されます。

デバイスを引き抜いたときは、これではなく [AzarashiDisconnectedError](#azarashidisconnectederror) です。

**尽きたことが重大かどうかは、azarashi からは分かりません。** 記録ファイルを最後まで読んだのなら正常終了で、`azarashi` コマンドは終了コード 0 を返します。生きたフィードが途切れたのなら、その配信は戻りません。
## AzarashiFixTheCall
呼び出し方が間違っていることを表すクラスです。読み直しても、開き直しても直りません。呼び出しているコードを直してください。

何も読まないうちに確かめるので、ストリームに届いていたメッセージは失われず、正しく呼び直せばそのまま読めます。ただ1つ、ストリームが文字列とバイト列のどちらを返すかだけは、最初の1回を読んで確かめます。

届いたメッセージの中身の誤りは、これに入りません。空のメッセージや壊れたメッセージは [AzarashiInvalidMessageError](#azarashiinvalidmessageerror) で、次を読めば先へ進めます。

`AzarashiReadOn`、`AzarashiReopenStream`、`AzarashiStopReading` のどれも継承していません。そのため、この3つを捕捉する読み取りのループを通り抜け、理由を示してプログラムを止めます。

何が起きたかは、これを継承した次のクラスが表します。
### AzarashiUnsupportedFormatError
`msg_type` に、azarashi が読まない形式を渡したときに送出されます。`decode()` が読むのは nmea・spresense・hex・ublox・net の5つです。`decode_stream()` と `reset_reading_state()` は、net を除く4つに l1s を加えた5つを読みます。

`decode_stream()` で l1s に `timestamp` を渡したときにも送出されます。

`ValueError` を継承しています。
### AzarashiArgumentTypeError
引数が、その呼び出しに必要な種類のものでないときに送出されます。

- `decode()` の `msg` が、文字列でもバイト列でもない
- `timestamp` が `datetime` でない
- `stream` に、その形式を読むメソッドがない。nmea・spresense・hex は `readline()`、ublox と l1s は `read1()` か `read()` を使います
- `stream` が、その形式では読めないものを返す。ublox と l1s は文字列を読めないので、ファイルはバイナリモードで開いてください
- `callback` が呼び出せない。`callback_args` が並びでない。`callback_kwargs` が名前と値の対応でない
- `unique` が、真偽値でも数値でもない

`TypeError` を継承しています。

## Earlier Names
次の名前も使えます。それぞれ右の名前と同じものです。

| 以前の名前 | 今の名前 |
| --- | --- |
| `QzssDcrDecoderException` | `AzarashiInvalidMessageError` |
| `QzssDcrDecoderNotImplementedError` | `AzarashiNotImplementedError` |

レポートのクラスも短くなりました。所属するモジュールで修飾して書きます。

| 以前の名前 | 今の名前 |
| --- | --- |
| `QzssDcReportJmaTsunami` | `reports.dcr.Tsunami` |
| `QzssDcxJAlert` | `reports.dcx.JAlert` |
| `QzssDcReportBase` | `reports.base.Base` |

以前のクラス名は、以前と同じ `azarashi.qzss_dc_report.QzssDcxJAlert` でも、`azarashi.QzssDcxJAlert` でも使えます。
`azarashi.qzss_dc_report` からは、今のモジュールの `base`・`dcr`・`dcx` も使えます。

`reports.dcr` が MT43、`reports.dcx` が MT44、両方に共通するものが `reports.base` です。全クラスの一覧は [Reports](reports.md) にあります。

ログやエラー出力に出るクラス名は、今の名前に変わります。以前の名前で出力を検索しているときは、書き換えてください。

呼び出し方の誤りだけは、以前の名前では捕捉できなくなりました。以前は `QzssDcrDecoderException` として報告していましたが、今は [AzarashiFixTheCall](#azarashifixthecall) です。
## Type Hints
azarashi は型ヒント付きで配布しています。mypy や pyright を使うと、関数の引数と戻り値や、レポートのフィールドの型を検査できます。

`decode()` と `decode_stream()` が返すレポートの型は `azarashi.Report` です。これは次の二つのどちらかです。クラスとフィールドの一覧は [Reports](reports.md) にあります。

- DCR のレポート: `dcr.Base` とそのサブクラス
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
DCX のレポートには、メッセージの種類や内容によって設定されないフィールドがあります。例えば `a12_ellipse_centre_latitude` は、楕円の情報を持たないメッセージでは `None` になります。型は `float | None` です。A1 から A10 までと `dcx_version` は必ず設定されます。このうち `None` になることがあるのは `a6a7_hazard_onset_datetime` だけです。

警報を持たない `dcx.NullMsg` は、これらのフィールドを一つも持ちません。そのため警報のフィールドを読むときは `dcx.AlertBase` で絞ってください。`dcx.Base` で絞ると `dcx.NullMsg` も通ってしまいます。
## Examples
### Minimal Loop
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
        except azarashi.AzarashiStopReading:
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

開き直すのは**同じオブジェクト**です。理由は [AzarashiReopenStream](#azarashireopenstream) にあります。

読みかけのデータは、ストリームが壊れた時点で捨てられます。差し直したあとの最初のメッセージに、消えたデバイスのバイト列は混ざりません。
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

`timeout` は下位ストリームの個々の読み取りに適用され、`decode_stream()` 全体の実行時間を制限しません。データが流れ続ける場合は、通知しないメッセージや重複も含めて読み続けるため、タイムアウトせず、終了の合図を確認できないことがあります。

`AzarashiTimeoutError` は [AzarashiReadOn](#azarashireadon) の下にあります。タイムアウトの合間に別の仕事をしないのであれば、この節をやめて `AzarashiReadOn` にまとめても構いません。両方書くときは、`AzarashiTimeoutError` を先に書いてください。

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
現場に置きっぱなしにする受信機のお手本です。3つの行動、抜き差しからの復帰、終了の伝え方、そして**自分の失敗を読み取りループに混ぜないこと**を入れました。

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

def stop(signum, frame):
    """読み取りや待ち時間の途中でも抜ける。ポートは main() の finally が閉じる"""
    sys.exit(0)

def deliver(report):
    """警報を渡す。ここでの失敗はこのプログラムのものなので、ここで始末する"""
    try:
        print(report, flush=True)
    except Exception:
        # 配信の失敗をログに残し、受信を続ける
        logger.exception('could not hand on the %s alert', report.message_type)

def read(port):
    """読めるものがなくなるまで読む。終了コードか、開き直しを求める None を返す"""
    while True:
        try:
            azarashi.decode_stream(port, 'ublox', deliver, unique=3600 * 24, ignore_dcx=False)
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

def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    # ポートを指定せずに作る。1つのオブジェクトを開いて閉じて開き直すため
    port = serial.Serial(baudrate=9600)
    port.port = PORT

    attempt = 0
    while True:
        try:
            port.open()
        except OSError as e:
            seconds = BACKOFF[min(attempt, len(BACKOFF) - 1)]
            logger.warning('[%s] %s: %d秒後に開き直す', type(e).__name__, e, seconds)
            attempt += 1
            time.sleep(seconds)
            continue
        logger.info('reading %s', port.port)
        attempt = 0
        try:
            code = read(port)
        finally:
            port.close()
        if code is not None:
            return code

if __name__ == '__main__':
    sys.exit(main())
```

このコードが守っていることを、上から順に挙げます。

**捕捉の順序には規則があります。** 同じ枝の中では葉を先に書いてください。`AzarashiStreamClosedError` は `AzarashiReopenStream` の下にあるので、先に書かないと、親の節が先に捕まえてしまいます。枝どうしの3つは、[Minimal Loop](#minimal-loop) のとおりどの順番でも構いません。

**この例では、配信に失敗しても受信を続けます。** コールバックの例外は `decode_stream()` からそのまま伝わります。通常の `OSError` は `AzarashiReopenStream` に変換されず、この読み取りループでは捕捉されません。`deliver()` は失敗をログに残して正常に戻るので、失敗した警報も `unique` の記憶には通知済みとして残ります。

**開き直すのは同じオブジェクトです。** ポートを指定せずにオブジェクトを作り、それを開いて閉じて開き直します。

**停止の合図を受けたら、その場で抜けます。** `stop()` が `SystemExit` を送出するので、読み取りの途中でも、開き直すまでの待ち時間の途中でも終わります。ポートは `main()` の `finally` が閉じます。`deliver()` が捕まえるのは `Exception` なので、`SystemExit` は通り抜けます。

**終了コードは supervisor のためです。** データが尽きたときと停止を頼まれたときは 0 を返し、自分でポートを閉じてしまったときは 1 を返します。systemd で `Restart=on-failure` としておけば、再起動と通知の対象は後者だけになります。デバイスの抜き差しからはプロセスの中で復帰するので、終了しません。

**ログにはクラス名を出します。** 送出されるのは葉なので、`[AzarashiDisconnectedError]` のように**何が起きたか**が記録されます。監視で「切断回数」と「自分で閉じた回数」を別に数えられます。
