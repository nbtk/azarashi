[azarashi](../README.md) / CLI

# CLI
azarashi コマンドを使うと、プログラムを書かずに災危通報メッセージをデコードできます。
```shell
$ echo '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05' | azarashi nmea
```
azarashi コマンドのオプションは、次のとおりです。
```shell
usage: azarashi [-h] [-f INPUT] [-b BAUDRATE] [--record RECORD] [--time TIME]
                [-s] [-u] [-r] [-x] [-v] [--json] [--english]
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
  -u, --unique          suppress duplicate messages (default: False)
  -r, --ignore-dcr      ignore dcr messages (default: False)
  -x, --ignore-dcx      ignore dcx messages (default: False)
  -v, --verbose         verbose mode (default: False)
  --json                output one JSON record per line (NDJSON) (default:
                        False)
  --english             output the text in English where the report has it
                        (default: False)
```
`-f` には、シリアルデバイスかファイルを指定します。`/dev/ttyS0` や `COM3` のようなシリアルデバイスを指定するときは、ボーレートを `-b` で指定してください。

azarashi コマンドは DCR と DCX の両方を表示します。DCR を表示したくないときは `-r` を、DCX を表示したくないときは `-x` を指定してください。
## u-blox
u-blox の受信機から読むときは、azarashi コマンドの形式に `ublox` を指定します。
```shell
$ azarashi ublox -f /dev/ttyS0 -b 9600
```
azarashi コマンドは、受信機が出すフレームのうち、QZSS の L1S 信号の災危通報だけを読み、ほかのフレームを読み飛ばします。

デバイスファイルの読み込み権限が足りないときは、sudo を使わずに、[Preparation](preparation.md) のとおりユーザを `dialout` グループに追加してください。
## Sony Spresense
Sony Spresense から読むときは、azarashi コマンドの形式に `nmea` を指定します。ボーレートは、スケッチで設定した値に合わせてください。
```shell
$ azarashi nmea -f /dev/ttyUSB0 -b 115200
```
## Hexadecimal
16進数の文字列を読むときは、azarashi コマンドの形式に `hex` を指定します。`hex` の入力は、QZQSM センテンスからヘッダとチェックサムを除いた、メッセージの16進63桁です。
```shell
$ echo C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC | azarashi hex
```
## L1S Archive
拡張子が `.l1s` の L1S アーカイブを読むときは、形式に `l1s` を指定します。
```shell
$ azarashi l1s -f Q002_20260917.l1s
```
アーカイブは、先頭の1バイトが衛星の PRN です。そのあとに、1秒ごとの記録が続きます。記録は、4バイトの GPS 時刻と、32バイトの L1S メッセージです。

レポートの `satellite_prn` には、アーカイブの PRN が入ります。レポートの受信時刻は、記録ごとの GPS 時刻を UTC に直したものです。受信時刻が記録から決まるので、`--time` は指定できません。

アーカイブには、災危通報のほかに、測位を補強するメッセージも入っています。azarashi コマンドは、災危通報でない記録を読み飛ばします。

記録の GPS 時刻は、前の記録より1日以内で先に進んでいるはずです。そうでない記録があれば、バイトが欠けたか増えたかして、記録の区切りがずれています。そのとき、azarashi コマンドはエラーを1つ出します。そのあと、時刻が続く記録を1バイトずつずらして探し、見つかったところから読み進めます。
## English
`--english` を指定すると、azarashi コマンドは DCR のレポートを英語で表示します。英語の文章は、気象庁が公表している英語を使います。気象庁の英語がない部分は、azarashi が訳しています。出典と方針は [English Translation Policy](english-translation-policy.md) にあります。
```shell
$ azarashi nmea -f messages.log --english
```
azarashi コマンドは、DCX と北西太平洋津波情報を、`--english` を指定しなくても英語で表示します。`--english` を指定すると、azarashi コマンドは、DCX のレポートから「(ja)」の付いた日本語の行を除いて表示します。南海トラフ地震に関連する情報には英語の文章がないので、azarashi コマンドは、`--english` を指定しても日本語で表示します。
`--english` は、`--json` とも `--verbose` とも併用できません。JSON では、そのレポートが持つすべての言語の文章が `texts` に入ります。

## Record and Replay
`--record` を指定すると、azarashi コマンドは、デコードしながら、受信したデータをそのままファイルに追記します。記録したファイルを `-f` で指定するか標準入力に流すと、同じ受信を再現できます。
```shell
$ azarashi ublox -f /dev/ttyS0 --record qzss.ubx
$ azarashi ublox -f qzss.ubx
```
メッセージの日時には、欠けている部分があります。DCR の日時には年がなく、DCX の日時には曜日と時刻しかありません。azarashi コマンドは、足りない部分を受信時刻から補います。記録してすぐに再生するなら、`--time` を指定しなくても日付は正しくなります。前の週や前の年に記録したファイルを再生するときは、記録した時刻を `--time` で指定してください。出力に表示する受信時刻も、指定した時刻になります。
```shell
$ azarashi ublox -f qzss.ubx --time 2026-09-01T12:00:00Z
```

## JSON Output

`--json` を指定すると、標準出力に1行1件の JSON（NDJSON）を出力します。azarashi コマンドは、1件ごとに出力をフラッシュします。エラーと Encountered EOF は、標準エラー出力に書き込みます。
JSON にできないレポートがあると、azarashi コマンドは、そのエラーを標準エラー出力に書き込み、そのレポートを読み飛ばして読み取りを続けます。
`head` などが出力を読むのをやめてパイプが閉じたとき、azarashi コマンドは何も書かずに終了します。終了コードは1です。
`--json` は、`--verbose` とも `--source` とも併用できません。出力の定義は [JSON Output](json.md) を参照してください。

```shell
azarashi nmea --input messages.log --json > reports.ndjson
```
