[azarashi](../README.md) / Tips

# Tips
この文書は、よくつまずくところと、その見分け方をまとめます。
## Nothing Is Printed / UnicodeDecodeError
受信機のボーレートと、それを読むシリアルポートのボーレートが違うと、azarashi は壊れたビット列を受け取るので、災危通報を見つけられません。azarashi コマンドは、災危通報でないデータを、エラーを出さずに読み飛ばします。そのため、何も出力されないまま時間が過ぎることがあります。よく使われるボーレートは次のとおりです。
```
9600, 19200, 38400, 57600, 115200
```
シリアルポートのボーレートは、azarashi コマンドでは [`-b` オプション](cli.md)で指定します。受信機の設定方法は、受信機のマニュアルを参照してください。

[`decode_stream()`](api.md#decode_stream) にテキストモードで開いたストリームを渡していると、壊れたビット列を読んだときに、ストリーム自体が次の例外を送出することがあります。ストリームを `'rb'` のバイナリモードで開けば、この例外は送出されません。azarashi は、壊れた行を読み飛ばすか、`AzarashiReadOn` を継承した例外で知らせます。
```
[UnicodeDecodeError] 'utf-8' codec can't decode byte 0xNN in position XX: ~
```
## Encountered EOF
azarashi コマンドは、読み込んでいるストリームの書き込み側が閉じられると、標準エラー出力に Encountered EOF と出力して終了します。これはエラーではなく、正常な終了です。
## DCX Satellite Designation Field
[DCX メッセージ](dcx.md)の衛星指定マスクを監視するときは、`decode_stream()` の `unique` を指定しないでください。`unique` は衛星指定マスクの違いを見ないので、衛星指定マスクだけが変わったメッセージを重複として捨てます。
