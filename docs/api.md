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
`decode()` はレポートオブジェクトを返します。レポートオブジェクトを `str()` に渡すと、災害情報を読みやすい文章にして返します。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
>>> report = azarashi.decode(msg, 'nmea')
>>> str(report)
'防災気象情報(緊急地震速報)(発表)(訓練/試験)\n*** これは訓練です ***\n緊急地震速報\n強い揺れに警戒してください。\n\n発表時刻: 3月10日10時0分\n\n震央地名: 日向灘\n地震発生時刻: 10日10時0分\n深さ: 10km\nマグニチュード: 7.2\n震度(下限): 震度6弱\n震度(上限): 〜程度以上\n島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州'
```
そのため、レポートオブジェクトを `print()` に渡すと災害情報を表示できます。
```python
>>> print(report)
```
```
防災気象情報(緊急地震速報)(発表)(訓練/試験)
*** これは訓練です ***
緊急地震速報
強い揺れに警戒してください。

発表時刻: 3月10日10時0分

震央地名: 日向灘
地震発生時刻: 10日10時0分
深さ: 10km
マグニチュード: 7.2
震度(下限): 震度6弱
震度(上限): 〜程度以上
島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州
```
レポートオブジェクトのパラメータは、`get_params()` メソッドで辞書として取得できます。時刻のパラメータは、すべて UTC のタイムゾーンが付いた `datetime` です。`str()` が返す文章では、時刻を JST に変換して表示します。

時刻として読めない値が届いたときは、その時刻のパラメータは `None` になります。送られてきた日・時・分は、名前の末尾に `_raw` が付いたパラメータに残ります。例えば `occurrence_time_of_earthquake` なら `occurrence_time_of_earthquake_raw` です。ただし発表時刻の `report_time` だけは、読めない値が届くと `None` にならず、`AzarashiInvalidMessageError` が送出されます。
```python
>>> from pprint import pprint
>>> pprint(report.get_params())
```
```python
{'assumptive': False,
 'depth_of_hypocenter': '10km',
 'depth_of_hypocenter_raw': 10,
 'disaster_category': '緊急地震速報',
 'disaster_category_en': 'Earthquake Early Warning',
 'disaster_category_no': 1,
 'eew_forecast_regions': ['島根', '岡山', '広島', '山口', '香川', '愛媛',
                          '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
                          '宮崎', '鹿児島', '中国', '四国', '九州'],
 'eew_forecast_regions_raw': [37, 38, 39, 40, 42, 43,
                              44, 45, 46, 47, 48, 49,
                              50, 51, 66, 67, 68],
 'information_type': '発表',
 'information_type_en': 'Issue',
 'information_type_no': 0,
 'long_period_ground_motion_lower_limit': None,
 'long_period_ground_motion_lower_limit_raw': 0,
 'long_period_ground_motion_upper_limit': None,
 'long_period_ground_motion_upper_limit_raw': 0,
 'magnitude': '7.2',
 'magnitude_raw': 72,
 'message': b'\xc6\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00'
            b'\x03\xdf\xf8\x00\x1c\x00\x00\x11\x85D?\xc0',
 'message_header': '$QZQSM',
 'message_type': 'DCR',
 'nmea': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'notifications_on_disaster_prevention': ['強い揺れに警戒してください。'],
 'notifications_on_disaster_prevention_raw': [201],
 'occurrence_time_of_earthquake': datetime.datetime(2024, 3, 10, 1, 0, tzinfo=datetime.timezone.utc),
 'occurrence_time_of_earthquake_raw': {'day': 10, 'hour': 1, 'minute': 0},
 'preamble': 'C',
 'raw': b'\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00\x03'
        b'\xdf\xf8\x00\x1c\x00\x00\x10',
 'report_classification': '訓練/試験',
 'report_classification_en': 'Training/Test',
 'report_classification_no': 7,
 'report_time': datetime.datetime(2024, 3, 10, 1, 0, tzinfo=datetime.timezone.utc),
 'satellite_id': 55,
 'satellite_prn': 183,
 'satellite_svid': None,
 'seismic_epicenter': '日向灘',
 'seismic_epicenter_raw': 791,
 'seismic_intensity_lower_limit': '震度6弱',
 'seismic_intensity_lower_limit_raw': 8,
 'seismic_intensity_upper_limit': '〜程度以上',
 'seismic_intensity_upper_limit_raw': 11,
 'sentence': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'timestamp': datetime.datetime(2024, 6, 21, 6, 40, 34, 960948, tzinfo=datetime.timezone.utc),
 'version': 1}
