[azarashi](../README.md) / Reports

# Reports
この文書は、`decode()` と `decode_stream()` が返すレポートを説明します。メッセージの種類によって、返るクラスが変わります。どのクラスが返るかは `isinstance()` で確かめてください。使い方は [API](api.md) にあります。

レポートの `get_params()` は、レポートのフィールドを辞書で返します。返された辞書や、その中のリストを変更しても、元のレポートは変わりません。DCX のレポートでは、メッセージで使われていない項目のフィールドは、辞書に入りません。そのフィールドを属性として読むと `None` です。すべてのフィールドは、この文書と [DCR](dcr.md)、[DCX](dcx.md) の文書に載っています。辞書の値には、`bytes`、`datetime`、`CAMF` などのオブジェクトも含まれます。レポートを JSON にするときは、[`report.to_json_dict()`](json.md) を使ってください。

フィールド名の接尾辞には、次の決まりがあります。

- `_raw`: 受信した値そのものです。コード表に名前がない値も、`_raw` のフィールドには残ります。
- `_en`: 英語の表記です。
- `_no`: 受信したコードです。azarashi は、このコードで、レポートのクラスや文章の形を決めます。

値については次の3点に注意してください。

- 日時のフィールドは、常にタイムゾーン付きの UTC です。
- 型が `DayHourMinute` と `Coordinates` のフィールドは、受信した値を持つ辞書です。`DayHourMinute` のキーは `day`・`hour`・`minute` です。`Coordinates` のキーは、緯度の `lat_ns`・`lat_d`・`lat_m`・`lat_s` と、経度の `lon_ew`・`lon_d`・`lon_m`・`lon_s` です。`lat_ns` と `lon_ew` は、0 が北緯か東経、1 が南緯か西経です。
- 時刻として読めない値が届いたときは、その時刻のフィールドは `None` になります。

`print(report)` や `str(report)` は、レポートを文章にして返します。その文章は、DCR では日本語、DCX と北西太平洋津波情報では英語です。
DCX の文章には、「(ja)」の付いた日本語の行も入ります。

`report.get_text()` は、言語を指定して文章を返します。言語は `'ja'` や `'en'` のコードで指定します。

```python
report.get_text()            # そのレポートが書かれている言語の文章。None になりません
report.get_text('en')        # 英語の文章。なければ None
report.get_text('en', 'ja')  # 英語の文章。なければ日本語の文章。どちらもなければ None
report.get_texts()           # そのレポートが持つすべての言語の文章。{'ja': '…', 'en': '…'}
```

`report.get_texts()` の辞書は、そのレポートが書かれている言語が先頭です。`get_texts()` は、呼び出すたびに新しい辞書を返します。
JSON の `texts` は、この辞書と同じ中身です。

| レポート | `get_text()` | `get_text('ja')` | `get_text('en')` |
|---|---|---|---|
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | 日本語 | 日本語 | 英語 |
| DCR の南海トラフ地震に関連する情報 | 日本語 | 日本語 | `None` |
| DCR の北西太平洋津波情報 | 英語 | `None` | 英語 |
| DCX | 英語 | `None` | 英語 |

- DCR の日本語は、`str(report)` と同じ文字列です。
- DCR の英語は、気象庁が公表している英語です。気象庁の英語がない部分は、azarashi が訳しています。出典と方針は [English Translation Policy](english-translation-policy.md) にあります。
- DCX の英語は、`str(report)` から「(ja)」の行を除いた文字列です。
- 北西太平洋津波情報の英語は、`str(report)` と同じ文字列です。

文章の中の時刻は、レポートによって JST か UTC かが違います。

| レポート | 出力 | タイムゾーン | 形式の例 |
|---|---|---|---|
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | `str(report)` | JST | 8月21日9時4分 |
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | `report.get_text('en')` | JST | 09:04 JST, 21 Aug. |
| DCR の南海トラフ地震に関連する情報 | `str(report)` | JST | 8月21日9時4分 |
| DCR の南海トラフ地震に関連する情報 | `report.get_text('en')` | なし（`None` を返します） | |
| DCR の北西太平洋津波情報 | `str(report)` | UTC | --08-21T00:04Z |
| DCR の北西太平洋津波情報 | `report.get_text('en')` | UTC | --08-21T00:04Z |
| DCX | `str(report)` | UTC | 2026-09-17T01:00:00Z |
| DCX | `report.get_text('en')` | UTC | 2026-09-17T01:00:00Z |

