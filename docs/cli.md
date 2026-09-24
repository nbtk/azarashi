[azarashi](../README.md) / CLI

# CLI
azarashi コマンドを使うと、プログラムを書かずに災危通報メッセージをデコードできます。
```shell
$ echo '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05' | azarashi nmea
```
オプションは下記のとおりです。
```shell
usage: azarashi [-h] [-f INPUT] [-b BAUDRATE] [--record RECORD] [--time TIME]
                [-s] [-u] [-r] [-x] [-v] [--json]
                {hex,nmea,ublox,l1s}

azarashi CLI

positional arguments:
  {hex,nmea,ublox,l1s}  message type

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
  --json                output one JSON record per line (NDJSON) (default: False)
```
`-f` には、シリアルデバイスかファイルを指定します。`/dev/ttyS0` や `COM3` のようなシリアルデバイスを指定するときは、ボーレートを `-b` で指定してください。ファイルを指定したときは、その中身をそのまま読み込みます。

CLI は DCR と DCX の両方を表示します。DCR を表示したくないときは `-r` を、DCX を表示したくないときは `-x` を指定してください。API の [`decode_stream()`](api.md#decode_stream) はデフォルトで DCX を無視するので、CLI とは動きが違います。
## u-blox
azarashi コマンドのメッセージタイプに `ublox` を指定します。デバイスファイルのパスとボーレートは適宜変更してください。
```shell
$ azarashi ublox -f /dev/ttyS0 -b 9600
```
デバイスファイルの読み込み権限が足りないときは、sudo を使わずに、[Preparation](preparation.md) のとおりユーザを `dialout` グループに追加してください。
## Sony Spresense
azarashi コマンドのメッセージタイプに `nmea` を指定します。ボーレートは、スケッチで設定した値に合わせてください。
```shell
$ azarashi nmea -f /dev/ttyUSB0 -b 115200
```
## Hexadecimal
azarashi コマンドのメッセージタイプに `hex` を指定します。`hex` は、ヘッダとチェックサムを含まない、16進数の文字列だけのメッセージ形式です。
```shell
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```
## L1S Archive
拡張子が `.l1s` の L1S アーカイブを読むときは、メッセージタイプに `l1s` を指定します。
```shell
$ azarashi l1s -f Q002_20260917.l1s
```
アーカイブは、先頭の1バイトが衛星の PRN です。そのあとに、1秒ごとの記録が続きます。記録は、4バイトの GPS 時刻と、32バイトの L1S メッセージです。

レポートの衛星番号には、アーカイブの PRN が入ります。受信時刻には、記録ごとの GPS 時刻を UTC に直したものを使います。GPS 時刻は UTC よりうるう秒の分だけ進んでいるので、その差の18秒を引きます。受信時刻が記録から決まるので、`--time` は指定できません。

アーカイブには、災危通報のほかに、測位を補強するメッセージも入っています。災危通報でない記録は読み飛ばします。

記録の GPS 時刻は、前の記録より1日以内で先に進んでいるはずです。そうでない記録があれば、バイトが欠けたか増えたかして、記録の区切りがずれています。そのときはエラーを1つ出します。そのあと、時刻が続く記録を1バイトずつずらして探し、見つかったところから読み進めます。
## Record and Replay
`--record` を指定すると、デコードしながら、受信したデータをそのままファイルに追記します。記録したファイルを `-f` で指定するか標準入力に流すと、同じ受信を再現できます。
```shell
$ azarashi ublox -f /dev/ttyS0 --record qzss.ubx
$ azarashi ublox -f qzss.ubx
```
メッセージは日付をすべて持っているわけではありません。DCR には年がなく、DCX には曜日と時刻しかありません。足りない部分は受信時刻から補います。記録してすぐに再生するなら、そのままで正しい日付になります。前の週や前の年に記録したファイルを再生するときは、記録した時刻を `--time` で指定してください。表示する時刻も、指定した時刻になります。
```shell
$ azarashi ublox -f qzss.ubx --time 2026-09-01T12:00:00Z
```

## JSON Output

`--json` を指定すると、標準出力に1行1件の JSON（NDJSON）を出力します。エラーや入力の終わりを知らせるメッセージは標準エラー出力に書き込みます。
JSON にできないレポートは標準エラー出力に記録して読み飛ばし、読み取りは続けます。
`head` などが出力を読むのをやめてパイプが閉じたときは、何も書かずに終了します。終了コードは1です。
`--verbose`・`--source` との併用はできません。出力の定義は [JSON Output](json.md) を参照してください。

```shell
azarashi nmea --input messages.log --json > reports.ndjson
```
