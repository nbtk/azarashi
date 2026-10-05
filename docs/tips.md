[azarashi](../README.md) / Tips

# Tips
よくつまずくところと、その見分け方です。
## Nothing Is Printed / UnicodeDecodeError
受信機のボーレートと、それを読むシリアルポートのボーレートが違うと、壊れたビット列を受け取るため災危通報を検出できません。azarashi コマンドは壊れた行を読み飛ばして動作を続けるので、エラーが出ないまま何も出力されないことがあります。よく使われるボーレートは次のとおりです。
```
9600, 19200, 38400, 57600, 115200
```
azarashi コマンドでは [`-b` オプション](cli.md)で指定します。受信機の設定方法は、受信機のマニュアルを参照してください。

[`decode_stream()`](api.md#decode_stream) にテキストモードで開いたストリームを渡していると、壊れたビット列を読んだときに、ストリーム自体が次の例外を送出することがあります。ストリームを `'rb'` のバイナリモードで開けば、壊れた行は読み飛ばされます。
```
[UnicodeDecodeError] 'utf-8' codec can't decode byte 0xNN in position XX: ~
```
## Encountered EOF
azarashi コマンドは、読み込んでいるストリームの書き込み側が閉じられると、stderr に Encountered EOF と出力して終了します。これはエラーではなく、正常な終了です。
## DCX Satellite Designation Field
[DCX メッセージ](dcx.md)の衛星指定マスクを監視するときは、`decode_stream()` の `unique` を指定しないでください。`unique` は衛星指定マスクの違いを見ないので、衛星指定マスクだけが変わったメッセージを重複として捨てます。