DCR の火山の活動時刻については、日付だけが有効なとき（Du=5）に限り、文章は UTC の日付をそのまま表示します。

## Construction, Mutation and Subclassing

レポートは `decode()` か `decode_stream()` で受け取ってください。
レポートのコンストラクタの引数は、版によって変わります。`get_params()` の辞書からは、レポートを作れません。

レポートのフィールドと、その中のリストと辞書は、変更できます。変わるのは、変更したフィールドだけです。
たとえば `magnitude` を変更しても、`magnitude_raw`・`message`・`raw`・`nmea` は変わりません。
JSON の `labels` も変わりません。`labels` は、`magnitude` ではなく `magnitude_raw` のコードから決まるからです。

レポートには、自分の属性を足せます。名前は、既存のフィールドと重ならないものにしてください。
足した属性は `get_params()` の辞書に入りますが、JSON には入りません。
`get_params()` は値を `copy.deepcopy()` でコピーするので、足す値は `copy.deepcopy()` でコピーできるものにしてください。

フィールドを変更するときは、そのフィールドの型と意味に合う値を設定してください。
タイムゾーンのない日時、NaN、型の違う値、長さのそろわないリストなどを設定すると、`str()` や JSON への変換が失敗することがあります。

レポートの `==` は、クラスと `raw` が同じときに真です。衛星・受信時刻・表示用のフィールドが違っても、等しいとみなします。
レポートを set の要素や dict のキーにしている間は、`raw` を変更しないでください。変更すると、そのレポートを set や dict の中で見つけられなくなります。

レポートのクラスを継承して、メソッドを足すこともできます。
継承したクラスのレポートと、元のクラスのレポートは、`raw` が同じでも等しくありません。

azarashi は、この文書と [DCR](dcr.md)、[DCX](dcx.md) の文書に載っているレポートの属性とメソッドの互換性を、できる限り保ちます。
以前の版の名前も使えます。たとえば `QzssDcReportJmaTsunami` は、今も `dcr.Tsunami` として使えます。
`azarashi.definitions`、`azarashi.decoders`、`azarashi.json` の中の名前は、版によって変わります。

## Common Fields
どのレポートにも、次のフィールドがあります。
| フィールド | 型 | 内容 |
|---|---|---|
| `sentence` | `str \| bytes` | 受け取った入力。NMEA センテンス、UBX フレーム、16進数の文字列など |
| `message` | `bytes` | 250ビットの L1S メッセージを入れた32バイト |
| `nmea` | `str` | azarashi が `message` から作った QZQSM センテンス |
| `raw` | `bytes` | `message` から、プリアンブルや CRC など、衛星ごと・送信ごとに変わる部分を除いたもの。`==` は、これで比べます。どのビットかは [Duplicates](json.md#duplicates) にあります |
| `timestamp` | `datetime` | 受信時刻 |
| `message_header` | `str \| bytes \| None` | 入力のヘッダ。NMEA では `'$QZQSM'`、u-blox では UBX-RXM-SFRBX のヘッダのバイト列 |
| `satellite_id` | `int \| None` | 衛星 ID。PRN の下位6ビット |
| `satellite_prn` | `int \| None` | 衛星の PRN |
| `satellite_svid` | `int \| None` | u-blox の受信機が衛星に付けた番号 |
| `preamble` | `str` | プリアンブル。`'A'`、`'B'`、`'C'` のどれか |
| `message_type` | `str` | `'DCR'` か `'DCX'` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

## DCR and DCX
メッセージの種類は2つあり、返るクラスもフィールドも種類で変わります。

- [DCR (MT43)](dcr.md): 気象庁が発表する防災気象情報です。災害種別ごとにクラスが分かれます。
- [DCX (MT44)](dcx.md): 気象庁以外の機関が発表するメッセージです。発信元ごとにクラスが分かれます。
