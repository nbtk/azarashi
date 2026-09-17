[![Downloads](https://static.pepy.tech/personalized-badge/azarashi?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/azarashi)

<img src="https://raw.githubusercontent.com/nbtk/azarashi/refs/heads/main/logo.png" width="256">

# Azarashi
A QZSS DCR Decoder.
## Description
azarashi は、準天頂衛星みちびきが送信する災危通報メッセージのデコーダーです。u-blox と Sony Spresense が出力するメッセージ形式に対応しています。災危通報は「災害・危機管理通報サービス」の略です。地震や津波などの災害情報や危機管理情報を、防災機関から受けてみちびき経由で送信するサービスです。
## Installation
```shell
$ pip install azarashi
```
シリアルデバイスの読み込みに使う [pySerial](https://pythonhosted.org/pyserial/) も一緒にインストールされます。
## Preparation
デバイスに災危通報メッセージを出力させるための設定例です。
### u-blox M10S < UART > Raspberry Pi 4 + Ubuntu 22.04 + ubxtool (CLI)
UARTを有効にするため、設定ファイルの末尾に `enable_uart=1` を追記します。
```shell
$ sudo vi /boot/firmware/config.txt
```
```shell
[all]
...

# Enable the UART port
enable_uart=1
```
再起動して、シリアルデバイスが認識されていることを確認します。
```shell
$ sudo reboot
```
`/dev/ttyS0` の状態を確認しましょう。
```shell
$ stat /dev/ttyS0 
```
```shell
  File: /dev/ttyS0
  Size: 0         	Blocks: 0          IO Block: 4096   character special file
Device: 5h/5d	Inode: 602         Links: 1     Device type: 4,40
Access: (0660/crw-rw----)  Uid: (    0/    root)   Gid: (   20/ dialout)
...
```
`/dev/ttyS0` が存在しないときは、dmesg コマンドでシリアルデバイスがどう認識されているかを確認しましょう。デバイスのファイル名が違う、UART を有効にする設定が間違っている、有効化に失敗している、といった原因が考えられます。
```shell
$ sudo dmesg | grep serial
```
```shell
[    0.525432] bcm2835-aux-uart fe215040.serial: there is not valid maps for state default
[    0.527303] fe215040.serial: ttyS0 at MMIO 0xfe215040 (irq = 21, base_baud = 62500000) is a 16550
```
シリアルデバイスに `sudo` コマンドを使わずに読み書きしたいときは、ユーザを `dialout` グループに追加します。
```shell
$ sudo usermod -a -G dialout $USER
$ logout # then re-login to the machine
```
次に、SFRBX メッセージの出力を有効にします。データシートを見て設定コマンドを直接送るか、設定ツールを使ってください。ここでは設定ツール ubxtool を使います。ubxtool は次のようにインストールします。
```shell
$ sudo apt update
$ sudo apt install gpsd gpsd-clients
```
SFRBX メッセージの出力に関連する設定コマンドの例です。
```shell
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,1,1 # sets 'enable'  to ram 
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,0,1 # sets 'disable' to ram 
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,1,2 # sets 'enable'  to bbr (battery-backed ram)
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,0,2 # sets 'disable' to bbr (battery-backed ram)
$ ubxtool -f /dev/ttyS0 -s 9600 -g CFG-MSGOUT-UBX_RXM_SFRBX_UART1 | grep -A3 UBX-CFG-VALGET # gets the state
```
デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。
### u-blox F9P < USB > Windows + u-center (GUI)
設定ツール [u-center](https://www.u-blox.com/en/product/u-center) をダウンロードし、インストールしてください。

u-center で SFRBX メッセージを出力するように設定してください。下記は SFRBX メッセージを USB に出力するための参考設定手順です。
```
Open u-center ->
  View -> Configuration View ->
    CFG (Configuration) -> Revert to default configuration -> Send
    MSG (Messages) -> Messages -> 02-13 RXM-SFRBX ->
      Check the "USB" box and type 1 in the "on" box -> Send
    NMEA (NMEA Protocol) -> NMEA Version -> Select 4.11 -> Send
    CFG (Configuration) -> Save current configuration -> Send
```
u-center で QZSS の L1S シグナル受信機能を有効にしてください。下記は GPS と QZSS のメッセージをすべて受信するための参考設定手順です。
```
Open u-center ->
  View -> Generation 9 Configuration View -> GNSS Configuration ->
    Check All the "GPS" and "QZSS" boxes ->
  　　  Check the "RAM" and "Flash" boxes in the "Write to layer" ->
 　　　　   Send Configuration
```
設定は永続化され、他の機器に接続し直しても災危通報メッセージを出力します。デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。
### Sony Spresense
[QZSS 災危通報 (QZQSM) の NMEA センテンスを出力するように設定してください。](https://developer.sony.com/develop/spresense/docs/arduino_tutorials_ja.html#_qzss_災危通報を出力する)
## CLI
azarashi コマンドをつかうとプログラミングすることなく災危通報メッセージをデコードできます。
```shell
$ echo '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05' | azarashi nmea
```
オプションは下記のとおりです。
```shell
usage: azarashi [-h] [-f INPUT] [-b BAUDRATE] [--record RECORD] [--time TIME]
                [-s] [-u] [-r] [-x] [-v]
                {hex,nmea,ublox}

azarashi CLI

positional arguments:
  {hex,nmea,ublox}      message type

options:
  -h, --help            show this help message and exit
  -f INPUT, --input INPUT
                        input serial device or file (default: stdin)
  -b BAUDRATE, --baudrate BAUDRATE
                        baud rate of the serial device (default: 9600)
  --record RECORD       append the raw input to this file (default: None)
  --time TIME           time the input was received, e.g. 2026-09-01T12:00:00Z
                        (default: None)
  -s, --source          output the source messages (default: False)
  -u, --unique          supress duplicate messages (default: False)
  -r, --ignore-dcr      ignore dcr messages (default: False)
  -x, --ignore-dcx      ignore dcx messages (default: False)
  -v, --verbose         verbose mode (default: False)
```
`-f` には、シリアルデバイスかファイルを指定します。`/dev/ttyS0` や `COM3` のようなシリアルデバイスを指定するときは、ボーレートを `-b` で指定してください。ファイルを指定したときは、その中身をそのまま読み込みます。

CLI は DCR と DCX の両方を表示します。DCR を表示したくないときは `-r` を、DCX を表示したくないときは `-x` を指定してください。API の `decode_stream()` はデフォルトで DCX を無視するので、CLI とは動きが違います。
### u-blox
azarashi コマンドのメッセージタイプに `ublox` を指定します。デバイスファイルのパスとボーレートは適宜変更してください。
```shell
$ azarashi ublox -f /dev/ttyS0 -b 9600
```
デバイスファイルの読込権限が足りないときは、sudo を使わずに前述のとおりユーザを `dialout` グループに追加してください。
### Sony Spresense
azarashi コマンドのメッセージタイプに `nmea` を指定します。ボーレートは、スケッチで設定した値に合わせてください。
```shell
$ azarashi nmea -f /dev/ttyUSB0 -b 115200
```
### Hexadecimal
azarashi コマンドのメッセージタイプに `hex` を指定します。`hex` は、ヘッダとチェックサムを含まない、16進数の文字列だけのメッセージ形式です。
```shell
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```
### Record and Replay
`--record` を指定すると、デコードしながら、受信したデータをそのままファイルに追記します。記録したファイルを `-f` で指定するか標準入力に流すと、同じ受信を再現できます。
```shell
$ azarashi ublox -f /dev/ttyS0 --record qzss.ubx
$ azarashi ublox -f qzss.ubx
```
メッセージは日付をすべて持っているわけではありません。DCR には年がなく、DCX には曜日と時刻しかありません。足りない部分は受信時刻から補います。記録してすぐに再生するなら、そのままで正しい日付になります。前の週や前の年に記録したファイルを再生するときは、記録した時刻を `--time` で指定してください。表示する時刻も、指定した時刻になります。
```shell
$ azarashi ublox -f qzss.ubx --time 2026-09-01T12:00:00Z
```
## API
### decode()
```python
azarashi.decode(msg, msg_type='nmea', timestamp=None)
```
- `msg`: デコードするメッセージです。
- `msg_type`: メッセージの形式です。`nmea`、`hex`、`ublox` のどれかを指定します。デフォルトは `nmea` です。`nmea` と `hex` のメッセージは str 型で、`ublox` のメッセージは bytes 型で渡してください。
- `timestamp`: メッセージを受信した時刻です。デフォルトは現在時刻です。メッセージにない年や日付は、この時刻から補います。記録しておいたメッセージをあとからデコードするときに指定してください。タイムゾーンのない datetime は、実行環境のローカル時刻として扱います。
#### Example
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

時刻として読めない値が届いたときは、その時刻のパラメータは `None` になります。送られてきた日・時・分は、名前の末尾に `_raw` が付いたパラメータに残ります。例えば `occurrence_time_of_earthquake` なら `occurrence_time_of_earthquake_raw` です。ただし発表時刻の `report_time` だけは、読めない値が届くと `None` にならず、`QzssDcrDecoderException` が送出されます。
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
### decode_stream()
```python
azarashi.decode_stream(stream, msg_type='nmea', callback=None, callback_args=(), callback_kwargs=None, unique=False, ignore_dcr=False, ignore_dcx=True, timestamp=None)
```
- `stream`: メッセージを読み込むストリームです。シリアルデバイスは pySerial で開いて渡してください。ファイルは `open(path, 'rb')` のように、バイナリモードで開くことをおすすめします。
- `msg_type`: メッセージの形式です。`nmea`、`hex`、`ublox` のどれかを指定します。デフォルトは `nmea` です。
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
- `timestamp`: ストリームのデータを受信した時刻です。デフォルトは現在時刻です。記録しておいたデータを読み込むときに、記録した時刻を指定してください。この時刻はすべてのレポートに使われるので、リアルタイムに受信するときは指定しないでください。
#### Example
シリアルデバイスを pySerial で開いて読み込み、デコードしたレポートオブジェクトを `print()` に渡します。
```python
>>> import azarashi
>>> import serial
>>> ser = serial.Serial('/dev/ttyS0', 9600)
>>> azarashi.decode_stream(ser, msg_type='ublox', callback=print)
```
### QzssDcrDecoderException
デコードに失敗したときに送出される例外クラスです。エラーメッセージに失敗の理由が書かれているので、表示すると原因を調べる手がかりになります。
### QzssDcrDecoderNotImplementedError
`NotImplementedError` を継承した例外クラスです。実験的な配信など、azarashi が対応していないメッセージを受け取ったときに送出されます。そうした配信が始まると頻繁に送出されるので、デバッグのとき以外は捕捉して無視してもよいでしょう。
### QzssDcrDecoderTimeoutError
`EOFError` を継承した例外クラスです。pySerial などで `timeout` を指定して開いたストリームから、タイムアウトまでにメッセージを読み終えられなかったときに送出されます。読みかけのデータは残っているので、もう一度 `decode_stream()` を呼べば続きから読み込みます。`EOFError` と区別するときは、`EOFError` より先に捕捉してください。
```python
with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
    while not stopped:
        try:
            azarashi.decode_stream(ser, 'ublox', handler)
        except azarashi.QzssDcrDecoderTimeoutError:
            continue  # no complete message within a second: check `stopped` and keep reading
```
### Type Hints
azarashi は型ヒント付きで配布しています。mypy や pyright を使うと、関数の引数と戻り値や、レポートのフィールドの型を検査できます。

`decode()` と `decode_stream()` が返すレポートの型は `azarashi.QzssDcReport` です。これは次の二つのどちらかです。

- JMA-DC Report のレポート: `QzssDcReportJmaBase` とそのサブクラス
- DCX のレポート: `QzssDcXtendedMessageBase` とそのサブクラス

災害の種類ごとのフィールドを参照するときは、先に `isinstance()` でレポートのクラスを確かめてください。
```python
import azarashi
from azarashi import qzss_dc_report


def handler(report: azarashi.QzssDcReport) -> None:
    if isinstance(report, qzss_dc_report.QzssDcReportJmaTsunami):
        for arrival in report.expected_tsunami_arrival_times:  # datetime | None
            print(arrival)
    elif isinstance(report, qzss_dc_report.QzssDcXtendedMessageBase):
        print(report.a6a7_hazard_onset_datetime)  # datetime | None
```
DCX のレポートには、メッセージの種類や内容によって設定されないフィールドがあります。例えば `a12_ellipse_centre_latitude` は、楕円の情報を持たないメッセージでは設定されません。設定されていないフィールドを参照すると `AttributeError` になります。型ヒントには宣言してあるので、型検査では気づけません。そうしたフィールドは `getattr()` や `get_params()` で確かめてから使ってください。
## Examples
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
            except azarashi.QzssDcrDecoderException as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.QzssDcrDecoderNotImplementedError as e:
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
[pySerial](https://pythonhosted.org/pyserial/) でシリアルポートを開いて `decode_stream()` に渡す例です。
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
            except azarashi.QzssDcrDecoderException as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.QzssDcrDecoderNotImplementedError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except EOFError as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
```
## Network
GPS アンテナは屋外や窓際に置く必要があるので、データを処理する装置の近くに置けるとは限りません。そこで、受信したデータを UDP パケットで別の装置に送るスクリプトを用意しました。IPv4 と IPv6 の両方に対応しています。簡単な実装なので、改造して使うときのベースにもしやすいと思います。
### Transmitter
送信側のスクリプトです。DCR と DCX の両方のメッセージを送信します。デフォルトの宛先は IPv6 のリンクローカルマルチキャストアドレスです。宛先を変えるときは `-d` で指定してください。`-f`、`-b`、`--record` の使い方は azarashi CLI と同じです。
```shell
$ python3 -m azarashi.network.transmitter -t ublox -f /dev/ttyS0 -b 9600
```
オプションは下記のとおりです。
```
usage: transmitter.py [-h] [-d DST_HOST] [-p DST_PORT] [-t {hex,nmea,ublox}]
                      [-f INPUT] [-b BAUDRATE] [--record RECORD] [-u]

azarashi network transmitter

options:
  -h, --help            show this help message and exit
  -d DST_HOST, --dst-host DST_HOST
                        destination host (default: ff02::1)
  -p DST_PORT, --dst-port DST_PORT
                        destination port (default: 2112)
  -t {hex,nmea,ublox}, --msg-type {hex,nmea,ublox}
                        message type (default: nmea)
  -f INPUT, --input INPUT
                        input serial device or file (default: stdin)
  -b BAUDRATE, --baudrate BAUDRATE
                        baud rate of the serial device (default: 9600)
  --record RECORD       append the raw input to this file (default: None)
  -u, --unique          supress duplicate messages (default: False)
```
### Receiver
受信側のスクリプトです。DCR と DCX の両方を表示します。DCR を表示したくないときは `-r` を、DCX を表示したくないときは `-x` を指定してください。受信するインタフェースは `-i` で指定できます。ただし `-i` は Linux の `SO_BINDTODEVICE` を使うので、Linux でしか使えません。
```shell
$ python3 -m azarashi.network.receiver
```
オプションは下記のとおりです。
```
usage: receiver.py [-h] [-b BIND_ADDR] [-p BIND_PORT] [-i BIND_IFACE] [-r]
                   [-x] [-v]

azarashi network receiver

options:
  -h, --help            show this help message and exit
  -b BIND_ADDR, --bind-addr BIND_ADDR
                        address to bind (default: ::)
  -p BIND_PORT, --bind-port BIND_PORT
                        port to bind (default: 2112)
  -i BIND_IFACE, --bind-iface BIND_IFACE
                        iface to bind (default: any)
  -r, --ignore-dcr      ignore dcr messages (default: False)
  -x, --ignore-dcx      ignore dcx messages (default: False)
  -v, --verbose         verbose mode (default: False)
```
プログラムから `Receiver.start()` を呼ぶときは、`decode_stream()` と同じく、DCX を無視するのがデフォルトです。DCX も受け取るときは `ignore_dcx=False` を指定してください。

受信したパケットをデコードできないとき、receiver コマンドと `Receiver.start()` は警告をログに出力し、そのパケットを読み飛ばして受信を続けます。

## DCX
azarashi は DCX メッセージのデコードをサポートしています。下記は L-Alert をデコードする例です。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E' # l-alert
>>> report = azarashi.decode(msg, 'nmea')
>>> print(report)
```
```
### DCX Message - L-Alert ###
A1 - Message type: Alert
A2 - Country/region name: Japan
A3 - Provider identifier: Foundation for MultiMedia Communications
A4 - Hazard category and type: MET - Rainfall
A4 - Hazard definition: Rainfall greater than or equal to 50 mm in past 24 hours. Note: Precise threshold is according to each local standard.
A5 - Severity: Severe - Significant threat to life or property
A6A7 - Hazard onset: 2024-06-23T13:00:00Z
A8 - Hazard duration: 6H <= Duration < 12H
A11 - Instruction: Keep away from Water area.
A11 - Instruction (ja): 離れろ。水場。
A12 - Ellipse centre latitude: 35.688258
A13 - Ellipse centre longitude: 139.690855
A14 - Ellipse semi - major axis: 10.933
A15 - Ellipse semi - minor axis: 5.979
A16 - Ellipse azimuth: 45.0
A17 - Type of specific settings: B1 - Improved Resolution of Main Ellipse
C1 - Refined latitude of centre of main ellipse: 35.688258
C2 - Refined longitude of centre of main ellipse: 139.690855
C3 - Refined length of semi major axis: 10.933
C4 - Refined length of semi minor axis: 5.979
```
レポートオブジェクトからパラメータを取得するには `get_params()` メソッドを使います。
```python
>>> from pprint import pprint
>>> pprint(report.get_params(), sort_dicts=False)
```
```python
{'sentence': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'raw': b'M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc\x00\x00\x00'
        b'\x00\x00\x00\x00\x10',
 'timestamp': datetime.datetime(2024, 6, 21, 6, 9, 5, 433111, tzinfo=datetime.timezone.utc),
 'message': b'S\xb0`M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc'
            b'\x00\x00\x00\x00\x00\x00\x00\x10"\xa8\x18\x80',
 'nmea': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'message_header': '$QZQSM',
 'satellite_id': 55,
 'satellite_prn': 183,
 'satellite_svid': None,
 'preamble': 'A',
 'message_type': 'DCX',
 'camf': <azarashi.qzss_dcr_lib.report.qzss_dc_report.QzssDcxCamf object at 0x10aeb3d10>,
 'ignore_a12_to_a16': False,
 'ignore_a17_to_a18': False,
 'ignore_ex1': True,
 'ignore_ex2_to_ex7': True,
 'ignore_ex8_to_ex9': True,
 'satellite_designation_mask_type': 'MT44 is for Japan or for use outside '
                                    'Japan',
 'satellite_designation_mask': ['For Japan',
                                'For Japan',
                                'For use outside Japan',
                                'For use outside Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan'],
 'dcx_message_type': 'L-Alert',
 'a1_message_type': 'Alert',
 'a2_country_region_name': 'Japan',
 'a3_provider_identifier': 'Foundation for MultiMedia Communications',
 'a4_hazard_category': 'MET',
 'a4_hazard_type': 'Rainfall',
 'a4_hazard_definition': 'Rainfall greater than or equal to 50 mm in past 24 '
                         'hours. Note: Precise threshold is according to each '
                         'local standard.',
 'a5_severity': 'Severe - Significant threat to life or property',
 'a6_hazard_onset_week': 'Current',
 'a7_hazard_onset_time_of_week': 'SUNDAY - 01:00 PM',
 'a6a7_hazard_onset_datetime': datetime.datetime(2024, 6, 23, 13, 0, tzinfo=datetime.timezone.utc),
 'a8_hazard_duration': '6H <= Duration < 12H',
 'a9_type_of_library': 'Country/region library',
 'a10_library_version': '#1',
 'a11_japanese_library': 'Keep away from Water area.',
 'a11_japanese_library_ja': '離れろ。水場。',
 'a12_ellipse_centre_latitude': 35.688258,
 'a13_ellipse_centre_longitude': 139.690855,
 'a14_ellipse_semi_major_axis': 10.933,
 'a15_ellipse_semi_minor_axis': 5.979,
 'a16_ellipse_azimuth': 45.0,
 'a17_type_of_specific_settings': 'B1 - Improved Resolution of Main Ellipse',
 'c1_refined_latitude_of_centre_of_main_ellipse': 35.688258,
 'c2_refined_longitude_of_centre_of_main_ellipse': 139.690855,
 'c3_refined_length_of_semi_major_axis': 10.933,
 'c4_refined_length_of_semi_minor_axis': 5.979,
 'dcx_version': 1}
```
デコードする前のビットフィールドの値は、`report.camf` に入っています。
```python
print(report.camf.get_params())
```
```python
{'sdmt': 0, 'sdm': 96, 'a1': 1, 'a2': 111, 'a3': 1, 'a4': 74, 'a5': 2, 'a6': 0, 'a7': 9421, 'a8': 2, 'a9': 1, 'a10': 0, 'a11': 773, 'a12': 45761, 'a13': 116395, 'a14': 13, 'a15': 11, 'a16': 48, 'a17': 0, 'a18': 0, 'ex1': 13104, 'ex2': 0, 'ex3': 0, 'ex4': 0, 'ex5': 0, 'ex6': 0, 'ex7': 0, 'ex8': 0, 'ex9': 7376896189632872448, 'ex10': 0, 'vn': 1, 'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0}
```
### DCX Message Types
DCX メッセージのデコード結果が格納されるレポートオブジェクトは下記のとおりです。
#### Null Message 
CAMF フィールドが空のメッセージです。SD フィールドを監視するために使用します。不要なら無視してください。
```python
class QzssDcxNullMsg(QzssDcXtendedMessageBase)
```
#### Information from Organizations outside Japan
日本国外の機関から発報されたメッセージです。
```python
class QzssDcxOutsideJapan(QzssDcXtendedMessageBase)
```
#### L-Alert
```python
class QzssDcxLAlert(QzssDcXtendedMessageBase)
```
#### J-Alert
```python
class QzssDcxJAlert(QzssDcXtendedMessageBase)
```
#### Information from Local Government
```python
class QzssDcxMTInfo(QzssDcXtendedMessageBase)
```
#### Unknown Message
日本から発報されたメッセージのうち、発信機関が L-Alert、J-Alert、自治体のどれでもないものです。azarashi は正確にデコードできない可能性が高いので、デバッグのとき以外は無視してください。
```python
class QzssDcxUnknown(QzssDcXtendedMessageBase)
```
## Note
IS-QZSS-DCR-017、IS-QZSS-DCX-004 をサポートしています。
## Tips
### 災危通報が出力されない / UnicodeDecodeError
GPS モジュールと接続するインタフェースのボーレートが一致していないと、壊れたビット列を受け取るため災危通報を検出できません。azarashi CLI は壊れた行を読み飛ばして動作を続けるので、エラーが出ないまま何も出力されないことがあります。ボーレートは例えば次のような値です。
```
9600, 19200, 38400, 57600, 115200
```
azarashi CLI では `-b` オプションで指定します。GPS モジュール側の設定方法はモジュールのマニュアルを参照してください。

`decode_stream()` にテキストモードで開いたストリームを渡していると、壊れたビット列を読んだときに、ストリーム自体が次の例外を送出することがあります。ストリームを `'rb'` のバイナリモードで開けば、壊れた行は読み飛ばされます。
```
[UnicodeDecodeError] 'utf-8' codec can't decode byte 0xNN in position XX: ~
```
### Encountered EOF
azarashi CLI は、読み込んでいるストリームの書き込み側が閉じられると、stderr に Encountered EOF と出力して終了します。これはエラーではなく、正常な終了です。
### DCX Satellite Designation Field
DCX メッセージの SD フィールドを監視するときは、`decode_stream()` の `unique` を指定しないでください。`unique` は、CAMF フィールドが同じ DCX メッセージを重複とみなし、SD フィールドの違いを見ません。そのため、SD フィールドだけが変わったメッセージを取りこぼし、SD フィールドの変化を監視できません。
## Development
リポジトリを取得して開発用のツールをインストールすると、テストと静的解析を実行できます。GitHub Actions でも push と pull request のたびに同じチェックを実行しています。
```shell
$ pip install -e . pytest pytest-cov ruff mypy 'pyright[nodejs]' types-pyserial
$ python -m pytest tests        # Python 3.11 から 3.14 で実行しています
$ python -m pytest --cov tests  # カバレッジも測るとき。設定: pyproject.toml の [tool.coverage]
$ ruff check azarashi/          # 規則: pyproject.toml の [tool.ruff]
$ mypy --strict azarashi/       # 型検査
$ pyright                       # 設定: pyproject.toml の [tool.pyright]
```
GitHub Actions の typing ジョブは、ビルドした wheel をインストールして、利用者と同じ立場で型検査をします。確かめている内容は次のとおりです。

- `tests/typing/consumer.py` の正しい使い方が、エラーなく通ること
- `tests/typing/consumer_mistakes.py` の誤った使い方が、エラーとして検出されること
- `tests/typing/generate_mistakes.py` が作る誤用が、すべて検出されること。誤用は、公開している関数とメソッドのすべての引数と戻り値について作ります

また `tests/test_declared_types.py` は、実際にデコードしたレポートの値が、宣言した型に合っていることを確かめます。

`tests/golden/` には、`tests/*.log` のサンプルログにある全メッセージのデコード結果を保存してあります。保存しているのは、`str()` の文章と全フィールドの値です。出力が変わるとテストが失敗します。意図して出力を変えたときは、`python tests/test_golden.py` で再生成し、差分を確認してからコミットしてください。

テスト用のメッセージは、`tests/qzqsm.py` を使ってフィールドの値から組み立てられます。CRC とチェックサムも自動で計算します。
```python
from qzqsm import jma, sfrbx
sentence = jma(11, [(53, 4, 2), (57, 40, 830303020300)])  # 洪水: 鬼怒川の氾濫警戒情報
frame = sfrbx(sentence)  # 同じメッセージの UBX-RXM-SFRBX
```
## Feedback
イシュー報告、プルリクエスト、コメント等、なんでもよいのでフィードバックお待ちしています。星をもらうと開発が活発になります。
Questions, suggestions, and comments are welcome! Please feel free to write in English.

## Credits
This project was originally developed during my time at BitMeister Inc., with support and resources generously provided by the company. I am really thankful for the people and the environment that helped make it happen. It is now maintained independently.
