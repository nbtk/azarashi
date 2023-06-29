[![Downloads](https://static.pepy.tech/personalized-badge/azarashi?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/azarashi)
# Azarashi
A QZSS DCR Decoder.
## Description
azarashi は準天頂衛星みちびきが送信する災危通報メッセージのデコーダーです。u-blox と Sony Spresense が出力するメッセージ形式に対応しています。災危通報(災害・危機管理通報サービス)とは、防災機関から発表される地震や津波発生時の災害情報などの危機管理情報を準天頂衛星みちびき経由で送信するサービスです。
## Installation
```shell
$ pip install azarashi
```
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
もし `/dev/ttyS0` が存在しない場合は dmsg コマンドで確認しましょう。ファイル名が異なるか UART ポートを有効化する設定が間違っているか、有効化に失敗していることが考えられます。
```shell
$ sudo dmesg | grep serial
```
```shell
[    0.525432] bcm2835-aux-uart fe215040.serial: there is not valid maps for state default
[    0.527303] fe215040.serial: ttyS0 at MMIO 0xfe215040 (irq = 21, base_baud = 62500000) is a 16550
```
シリアルデバイスに sudo コマンドを使わずに読み書きしたいときは、ユーザを `dialout` グループに追加します。
```shell
$ sudo usermod -a -G dialout $USER
$ logout # then re-login to the machine
```
データシートを参照して直接インストラクションを流し込むか、設定ツールをつかって SFRBX メッセージの出力を有効にしてください。設定ツール ubxtool は下記のようにインストールします。
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
usage: azarashi [-h] [-f INPUT] [-s] [-u] [-v] {hex,nmea,ublox}

azarashi CLI

positional arguments:
  {hex,nmea,ublox}      message type

options:
  -h, --help            show this help message and exit
  -f INPUT, --input INPUT
                        input device (default: stdin)
  -s, --source          output the source messages (default: False)
  -u, --unique          supress duplicate messages (default: False)
  -v, --verbose         verbose mode (default: False)
```
### u-blox
stty コマンドでデバイスファイルを `raw` に設定し azarashi コマンドのメッセージタイプに `ublox` を指定します。デバイスファイルのパスは適宜変更してください。
```shell
$ stty -F /dev/ttyS0 raw
```
azarashi コマンドに ublox オプションを指定します。
```shell
$ azarashi ublox -f /dev/ttyS0
```
なお、デバイスファイルの読込権限が足りず sudo コマンドを使って python3 インタプリタを実行するとき azarashi モジュールも sudo で実行される python3 環境にインストールされている必要があることに注意してください。あるいは次のように実行しても動作は同じです。
```shell
$ sudo cat /dev/ttyS0 | azarashi ublox
```
### Sony Spresense
azarashi コマンドに nmea オプションを指定します。
```shell
$ azarashi nmea -f /dev/ttyUSB0
```
### Hexadecimal
azarashi コマンドのメッセージタイプに `hex` を指定してください。`hex` はヘッダ、チェックサムを含まない16進数文字列のメッセージ形式です。
```shell
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```
## API
### decode()
```python
azarashi.decode(msg, msg_type='nmea')
```
- `msg`: メッセージを渡してください。メッセージは str 型または bytes 型です。
- `msg_type`: デフォルトは `nmea` 、オプションとして `hex` または `ublox` を指定できます。`nmea` または `hex` を指定したときメッセージは str 型、`ublox` を指定したときメッセージは bytes 型です。
#### Example
デコードして得られたレポートオブジェクトを `str()` にわたすとヒューマンリーダブルな災害情報を返します。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
>>> report = azarashi.decode(msg, 'nmea')
>>> str(report)
'防災気象情報(緊急地震速報)(発表)(訓練/試験)\n*** これは訓練です ***\n緊急地震速報\n強い揺れに警戒してください。\n\n発表時刻: 3月10日10時0分\n\n震央地名: 日向灘\n地震発生時刻: 10日10時0分\n深さ: 10km\nマグニチュード: 7.2\n震度(下限): 震度6弱\n震度(上限): 〜程度以上\n島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州'
```
つまりレポートオブジェクトを `print()` にわたせば災害情報を出力します。
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
レポートオブジェクトからパラメータを取得するには `get_params()` メソッドを使います。
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
 'magnitude': '7.2',
 'magnitude_raw': 72,
 'message': b'\xc6\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00'
            b'\x03\xdf\xf8\x00\x1c\x00\x00\x11\x85D?\xc0',
 'message_header': '$QZQSM',
 'message_type': 'DC Report (JMA)',
 'nmea': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'notifications_on_disaster_prevention': ['強い揺れに警戒してください。'],
 'notifications_on_disaster_prevention_raw': [201],
 'occurrence_time_of_earthquake': datetime.datetime(2023, 3, 10, 1, 0),
 'preamble': 'C',
 'raw': b'\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00\x03'
        b'\xdf\xf8\x00\x1c\x00\x00\x10',
 'report_classification': '訓練/試験',
 'report_classification_en': 'Training/Test',
 'report_classification_no': 7,
 'report_time': datetime.datetime(2023, 3, 10, 1, 0),
 'satellite_id': 55,
 'satellite_prn': 183,
 'seismic_epicenter': '日向灘',
 'seismic_epicenter_raw': 791,
 'seismic_intensity_lower_limit': '震度6弱',
 'seismic_intensity_lower_limit_raw': 8,
 'seismic_intensity_upper_limit': '〜程度以上',
 'seismic_intensity_upper_limit_raw': 11,
 'sentence': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'timestamp': datetime.datetime(2023, 6, 29, 9, 22, 2, 203772),
 'version': 1}
```
重複して受信した同一情報のメッセージかどうかは等価演算子で判別できます。
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
azarashi.decode_stream(stream, msg_type='nmea', callback=None, callback_args=(), callback_kwargs={}, unique=False)
```
- `stream`: I/Oストリームを渡してください。デバイスファイルを `open()` して渡すときは、事前に stty コマンドで `ublox` なら `raw` モード、`nmea` ならデフォルト設定にしてください。pySerial つかうときは stty コマンドによる設定は不要です。
- `msg_type`: デフォルトは `nmea` 、オプションとして `hex` または `ublox` を指定できます。
- `callback`: メッセージをデコードしたあとに実行されるコールバック関数です。`None` の場合 `decode_stream()` はメッセージをデコードするたびに結果を返します。コールバック関数が与えられた場合 `decode_stream()` は例外が発生しない限り繰り返しメッセージをデコードし、そのたびにコールバック関数に結果を渡して実行します。下記はコールバック関数のインタフェースです。
```python
callback(report, *callback_args, **callback_kwargs)
```
- `calback_args`: コールバック関数に渡される引数です。
- `callback_kwargs`: コールバック関数に渡されるキーワード引数です。
- `unique`: 重複したメッセージを無視したいときは `True` を指定してください。
#### Example
指定したデバイスファイルを読み込み、デコードしたレポートオブジェクトを `print()` に渡します。
```python
>>> import azarashi
>>> f = open('/dev/ttyS0', mode='r')
>>> azarashi.decode_stream(f, msg_type='ublox', callback=print)
```
### QzssDcrDecoderException
この例外クラスは何らかの理由でデコードに失敗したときに送出されます。エラーメッセージを表示すると問題解決の一助となるでしょう。
### QzssDcrDecoderNotImplementedError
`NotImplementedError` を継承した例外クラスです。実験的な配信など、デコーダが対応していないメッセージを受け取ったときに送出されます。配信がはじまると騒々しいのでデバッグ以外ではこの例外を握りつぶしたほうがよいかもしれません。
## Examples
### I/O Stream
例外処理を加えた簡単なプログラムの例です。
```python
import azarashi
import sys

def example():
    with open('/dev/ttyS0', mode='r') as f:
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
[pySerial](https://pythonhosted.org/pyserial/) でシリアルポートを `open()` して `decode_stream()` に渡すこともできます。この方法では stty コマンドによる設定は不要です。
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
GPS アンテナは屋外や窓際に設置する必要があるため、それが実際にデータを処理する装置の近くとは限りません。そこでデータを UDP パケットに載せて再送するスクリプトを書きました。IPv4/IPv6 両方に対応しています。簡単な実装なので、ソースを参考に改造するベースにもよいと思います。
### Transmitter
送信側のスクリプトです。デフォルトでは IPv6 リンクローカルマルチキャストアドレスにパケットを送信します。宛先アドレスを指定したい場合は -d オプションを使用してください。
```shell
$ python3 -m azarashi.network.transmitter -t ublox -f /dev/ttyS0
```
なお、デバイスファイルの読込権限が足りず sudo コマンドを使って python3 インタプリタを実行するとき azarashi モジュールも sudo で実行される python3 環境にインストールされている必要があることに注意してください。あるいは次のように実行しても動作は同じです。
```shell
$ sudo cat /dev/ttyS0 | python3 -m azarashi.network.transmitter -t ublox
```
オプションは下記のとおりです。
```
usage: transmitter.py [-h] [-d DST_HOST] [-p DST_PORT] [-t {hex,nmea,ublox}] [-f INPUT] [-u]

azarashi network transmitter

options:
  -h, --help            show this help message and exit
  -d DST_HOST, --dst-host DST_HOST
                        destination host (default: ff02::1)
  -p DST_PORT, --dst-port DST_PORT
                        destination port (default: 2112)
  -t {hex,nmea,ublox}, --msg-type {hex,nmea,ublox}
                        message type (default: ublox)
  -f INPUT, --input INPUT
                        input device (default: stdin)
  -u, --unique          supress duplicate messages (default: False)
```
### Receiver
受信側のスクリプトです。
```shell
$ python3 -m azarashi.network.receiver
```
オプションは下記のとおりです。
```
usage: receiver.py [-h] [-b BIND_ADDR] [-p BIND_PORT] [-i BIND_IFACE] [-v]

azarashi network receiver

optional arguments:
  -h, --help            show this help message and exit
  -b BIND_ADDR, --bind-addr BIND_ADDR
                        address to bind (default: ::)
  -p BIND_PORT, --bind-port BIND_PORT
                        port to bind (default: 2112)
  -i BIND_IFACE, --bind-iface BIND_IFACE
                        iface to bind (default: any)
  -v, --verbose         verbose mode (default: False)
```
## Note
IS-QZSS-DCR-010 をサポートしています。
## Tips
### UnicodeDecodeError
```
[UnicodeDecodeError] 'utf-8' codec can't decode byte 0xNN in position XX: ~
```
GPSモジュールと接続するインタフェースのボーレートが一致せず、壊れたビット列をデコードしようとして失敗していることが考えられます。ボーレートは例えば次のような値です。
```
9600, 19200, 38400, 57600, 115200
```
設定方法はGPSモジュール、sttyまたはpySerialのマニュアルを参照してください。
### Encountered EOF
CLI でストリームを受けていた azarashi は、書き込み側がクローズすると Encountered EOF と stderr に出力して終了します。これは正常な動作です。その直前までエラーなく動作していたと解釈してください。
## Feedback
イシュー報告、プルリクエスト、コメント等、なんでもよいのでフィードバックお待ちしています。星をもらうと開発が活発になります。
