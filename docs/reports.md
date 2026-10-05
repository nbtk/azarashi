[azarashi](../README.md) / Reports

# Reports
この文書は、`decode()` と `decode_stream()` が返すレポートを説明します。メッセージの種類によって、返るクラスが変わります。どのクラスが返るかは `isinstance()` で確かめてください。使い方は [API](api.md) にあります。

レポートの `get_params()` は、レポートのインスタンスに保存された属性を、深いコピーの辞書で返します。返された辞書や、その中のリストを変更しても、元のレポートには影響しません。インスタンスに保存されていないフィールドは、辞書に入りません。たとえば、DCX のメッセージに含まれていなかったフィールドです。そのフィールドを属性として読むと、クラスの既定値の `None` が返ります。全フィールドの一覧が必要なときは、この文書と型定義を参照してください。辞書の値には、`bytes`、`datetime`、`CAMF` などのオブジェクトも含まれます。レポートを JSON にするときは、[`report.to_json_dict()`](json.md) を使ってください。

フィールド名の接尾辞には、次の決まりがあります。

- `_raw`: 受信した値そのものです。コード表に名前がない値も、`_raw` のフィールドには残ります。
- `_en`: 英語の表記です。
- `_no`: azarashi が処理の分岐に使う番号です。

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
レポートのコンストラクタの引数は、版によって増えたり変わったりします。サブクラスから基底クラスのコンストラクタを呼ぶ場合も、引数は版によって変わります。
`get_params()` の辞書は、中身を読むためのものです。レポートを作り直すのには使えません。

レポートの公開フィールドと、その中のリストと辞書は、変更できます。ただし変更は、そのフィールドだけに作用します。
たとえば `magnitude` を変更しても `magnitude_raw`・`message`・`raw`・`nmea` は再計算されません。
JSON の `labels` は、表示用のフィールドではなくコード表から値を取るので、変わりません。
利用者は、自分の情報を、既存の名前と衝突しない属性としてレポートに保存できます。
付加したインスタンス属性も `get_params()` の対象なので、深いコピーが可能な値を使ってください。付加した属性は JSON には入りません。

フィールドを変更するときは、そのフィールドの型と意味に合う値を設定してください。
タイムゾーンのない日時、NaN、型の違う値、長さのそろわないリストなどを設定すると、`str()` や JSON への変換が失敗することがあります。

レポートの `==` は、同じ具象クラスで同じ `raw` のときに真になります。ハッシュは `raw` に基づきます。
`==` は、衛星・受信時刻・表示用のフィールドを比べません。レポートを set の要素や dict のキーとして使っている間は、
`raw` を変更しないでください。

レポートのクラスを継承すると、補助メソッドなどを足せます。
基底クラスのインスタンスとそのサブクラスのインスタンスは、同じ `raw` でも等しくありません。

この文書に載っているレポートの属性とメソッドは、互換性の対象です。以前の版の名前も互換性の対象で、たとえば `QzssDcReportJmaTsunami` は今も `dcr.Tsunami` として使えます。azarashi は、これらの互換性をできる限り保ちます。
`azarashi.definitions` のモジュール経路・内部の定義名、および `azarashi.decoders` の段階構成・context・内部コンストラクタは、互換性の対象に含めません。
`azarashi.json` の中の内部名も同様です。

## Common Fields
どのレポートにも、この節の3つの表のフィールドがあります。次の表は `base.Base` のフィールドです。
| フィールド | 型 |
|---|---|
| `sentence` | `str \| bytes` |
| `raw` | `bytes` |
| `timestamp` | `datetime` |

`base.MessagePartial` は `base.Base` を継承し、次のフィールドを加えます。
| フィールド | 型 |
|---|---|
| `message` | `bytes` |
| `nmea` | `str` |
| `message_header` | `str \| bytes \| None` |
| `satellite_id` | `int \| None` |
| `satellite_prn` | `int \| None` |
| `satellite_svid` | `int \| None` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

`base.MessageBase` は `base.MessagePartial` を継承し、次のフィールドを加えます。DCR と DCX のレポートは、どれも `base.MessageBase` を継承します。
| フィールド | 型 |
|---|---|
| `preamble` | `str` |
| `message_type` | `str` |

## DCR and DCX
メッセージの種類は2つあり、返るクラスもフィールドも種類で変わります。

- [DCR (MT43)](dcr.md): 気象庁が発表する防災気象情報です。災害種別ごとにクラスが分かれます。
- [DCX (MT44)](dcx.md): 気象庁以外の機関が発表するメッセージです。発信元ごとにクラスが分かれます。