```
同じ情報を重複して受信したかどうかは、`==` で比べると判別できます。
```python
>>> msg2 = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'
>>> report2 = azarashi.decode(msg2, 'nmea')
>>> report == report2
```
```
True
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
## AzarashiError
azarashi が定義する例外は、すべてこのクラスを継承しています。

これを捕捉したときは、`decode_stream()` をもう一度呼んでください。読めないメッセージも、扱えないメッセージも、読み終えていないメッセージも、すべてこのクラスの下にあります。どれも次を読めば済みます。ストリームが終わったことを表す `EOFError` だけが、このクラスの外にあります。つまり、このクラスは「続けてよい」、`EOFError` は「やめる」を表します。例は [Minimal Loop](#minimal-loop) にあります。
## AzarashiDecodeError
メッセージをレポートにできなかったことを表すクラスです。次の二つの親にあたります。デコードの失敗をまとめて捕捉したいときは、これを捕捉してください。
## AzarashiInvalidMessageError
デコードに失敗したときに送出される例外クラスです。エラーメッセージに失敗の理由が書かれているので、表示すると原因を調べる手がかりになります。

送出されるのは、メッセージそのものを読めないときです。チェックサムや CRC が合わない、長さが足りない、どのデコーダに渡すか決められない、といった場合です。仕様にないコード値を受け取っただけでは送出しません。そのコード値は `火山(コード番号：999)` のような名前にしてレポートに入れます。仕様が改訂されて新しいコードが増えても、メッセージは読めるままです。
## AzarashiNotImplementedError
`NotImplementedError` を継承した例外クラスです。実験的な配信など、azarashi が対応していないメッセージを受け取ったときに送出されます。そうした配信が始まると頻繁に送出されるので、デバッグのとき以外は捕捉して無視してもよいでしょう。
## AzarashiTimeoutError
`EOFError` を継承した例外クラスです。pySerial などで `timeout` を指定して開いたストリームから、タイムアウトまでにメッセージを読み終えられなかったときに送出されます。読みかけのデータは残っているので、もう一度 `decode_stream()` を呼べば続きから読み込みます。`EOFError` と区別するときは、`EOFError` より先に捕捉してください。

このクラスは `AzarashiDecodeError` を継承していません。デコードに失敗したわけではないからです。プログラムの例は [Timeout](#timeout) にあります。
## 以前の名前
次の名前も使えます。それぞれ右の名前と同じものです。以前から使っているコードは、書き換えなくてもそのまま動きます。

| 以前の名前 | 今の名前 |
| --- | --- |
| `azarashi.qzss_dc_report` | `azarashi.reports` |
| `azarashi.QzssDcReport` | `azarashi.Report` |
| `QzssDcrDecoderException` | `AzarashiInvalidMessageError` |
| `QzssDcrDecoderNotImplementedError` | `AzarashiNotImplementedError` |
| `QzssDcrDecoderTimeoutError` | `AzarashiTimeoutError` |

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
ストリームから読み続けるときの、いちばん短い形です。捕捉するのは2つだけです。`AzarashiError` なら次を読み、`EOFError` なら止めます。
```python
import azarashi
import sys
import serial

with serial.Serial('/dev/ttyS0', 9600) as ser:
    while True:
        try:
            azarashi.decode_stream(ser, 'ublox', print)
        except azarashi.AzarashiError as e:
            print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
        except EOFError:
            break
```
読めないメッセージと、azarashi が扱えないメッセージは、ここで読み飛ばされます。何を飛ばしたかを気にしないなら、`AzarashiError` の節は `pass` だけでも構いません。

`timeout` を付けて開いたストリームでも、この形のまま動きます。タイムアウトも `AzarashiError` の下にあるからです。タイムアウトの合間に別の仕事をしたいときだけ、[Timeout](#timeout) のように節を分けてください。
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
### Timeout
シリアルポートを `timeout` 付きで開くと、`decode_stream()` はメッセージが届かないまま待ち続けることがなくなります。一定の時間で `AzarashiTimeoutError` を送出して戻ってくるので、その合間に別の仕事ができます。終了の合図を見にいく例です。

`AzarashiTimeoutError` は `EOFError` を継承しています。`EOFError` より先に捕捉してください。順番を逆にすると、タイムアウトのたびにストリームの終わりだと判断してしまいます。

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
