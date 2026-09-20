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
- `callback`: レポートを受け取る関数です。`None` のときは、メッセージを一つデコードして、そのレポートを返します。関数を指定したときは、例外が発生するまでデコードを繰り返し、レポートができるたびに関数を呼び出します。関数は次のように呼び出されます。
```python
callback(report, *callback_args, **callback_kwargs)
```
- `callback_args`: 関数に渡す位置引数です。
- `callback_kwargs`: 関数に渡すキーワード引数です。
- `unique`: 重複したメッセージを無視するかどうかです。
  - `False`: 重複を無視しません。デフォルトです。
  - `True`: 同じメッセージは、2回目以降をいつまでも無視します。
  - 秒数: 同じメッセージでも、最後に受信してからその秒数を過ぎていれば、もう一度通知します。例えば、続いている警報が翌日にもう一度配信されたときに通知させたいなら、`unique=3600*24` と指定します。

  重複の記憶はストリームごとです。ストリームを渡しかえると、記憶も切り替わります。デバイスを開き直すときは [AzarashiReopenStream](#azarashireopenstream) を見てください。
- `ignore_dcr`: DCR メッセージを無視するときは `True` を指定します。デフォルトは `False` です。
- `ignore_dcx`: DCX メッセージを無視するかどうかです。デフォルトは `True` で、DCX メッセージを無視します。DCX メッセージも受け取るときは `False` を指定してください。
- `timestamp`: ストリームのデータを受信した時刻です。デフォルトは現在時刻です。[記録しておいたデータ](cli.md#record-and-replay)を読み込むときに、記録した時刻を指定してください。この時刻はすべてのレポートに使われるので、リアルタイムに受信するときは指定しないでください。
### Example
シリアルデバイスを pySerial で開いて読み込み、デコードしたレポートオブジェクトを `print()` に渡します。
```python
>>> import azarashi
>>> import serial
>>> ser = serial.Serial('/dev/ttyS0', 9600)
>>> azarashi.decode_stream(ser, msg_type='ublox', callback=print)
```
## AzarashiException
azarashi が送出する例外は、すべてこのクラスを継承しています。ログにまとめて記録したいときなど、azarashi が止まったことを一箇所で受けたいときに捕捉してください。

このクラスは次に何をすべきかを表しません。それは下の3つが表します。読み取りのループで捕捉するのはそちらです。

| 捕捉するクラス | 何をすべきか |
| --- | --- |
| [AzarashiReadOn](#azarashireadon) | 次のメッセージを読む |
| [AzarashiReopenStream](#azarashireopenstream) | ストリームを開き直す |
| [AzarashiStopReading](#azarashistopreading) | 読み取りをやめる |

この3つは送出されません。送出されるのは、その下にある「何が起きたか」を表すクラスです。ループで捕捉するのは上の3つ、ログに出すのは下のクラス名になります。

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

理由は今後増えることがあります。上の3つを捕捉しておけば、増えても書き換えは要りません。

この3つの下にあるクラスは、何が起きたかを表します。ログに出すのはそちらです。`.message` に理由が入り、`.instance` にはデコーダが入ります。`str()` は電文があればそれも付けます。
## AzarashiReadOn
このメッセージは手に入らず、次のメッセージは手に入る、という意味です。捕捉したら `decode_stream()` をもう一度呼んでください。

読めないメッセージも、扱えないメッセージも、読み終えていないメッセージも、すべてこのクラスの下にあります。どれも次を読めば済みます。ストリームは無事です。

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
pySerial などで `timeout` を指定して開いたストリームから、タイムアウトまでにメッセージを読み終えられなかったときに送出されます。読みかけのデータは残っているので、もう一度 `decode_stream()` を呼べば続きから読み込みます。

**組み込みの例外を一つも継承していません。** `EOFError` ではありません。データが終わったわけではないので、`EOFError` で止めるコードが生きているストリームを打ち切らないためです。`TimeoutError` でもありません。あちらは `OSError` の一種なので、[AzarashiReopenStream](#azarashireopenstream) と同じ網に入り、`except OSError` で開き直すコードが健全なデバイスを開き直してしまいます。

このクラスは `AzarashiDecodeError` を継承していません。デコードに失敗したわけではないからです。プログラムの例は [Timeout](#timeout) にあります。
## AzarashiReopenStream
ストリームを開き直してください、という意味です。読み取りそのものが失敗したときに送出されます。USB のシリアルデバイスを引き抜いたときや、ソケットが切れたときです。

ストリームはもう使えません。読み直しても同じエラーがすぐに返ります。そのまま読み直し続けると、待ち時間のないループになり、CPU を使い切ります。

`AzarashiReadOn` も `EOFError` も継承していません。読み続けてはいけないので前者ではなく、ストリームが終わったわけでもないので後者でもありません。どちらの外にもあるので、**捕捉する順序を気にする必要がありません**。どちらも捕捉していないコードは、この例外をそのまま受け取ります。

デバイスを差し直して読み続けるときは、`close()` して `open()` で**同じオブジェクトを開き直してください**。`unique` の重複の記憶はストリームごとなので、同じオブジェクトなら記憶が残り、既に通知した警報を通知しなおしません。`serial.Serial()` で別のオブジェクトを作ると、記憶は消えて同じ警報をもう一度通知します。プログラムの例は [Reconnect](#reconnect) にあります。

pySerial の `serial.SerialException` も `OSError` の一種です。このクラスも `OSError` を継承しているので、`OSError` を捕捉しているコードはそのまま動きます。`serial.SerialException` を名指しで捕捉しているコードは、このクラスに書き換えてください。

理由は下の2つのクラスが表します。どちらも開き直せば済むので、ループで分ける必要はありません。ログや監視で区別したいときに使ってください。
### AzarashiDisconnectedError
読み取り中にデバイスや相手が消えた、という意味です。USB のシリアルデバイスを引き抜いたとき、ソケットがリセットされたとき、その他ストリームが `OSError` として報告した失敗です。現場で起きる想定内の事象です。
### AzarashiStreamClosedError
読み取り中にストリームが閉じられた、という意味です。閉じた `io` オブジェクトは `OSError` ではなく `ValueError` を送出するので、azarashi がこのクラスに変換しています。

再接続処理が閉じたのなら開き直せば済みます。ただし、**自分のプログラムが閉じたストリームを読み続けている**場合もこれになります。無条件に開き直すループは、そのバグを隠します。
## AzarashiStopReading
読み取りをやめてください、という意味です。取るものがなく、進む道もありません。`EOFError` を継承しているので、`EOFError` で止めているコードはそのまま動きます。

理由は下のクラスが表します。
### AzarashiNoMoreData
データが尽きた、という意味です。ファイルが末尾に達したときや、ソケットを相手側が閉じたときに送出されます。

壊れたものはないので直すものもなく、ただ取るものがありません。デバイスを引き抜いたときは [AzarashiDisconnectedError](#azarashidisconnectederror) です。あちらは開き直せますが、こちらは開き直しても何も来ません。

**尽きたことが重大かどうかは、azarashi からは分かりません。** 記録ファイルを最後まで読んだのなら正常終了で、`azarashi` コマンドは終了コード 0 を返します。生きたフィードが途切れたのなら、その配信は戻りません。このクラスは事実だけを伝えるので、重大さの判断は呼び出し側に残ります。
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
            except EOFError as e:
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
            except EOFError as e:
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

読みかけのデータが残っていても、次のメッセージは壊れません。`ublox` はフレームの先頭を探しなおし、`nmea` と `hex` はチェックサムで弾きます。
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
        except EOFError as e:
            print(f'{e}', file=sys.stderr)
            return 0

exit(example())
```
### Timeout
シリアルポートを `timeout` 付きで開くと、`decode_stream()` はメッセージが届かないまま待ち続けることがなくなります。一定の時間で `AzarashiTimeoutError` を送出して戻ってくるので、その合間に別の仕事ができます。終了の合図を見にいく例です。

`AzarashiTimeoutError` は `EOFError` を継承していないので、捕捉する順序を気にする必要はありません。[AzarashiReadOn](#azarashireadon) の下にあるので、タイムアウトの合間に別の仕事をしないのであれば、そちらでまとめて捕捉しても構いません。

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
                continue  # 1秒のあいだにメッセージを読み終えられなかった。続きを読む
            except azarashi.AzarashiDecodeError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except EOFError as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
```
### Field Receiver
現場に置きっぱなしにする受信機のお手本です。ここまでの例を一つにまとめ、**3つの行動、抜き差しからの復帰、終了、そして自分の失敗を読み取りループに混ぜないこと**を全部入れています。

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
        # 読み取りループに投げ返さない。投げるとデバイスの故障と見分けがつかなくなる
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

**捕捉の順序には規則があります。** 同じ枝の中では葉を先に書いてください。`AzarashiTimeoutError` は `AzarashiReadOn` の下、`AzarashiStreamClosedError` は `AzarashiReopenStream` の下にあるので、先に書かないと親に飲まれます。枝どうし、つまり `AzarashiReadOn` と `AzarashiReopenStream` と `AzarashiStopReading` の3つは互いに継承関係がないので、**どの順番でも構いません**。

**コールバックは自分の失敗を自分で始末します。** これが一番間違えやすい点です。`deliver()` の中で送信に失敗した例外を読み取りループまで投げ返すと、それが `OSError` だったときに「デバイスが消えた」と見分けられなくなります。警報の配信が一度こけただけで、健全な GPS のポートを開き直す受信機になります。

**開き直すのは同じオブジェクトです。** `unique` の重複の記憶はストリームごとなので、同じオブジェクトを `close()` して `open()` すれば、抜き差しをまたいでも既報の警報を通知しなおしません。`serial.Serial()` で作り直すと記憶が消えます。ポートを指定せずにオブジェクトを作っているのはこのためです。

**`timeout=1` は停止のためです。** メッセージを待って止まったままにならないので、1秒ごとに `stopping` を見にいけます。`SIGTERM` を受けてから1秒以内に終了します。

**待ち時間は刻みます。** `time.sleep(30)` だと、停止を頼まれてから30秒待たせます。`wait()` が1秒ずつ確認します。

**終了コードは supervisor のためです。** データが尽きたときと停止を頼まれたときは 0、自分でポートを閉じてしまったときは 1 を返します。systemd なら `Restart=on-failure` で後者だけが再起動と通知の対象になります。デバイスの抜き差しは 0 でも 1 でもなく、プロセスの中で復帰するので supervisor は関与しません。

**ログにはクラス名を出します。** 送出されるのは葉なので、`[AzarashiDisconnectedError]` のように**何が起きたか**が記録されます。`[AzarashiReopenStream]` のような対処法ではありません。監視で「切断回数」と「自分で閉じた回数」を別に数えられます。
