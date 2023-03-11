[![Downloads](https://static.pepy.tech/personalized-badge/azarashi?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/azarashi)

# Azarashi
A QZSS DCR Decoder.

## Description
azarashi は準天頂衛星みちびきが送信する災危通報メッセージのデコーダーです。U-blox と Sony Spresense が出力するメッセージ形式に対応しています。災危通報(災害・危機管理通報サービス)とは、防災機関から発表される地震や津波発生時の災害情報などの危機管理情報を、準天頂衛星みちびき経由で送信するサービスです。

## Installation
```shell
$ pip install azarashi
```

## Preparation
デバイスに災危通報メッセージを出力させるための設定例です。
### Ubuntu 22.04
シリアルデバイスに sudo コマンドを使わずに読み書きしたいときは、ユーザを `dialout` グループに追加します。
```shell
$ sudo usermod -a -G dialout $USER
$ logout # then re-login to the machine
```
### U-blox M10S < UART > Raspberry Pi 4 + Ubuntu 22.04 + ubxtool (CLI)
UARTを有効にするため、設定ファイルの末尾に `enable_uart=1` を追記します。
```shell
$ sudo vi /boot/firmware/config.txt
[all]
...

# Enable the UART port
enable_uart=1
```
再起動して、シリアルデバイスが認識されていることを確認します。
```shell
$ sudo reboot
```
```shell
$ sudo stty -F /dev/ttyS0
speed 9600 baud; line = 0;
-brkint -imaxbel
```
もし `/dev/ttyS0` がない場合は、 dmsg コマンドで確認しましょう。
```shell
$ sudo dmesg | grep serial
[    0.525432] bcm2835-aux-uart fe215040.serial: there is not valid maps for state default
[    0.527303] fe215040.serial: ttyS0 at MMIO 0xfe215040 (irq = 21, base_baud = 62500000) is a 16550
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
設定コマンドを実行すると tty の設定が変更されるので、stty コマンドでデバイスファイルを raw に設定し直してください。
```shell
$ stty -F /dev/ttyS0 raw
```
デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。

### U-blox F9P < USB > Windows + U-center (GUI)
設定ツール U-center で、 SFRBX メッセージを出力するように設定してください。下記は SFRBX メッセージを USB に出力するための参考設定手順です。
```
Open U-center ->
  View -> Configuration View ->
    CFG (Configuration) -> Revert to default configuration -> Send
    MSG (Messages) -> Messages -> 02-13 RXM-SFRBX ->
      Check the "USB" box and type 1 in the "on" box -> Send
    NMEA (NMEA Protocol) -> NMEA Version -> Select 4.11 -> Send
    CFG (Configuration) -> Save current configuration -> Send
```
設定ツール U-center で、QZSS の L1S シグナル受信機能を有効にしてください。下記は GPS と QZSS のメッセージをすべて受信するための参考設定手順です。
```
Open U-center ->
  View -> Generation 9 Configuration View -> GNSS Configuration ->
    Check All the "GPS" and "QZSS" boxes ->
  　　  Check the "RAM" and "Flash" boxes in the "Write to layer" ->
 　　　　   Send Configuration
```
設定は永続化され、他の機器に接続し直しても災危通報メッセージを出力します。デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。

### Sony Spresense
[QZSS 災危通報 (QZQSM) の NMEA センテンスを出力するように設定してください。](https://developer.sony.com/develop/spresense/docs/arduino_tutorials_ja.html#_qzss_災危通報を出力する)

## CLI
azarashi コマンドの標準入力にメッセージを流してください。

### Hexadecimal
azarashi コマンドに hex オプションを指定してください。
```shell
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```

### U-blox
stty コマンドでデバイスファイルを raw に設定し、azarashi コマンドに ublox オプションを指定します。USB ではなく UART を使っている場合は、適宜 stty コマンドのオプションを変更してください。
#### M10S via UART
```shell
$ stty -F /dev/ttyS0 raw # via UART
$ cat /dev/ttyS0 | azarashi ublox
```
#### F9P via USB
```shell
$ stty -F /dev/ttyACM0 raw # via USB
$ cat /dev/ttyACM0 | azarashi ublox
```

### Sony Spresense
stty コマンドでデバイスファイルをデフォルト設定にし、azarashi コマンドに nmea オプションを指定します。
```shell
$ stty -F /dev/ttyUSB0
$ cat /dev/ttyUSB0 | azarashi nmea
```

### --unique Option
重複したメッセージを表示しません。

### --source Option
デコード前のメッセージを表示します。

## API
### decode()

```python
azarashi.decode(msg, msg_type='hex')
```

* msg

メッセージを渡してください。メッセージは bytes 型または str 型です。

* msg_type

デフォルトは 'hex' 、オプションとして 'ublox' または 'nmea' を指定できます。'ublox' を指定したときメッセージは bytes 型、'nmea' を指定したときメッセージは str 型です。

#### Example
デコードして得られたレポートオブジェクトを print() にわたすと、ヒューマンリーダブルな災害情報を返します。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
>>> report = azarashi.decode(msg, 'nmea')
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
レポートオブジェクトからパラメータを取得するには、get_params() メソッドを使います。
```python
>>> from pprint import pprint
>>> pprint(report.get_params())
```
```python
{'assumptive': False,
 'depth_of_hypocenter': '10km',
 'disaster_category': '緊急地震速報',
 'disaster_category_en': 'Earthquake Early Warning',
 'disaster_category_no': 1,
 'eew_forecast_regions': ['島根', '岡山', '広島', '山口', '香川', '愛媛',
                          '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
                          '宮崎', '鹿児島', '中国', '四国', '九州'],
 'information_type': '発表',
 'information_type_en': 'Issue',
 'information_type_no': 0,
 'magnitude': '7.2',
 'message': b'\xc6\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00'
            b'\x03\xdf\xf8\x00\x1c\x00\x00\x11\x85D?\xc0',
 'message_header': '$QZQSM',
 'message_type': 'DC Report (JMA)',
 'nmea': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'notifications_on_disaster_prevention': ['強い揺れに警戒してください。'],
 'occurrence_time_of_eathquake': datetime.datetime(2022, 3, 10, 1, 0),
 'preamble': 'C',
 'raw': b'\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00\x03'
        b'\xdf\xf8\x00\x1c\x00\x00\x10',
 'report_classification': '訓練/試験',
 'report_classification_en': 'Training/Test',
 'report_classification_no': 7,
 'report_time': datetime.datetime(2022, 3, 10, 1, 0),
 'satellite_id': 55,
 'satellite_prn_code': 183,
 'seismic_epicenter': '日向灘',
 'seismic_intensity_lower_limit': '震度6弱',
 'seismic_intensity_upper_limit': '〜程度以上',
 'sentence': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'timestamp': datetime.datetime(2022, 4, 8, 15, 8, 52, 930551)}
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
azarashi.decode_stream(stream, msg_type='hex', callback=None, callback_args=(), callback_kwargs={}, unique=False)
```

* stream

I/Oストリームを渡してください。デバイスファイルを open して渡すときは、事前に stty コマンドで `ublox` なら raw モード、`nmea` ならテキストモードに設定してください。

* msg_type

デフォルトは `hex` 、オプションとして `ublox` または `nmea` を指定できます。

* callback

メッセージをデコードしたあとに実行されるコールバック関数です。None の場合、decode_stream() はメッセージをデコードするたびに結果を返します。コールバック関数が与えられた場合、decode_stream() は例外が発生しない限り繰り返しメッセージをデコードし、そのたびにコールバック関数に結果を渡して実行します。下記はコールバック関数のインタフェースです。
```python
callback(report, *callback_args, **callback_kwargs)
```

* calback_args

コールバック関数に渡される引数です。

* callback_kwargs

コールバック関数に渡されるキーワード引数です。

* unique

重複したメッセージを無視したいときは、`True` を指定してください。

#### Example
指定したデバイスファイルを読み込み、デコードしたレポートオブジェクトを print() に渡します。スクリプトを実行する前に、stty コマンドでデバイスファイルの設定をしておく必要があります。U-blox のGNSSモジュールでは、stty コマンドに raw オプションを指定して動作することを確認しています。
```python
import azarashi
import sys

with open('/dev/ttyACM0', mode='r') as f:
    while True:
        try:
            azarashi.decode_stream(f,
                                   msg_type='ublox',
                                   callback=print)
        except azarashi.QzssDcrDecoderException as e:
            print(f'# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except NotImplementedError as e:
            print(f'# [{type(e).__name__}] {e}\n', file=sys.stderr)
```

## Network
GPS アンテナは屋外や窓際に設置する必要があるため、それが実際にデータを処理する装置の近くとは限りません。そこでデータを UDP パケットに載せて再送するスクリプトを書きました。 IPv4/IPv6 両方に対応しています。簡単な実装なので、ソースを参考に改造するベースにもよいと思います。

### Transmitter
送信側のスクリプトです。デフォルトでは IPv6 リンクローカルマルチキャストアドレスにパケットを送信します。宛先アドレスを指定したい場合は -d オプションを使用してください。
```shell
$ python3 -m azarashi.network.transmitter -t ublox -f /dev/ttyACM0
```
なお、デバイスファイルの読込権限が足りず sudo コマンドを使って python3 インタプリタを実行するとき azarashi モジュールも sudo で実行される python3 環境にインストールされている必要があることに注意してください。あるいは次のように実行しても動作は同じです。
```shell
$ sudo cat /dev/ttyACM0 | python3 -m azarashi.network.transmitter -t ublox
```
オプションの下記のとおりです。
```shell
usage: transmitter.py [-h] [-d DST_HOST] [-p DST_PORT] [-t {ublox,nmea,hex}] [-f INPUT] [-u]

azarashi network transmitter

options:
  -h, --help            show this help message and exit
  -d DST_HOST, --dst-host DST_HOST
                        destination host (default: ff02::1)
  -p DST_PORT, --dst-port DST_PORT
                        destination port (default: 2112)
  -t {ublox,nmea,hex}, --msg-type {ublox,nmea,hex}
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
オプションの下記のとおりです。
```shell
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
IS-QZSS-DCR-010をサポートしています。

## Feedback
イシュー報告、プルリクエスト、コメント等、なんでもよいのでフィードバックお待ちしています。お力添えください。
