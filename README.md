# azarashi

## QZSS DCR Decoder
azarashi は準天頂衛星みちびきがブロードキャストする災害・危機管理通報メッセージのデコーダーです。U-blox F9P、Sony Spresense が出力するメッセージ形式に対応しています。

## Installation
git レポジトリをクローンしてから、pip コマンドでインストールしてください。環境によって pip コマンドは pip3 コマンドかもしれません。
```
$ git clone https://github.com/nbtk/azarashi.git
$ pip install ./azarashi
```

## Preparation
### U-blox F9P
設定ツール U-center で、RXM-SFRBXメッセージを出力するように設定してください。下記は RXM-SFRBX メッセージをUSBに出力するための参考設定手順です。
```
Open U-center ->
  View -> Configuration View ->
    CFG (Configuration) -> Revert to default configuration -> Send
    MSG (Messages) -> Messages -> 02-13 RXM-SFRBX -> Check USB on (1) -> Send
    NMEA (NMEA Protocol) -> NMEA Version -> Select 4.11 -> Send
    CFG (Configuration) -> Save current configuration -> Send
```
設定ツール U-center で、QZSS の L1S チャネルのメッセージ受信機能を有効にしてください。下記は GPS と QZSS のメッセージの受信を有効にするための参考設定手順です。
```
Open U-center ->
  View -> Generation 9 Configuration View -> GNSS Configuration ->
    Check All the GPS and QZSS boxes ->
  　　  Check the RAM and Flash boxes in the "Write to layer" ->
 　　　　   Send Configuration
```

### Sony Spresense
QZSS 災危通報 (QZQSM) の NMEA センテンスを出力するように設定してください。
https://developer.sony.com/develop/spresense/docs/arduino_tutorials_ja.html#_qzss_災危通報を出力する

## コマンド
### U-blox F9P
stty コマンドで raw モードに設定し、azarashi コマンドには ublox オプションを指定します。
```
$ stty -F /dev/ttyACM0 raw
$ cat /dev/ttyACM0 | azarashi ublox
```

### Sony Spresense
stty コマンドでテキストモードに設定し、azarashi コマンドには spresense オプションを指定します。
```
$ stty /dev/ttyUSB0
$ cat /dev/ttyUSB0 | azarashi spresense
```

## API
### decode()
```python
azarashi.decode(msg, msg_type='hex')
```
#### msg
メッセージ。bytes 型または str 型。
#### msg_type
デフォルトは 'hex' 、オプションとして 'u-blox' または 'spresense' 。'u-blox' を指定したとき、メッセージは bytes 型。'spresense' を指定したとき、メッセージは str 型。

#### Example
```python
>>> import azarashi
>>> msg = '53AF898400000194DA6FEDFB000302D5A001400000000000010040100E143EC'
>>> report = azarashi.decode(msg)
>>> print(report)
```
```
防災気象情報(緊急地震速報)(発表)(訓練/試験)
*** これは訓練です ***
緊急地震速報
今後若干の海面変動があるかもしれません。
津波と満潮が重なると、津波はより高くなりますので一層厳重な警戒が必要です。
場所によっては、観測した津波の高さよりさらに大きな津波が到達しているおそれがあります。

発表時刻: 3月1日9時0分

震央地名: 北海道地方
地震発生時刻: 1日8時59分
深さ: 0km
マグニチュード: 0.3
震度(下限): 震度4
震度(上限): 震度5弱
北海道道央、埼玉、東京、沖縄、その他の府県予報区および地方予報区_緊急地震速報(警報)
```

### decode_stream()
```python
decode_stream(stream, msg_type='hex', callback=None, callback_args=(), callback_kwargs={})
```

#### stream
I/Oストリーム。

#### msg_type
デフォルトは 'hex' 、オプションとして 'u-blox' または 'spresense' 。

#### callback
None の場合、メッセージをデコードするたびに結果を返します。関数が与えられた場合、例外が発生しない限りメッセージをデコードしてコールバック関数の実行を繰り返します。
```python
callback(report, *callback_args, **callback_kwargs)
```

#### calback_args
コールバック関数に渡される引数。

#### callback_kwargs
コールバック関数に渡されるキーワード引数。

#### Example
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

## Note
災害種別「南海トラフ地震」は未対応です。
