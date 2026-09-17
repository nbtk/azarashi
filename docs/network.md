[azarashi](../README.md) / Network

# Network
GPS アンテナは屋外や窓際に置く必要があるので、データを処理する装置の近くに置けるとは限りません。そこで、受信したデータを UDP パケットで別の装置に送るスクリプトを用意しました。IPv4 と IPv6 の両方に対応しています。簡単な実装なので、改造して使うときのベースにもしやすいと思います。
## Transmitter
送信側のスクリプトです。DCR と DCX の両方のメッセージを送信します。デフォルトの宛先は IPv6 のリンクローカルマルチキャストアドレスです。宛先を変えるときは `-d` で指定してください。`-f`、`-b`、`--record` の使い方は [azarashi CLI](cli.md) と同じです。
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
## Receiver
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
プログラムから `Receiver.start()` を呼ぶときは、[`decode_stream()`](api.md#decode_stream) と同じく、DCX を無視するのがデフォルトです。DCX も受け取るときは `ignore_dcx=False` を指定してください。

受信したパケットをデコードできないとき、receiver コマンドと `Receiver.start()` は警告をログに出力し、そのパケットを読み飛ばして受信を続けます。
