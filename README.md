[![Downloads](https://static.pepy.tech/personalized-badge/azarashi?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/azarashi)

# Azarashi
A QZSS DCR Decoder.

## Description
azarashi は準天頂衛星みちびきが送信する災危通報メッセージのデコーダーです。U-blox F9P と Sony Spresense が出力するメッセージ形式に対応しています。災危通報(災害・危機管理通報サービス)とは、防災機関から発表される地震や津波発生時の災害情報などの危機管理情報を、準天頂衛星みちびき経由で送信するサービスです。

## Installation
```
$ pip install azarashi
```

## Preparation
### U-blox F9P
設定ツール U-center で、RXM-SFRBX メッセージを出力するように設定してください。下記は RXM-SFRBX メッセージを USB に出力するための参考設定手順です。
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

### Sony Spresense
[QZSS 災危通報 (QZQSM) の NMEA センテンスを出力するように設定してください。](https://developer.sony.com/develop/spresense/docs/arduino_tutorials_ja.html#_qzss_災危通報を出力する)

## CLI
azarashi コマンドの標準入力にメッセージを流してください。

### Hexadecimal
azarashi コマンドに hex オプションを指定してください。
```
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```

### U-blox F9P
stty コマンドでデバイスファイルを raw に設定し、azarashi コマンドに ublox オプションを指定します。USB ではなく UART を使っている場合は、適宜 stty コマンドのオプションを変更してください。
```
$ stty -F /dev/ttyACM0 raw
$ cat /dev/ttyACM0 | azarashi ublox
```

### Sony Spresense
stty コマンドでデバイスファイルをデフォルト設定にし、azarashi コマンドに nmea オプションを指定します。
```
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
azarashi.decode
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
```
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
>>> msg2 = '9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0'
>>> report2 = azarashi.decode(msg2)
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

I/Oストリームを渡してください。デバイスファイルを open して渡すときは、事前に stty コマンドで 'ublox' なら raw モード、'nmea' ならテキストモードに設定してください。

* msg_type

デフォルトは 'hex' 、オプションとして 'ublox' または 'nmea' を指定できます。

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

重複したメッセージを無視したいときは、True を指定してください。

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
GPSアンテナは屋外や窓際に設置する必要があるため、それが実際にデータを処理する装置の近くとは限りません。そこでデータをUDPパケットに載せて再送するスクリプトを書きました。IPv4/IPv6両方に対応しています。簡単な実装なので、ソースを参考に改造するベースにもよいと思います。

### Transmitter
送信側のスクリプトです。デフォルトでは IPv6 リンクローカルマルチキャストアドレスにパケットを送信します。宛先アドレスを指定したい場合は -d オプションを使用してください。IPv4/IPv6両方に対応しています。なお、デバイスファイルの読込権限が必要なため sudo を使っていますが、このとき azarashi モジュールも sudo で実行される python3 環境にインストールされている必要があることに注意してください。
```bash
$ sudo python3 -m azarashi.network.transmitter -t ublox -f /dev/ttyACM0
```
もし Python3 インタプリタを sudo で実行したくない、あるいは sudo で実行される Python3 環境に azarashi をインストールしたくない場合は、次のように実行しても動作は同じです。
```bash
$ sudo cat /dev/ttyACM0 | python3 -m azarashi.network.transmitter -t ublox
```
オプションの下記のとおりです。
```bash
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

## Receiver
受信側のスクリプトです。
```bash
$ python3 -m azarashi.network.receiver
```
オプションの下記のとおりです。
```bash
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
不具合報告、プルリクエスト、コメント等、なんでもよいのでフィードバックお待ちしています。お力添えください。
