[azarashi](../README.md) / Reports

# Reports
`decode()` と `decode_stream()` が返すレポートの一覧です。メッセージの種類によって、返るクラスが変わります。どのクラスが返るかは `isinstance()` で確かめてください。使い方は [API](api.md) にあります。

`get_params()` は、そのインスタンスに保存された属性の深いコピーを返します。返された辞書や内部のリストを変更しても、元のレポートには影響しません。DCX の省略されたフィールドなど、クラスの既定値として参照できる `None` は、辞書に含まれないことがあります。全フィールドの一覧が必要なときは、この文書と型定義を参照してください。値には `bytes`、`datetime`、`CAMF` などのオブジェクトも含みます。JSON にするときは [`to_json_dict()`](json.md) を使ってください。

フィールド名の接尾辞には決まりがあります。

- `_raw`: 受信した値そのものです。名前を持たない値でも、ここには残ります。
- `_en`: 英語の表記です。
- `_no`: azarashi が処理の分岐に使う番号です。

値については次の3点に注意してください。

- 日時の属性は、常にタイムゾーン付きの UTC です。
- `DayHourMinute` と `Coordinates` は辞書です。前者は `day`、`hour`、`minute` を、後者は緯度と経度を持ちます。
- 時刻として読めない値が届いたときは、その時刻のフィールドは `None` になります。

`print(report)` や `str(report)` は、レポートを文章にして返します。DCR は日本語で、DCX と北西太平洋津波情報は英語です。
DCX の文章には、「(ja)」の付いた日本語の行も入ります。

`report.get_text()` は、言語を指定して文章を返します。言語は `'ja'` や `'en'` のコードで指定します。

```python
report.get_text()            # そのレポートが書かれている言語の文章。必ずある
report.get_text('en')        # 英語の文章。なければ None
report.get_text('en', 'ja')  # 英語の文章。なければ日本語の文章。どちらもなければ None
report.get_texts()           # そのレポートが持つすべての言語の文章。{'ja': '…', 'en': '…'}
```

`report.get_texts()` の辞書は、そのレポートが書かれている言語が先頭です。呼び出すたびに新しい辞書を返します。
JSON の `texts` は、この辞書と同じ中身です。

| レポート | `get_text()` | `get_text('ja')` | `get_text('en')` |
|---|---|---|---|
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | 日本語 | 日本語 | 英語 |
| DCR の南海トラフ地震に関連する情報 | 日本語 | 日本語 | `None` |
| DCR の北西太平洋津波情報 | 英語 | `None` | 英語 |
| DCX | 英語 | `None` | 英語 |

- DCR の日本語は、`str(report)` と同じ文字列です。
- DCR の英語は、気象庁の英語を出典にしています。出典と方針は [English Translation Policy](english-translation-policy.md) にあります。
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

DCR の火山の活動時刻は、日付だけが有効なとき（Du=5）に限り、UTC の日付をそのまま表示します。

## Construction, Mutation and Subclassing

レポートは `decode()` か `decode_stream()` で受け取ってください。
レポートのコンストラクタの引数は、版によって増えたり変わったりします。サブクラスから基底クラスのコンストラクタを呼ぶときも同じです。
`get_params()` の辞書は、中身を読むためのものです。レポートを作り直すのには使えません。

公開のデータ属性とリスト・辞書の変更をサポートします。ただし変更は、その属性だけに作用します。
例えば `magnitude` を変更しても `magnitude_raw`・`message`・`raw`・`nmea` は再計算されません。
JSON の `labels` も、表示用の属性ではなくコード表から取るので変わりません。
利用者の付加情報は、既存名と衝突しない属性として保存できます。
付加したインスタンス属性も `get_params()` の対象なので、深いコピーが可能な値を使ってください。JSON には入りません。

属性を変更するときは、そのフィールドで定められた型と意味に合う値を設定してください。
タイムゾーンのない日時、NaN、型の違う値、長さのそろわないリストなどを設定すると、`str()` や JSON への変換が失敗することがあります。

比較は「同じ具象クラス、同じ `raw`」で、ハッシュは `raw` に基づきます。
衛星・受信時刻・表示用属性は比較に使いません。set の要素・dict のキーとして使用中は
`raw` を変更しないでください。

レポートのクラスを継承すると、補助メソッドなどを足せます。
基底クラスのインスタンスとそのサブクラスのインスタンスは、同じ `raw` でも等しくありません。

この文書にある公開レポートの属性とメソッド、既存の旧名は互換性の対象です。できる限り互換性を保ちます。
`azarashi.definitions` のモジュール経路・内部の定義名、および `azarashi.decoders` の段階構成・context・内部コンストラクタは、対象に含めません。
`azarashi.json` の中の内部名も同様です。

## Common Fields
`base.Base` のフィールドです。どのレポートにもあります。
| フィールド | 型 |
|---|---|
| `sentence` | `str \| bytes` |
| `raw` | `bytes` |
| `timestamp` | `datetime` |

メッセージを取り出せたレポートには、`base.MessagePartial` のフィールドが加わります。
| フィールド | 型 |
|---|---|
| `message` | `bytes` |
| `nmea` | `str` |
| `message_header` | `str \| bytes \| None` |
| `satellite_id` | `int \| None` |
| `satellite_prn` | `int \| None` |
| `satellite_svid` | `int \| None` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

DCR と DCX のレポートには、さらに `base.MessageBase` の次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `preamble` | `str` |
| `message_type` | `str` |

## DCR and DCX
メッセージの種類は2つあり、返るクラスもフィールドも種類で変わります。

- [DCR (MT43)](dcr.md): 気象庁が発表する防災気象情報です。災害種別ごとにクラスが分かれます。
- [DCX (MT44)](dcx.md): 気象庁以外の機関が発表するメッセージです。発信機関ごとにクラスが分かれます。
