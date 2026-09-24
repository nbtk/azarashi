[![Downloads](https://static.pepy.tech/personalized-badge/azarashi?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/azarashi)

<img src="https://raw.githubusercontent.com/nbtk/azarashi/refs/heads/main/logo.png" width="256">

# Azarashi
A QZSS DCR Decoder.
## Description
azarashi は、準天頂衛星みちびきが送信する災危通報メッセージのデコーダーです。u-blox と Sony Spresense が出力するメッセージ形式に対応しています。災危通報は「災害・危機管理通報サービス」の略で、防災機関が発表した地震や津波などの情報を、みちびきが送信します。

IS-QZSS-DCR-017 と IS-QZSS-DCX-004 に対応しています。DCX は災危通報の拡張メッセージで、L-Alert や J-Alert などを伝えます。
## Installation
```shell
$ pip install azarashi
```
シリアルデバイスからの読み込みに使う [pySerial](https://pyserial.readthedocs.io/en/latest/) も一緒にインストールされます。

Python 3.11 以降で動きます。
## Usage
azarashi コマンドにメッセージを渡すと、災害情報を読みやすい文章にして表示します。
```shell
$ echo '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05' | azarashi nmea
```
```
2026-09-17T14:22:41.075694Z --------------------------------
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
GPS モジュールから直接読むときは、デバイスのパスとボーレートを指定します。
```shell
$ azarashi ublox -f /dev/ttyS0 -b 9600
```
プログラムから使うときは `decode()` にメッセージを渡します。レポートオブジェクトが返り、`print()` に渡すと、さきほどのコマンドと同じ文章を表示します。災害の種類ごとのパラメータは、属性か `get_params()` で取り出せます。
```python
>>> import azarashi
>>> report = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')
>>> report.disaster_category, report.magnitude, report.seismic_epicenter
('緊急地震速報', '7.2', '日向灘')
```
ストリームから読み続けるときは `decode_stream()` を使います。シリアルデバイスは pySerial で開いて渡してください。メッセージが一つ読めるたびに `callback` が呼ばれます。
```python
import azarashi
import serial

with serial.Serial('/dev/ttyS0', 9600) as ser:
    while True:
        try:
            azarashi.decode_stream(ser, msg_type='ublox', callback=print)
        except azarashi.AzarashiReadOn as e:
            print(f'# [{type(e).__name__}] {e}')
        except azarashi.AzarashiReopenStream as e:
            print(f'# [{type(e).__name__}] {e}')
            break
        except azarashi.AzarashiStopReading:
            break
```
捕捉している3つのクラスが、次に何をすべきかを表します。

- `AzarashiReadOn`: メッセージが手に入らなかったときに送出されます。たとえば電文が壊れていたときや、azarashi がまだ対応していない種類のメッセージだったときです。ストリームは無事なので、もう一度呼べば次のメッセージに進みます。
- `AzarashiReopenStream`: ストリームの読み取りそのものが失敗したときに送出されます。たとえば USB のデバイスが抜けたときです。そのストリームは二度と読めないので、閉じて開き直してください。
- `AzarashiStopReading`: 読むものがなくなったときに送出されます。たとえば記録したファイルを最後まで読んだときです。続きは届きません。

3つは互いに継承関係がないので、どの順番に書いても同じように動きます。実際に送出されるのは、この3つのいずれかを継承した、より細かいクラスです。何が起きたかを名前が表すので、ログには `AzarashiDisconnectedError` のような具体的な名前が出ます。

呼び出し方を間違えたときは、この3つのどれでもない `AzarashiFixTheCall` の仲間が送出されます。たとえば対応していない形式を指定したときです。ループでは捕捉されず、理由を示して止まります。コードを直してください。

仕様にないコード値を受け取っただけでは例外になりません。そのコード値は `火山(コード番号：999)` のような名前にしてレポートに入れます。例外の一覧は [API](https://github.com/nbtk/azarashi/blob/main/docs/api.md) を見てください。
## Documentation
- [Preparation](https://github.com/nbtk/azarashi/blob/main/docs/preparation.md): u-blox や Sony Spresense に災危通報を出力させる設定
- [CLI](https://github.com/nbtk/azarashi/blob/main/docs/cli.md): azarashi コマンドのオプション、受信データの記録と再生
- [API](https://github.com/nbtk/azarashi/blob/main/docs/api.md): `decode()`、`decode_stream()`、例外、型ヒント、プログラムの例
- [JSON](https://github.com/nbtk/azarashi/blob/main/docs/json.md): JSON API、NDJSON 出力、JSON Schema
- [English Translation Policy](https://github.com/nbtk/azarashi/blob/main/docs/english-translation-policy.md): DCR の英語の方針と出典、azarashi が訳した英語の一覧
- [Reports](https://github.com/nbtk/azarashi/blob/main/docs/reports.md): レポートオブジェクトの共通フィールドと、形式ごとの一覧
  - [DCR](https://github.com/nbtk/azarashi/blob/main/docs/dcr.md): MT43 のクラスとフィールド、デコード例
  - [DCX](https://github.com/nbtk/azarashi/blob/main/docs/dcx.md): MT44 のクラスとフィールド、デコード例
- [Network](https://github.com/nbtk/azarashi/blob/main/docs/network.md): 受信したデータを UDP で別の装置に送る
- [Tips](https://github.com/nbtk/azarashi/blob/main/docs/tips.md): 何も表示されないとき、Encountered EOF、SD フィールドの監視
- [Development](https://github.com/nbtk/azarashi/blob/main/docs/development.md): テストと静的解析の実行方法
## Feedback
イシュー報告、プルリクエスト、コメント等、なんでもよいのでフィードバックお待ちしています。星をもらうと開発が活発になります。
Questions, suggestions, and comments are welcome! Please feel free to write in English.

## Credits
This project was originally developed during my time at BitMeister Inc., with support and resources generously provided by the company. I am really thankful for the people and the environment that helped make it happen. It is now maintained independently.
