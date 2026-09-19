[azarashi](../README.md) / Tips

# Tips
よくつまずくところと、その見分け方です。
## Nothing Is Printed / UnicodeDecodeError
GPS モジュールと接続するインタフェースのボーレートが一致していないと、壊れたビット列を受け取るため災危通報を検出できません。azarashi CLI は壊れた行を読み飛ばして動作を続けるので、エラーが出ないまま何も出力されないことがあります。ボーレートは例えば次のような値です。
```
9600, 19200, 38400, 57600, 115200
```
azarashi CLI では [`-b` オプション](cli.md)で指定します。GPS モジュール側の設定方法はモジュールのマニュアルを参照してください。

[`decode_stream()`](api.md#decode_stream) にテキストモードで開いたストリームを渡していると、壊れたビット列を読んだときに、ストリーム自体が次の例外を送出することがあります。ストリームを `'rb'` のバイナリモードで開けば、壊れた行は読み飛ばされます。
```
[UnicodeDecodeError] 'utf-8' codec can't decode byte 0xNN in position XX: ~
```
## Encountered EOF
azarashi CLI は、読み込んでいるストリームの書き込み側が閉じられると、stderr に Encountered EOF と出力して終了します。これはエラーではなく、正常な終了です。
## DCX Satellite Designation Field
[DCX メッセージ](dcx.md)の SD フィールドを監視するときは、`decode_stream()` の `unique` を指定しないでください。`unique` は、CAMF フィールドが同じ DCX メッセージを重複とみなし、SD フィールドの違いを見ません。そのため、SD フィールドだけが変わったメッセージを取りこぼし、SD フィールドの変化を監視できません。
