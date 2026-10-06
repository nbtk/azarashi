[azarashi](../README.md) / JSON

# JSON Output v2

この文書は、レポートの `to_json_dict()` と `to_ndjson()`、CLI の `--json` が出力する JSON の形式と、各項目の意味を説明します。

- [JSON Schema](../azarashi/json/schemas/report-v2.schema.json)：Draft 2020-12。レポートの18種類すべてを定めます
- [コード表](json/code-tables-v2.json)：レコードの `table` と `code` で引ける表
- [整形した完全な出力例](json/report-v2.examples.pretty.json)
- [同じ内容の NDJSON](json/report-v2.examples.ndjson)

## API

```python
import sys
import azarashi

report = azarashi.decode(sentence, 'nmea')
record = report.to_json_dict()
sys.stdout.write(report.to_ndjson())
schema = azarashi.json_schema()
tables = azarashi.json_code_tables()
```

レポートの `to_json_dict()` はレコードを、`json_schema()` はパッケージに同梱されたスキーマを、`json_code_tables()` はコード表を辞書として返します。
どれも呼び出すたびに新しい辞書を返すので、返った辞書を書き換えても、レポートやほかの呼び出しの結果は変わりません。
レポートの `to_ndjson()` は、末尾の改行を含む1件分の文字列を返します。`print()` を使う場合は `end=''` を指定します。
`to_json_dict()`・`json_schema()`・`json_code_tables()` の戻り値の型は、`dict[str, JsonValue]` です。`JsonValue` は、JSON の値を表す型の別名です。
`JsonValue` が表すのは、文字列・整数・小数・真偽値・`None`、または中身が `JsonValue` のリストと辞書です。`JsonValue` は `azarashi` から import できます。

## CLI

```shell
azarashi nmea --input messages.log --json > reports.ndjson
azarashi ublox --input /dev/ttyUSB0 --json --unique
```

出力とエラーの扱いは [CLI](cli.md#json-output) にあります。

## Record

```json
{
  "schema_version": 2,
  "type": "qzss.dcx.l_alert",
  "is_test": false,
  "message_id": "qzss.dcx:cde14816c7200000000000000000002a334000000000000010",
  "series": {"lifecycle": "all_clear", "key": "111.1.36.43213"},
  "reception": {
    "at": "2026-03-07T06:00:00.000Z",
    "satellite": {"system": "qzss", "prn": 185},
    "nmea": "$QZQSM,57,C6B084CDE14816C7200000000000000000002A33400000000000001112B9590*70"
  },
  "texts": {"en": "### DCX Message - L-Alert ###\n..."},
  "data": {"...": "..."}
}
```

レコードの中のどのオブジェクトでも、キーを出さないことと、値を `null` にすることは、意味が違います。
この文書では、キーを出さないことを「省く」と書きます。

- キーを省く：その項目が、このレコードに当てはまらないことを表します。たとえば、南海トラフ地震に関連する情報でない DCR のレポートには、`series.key` がありません。
- 値を `null` にする：その項目は当てはまるが、値がないことを表します。たとえば、衛星のわからない入力では、`reception.satellite` が `null` です。

| キー | 何がわかるか | 内容 |
|---|---|---|
| `schema_version` | どの版の形式か | 整数 `2` |
| `type` | 何のレポートか | `qzss.dcr.tsunami` などの固定識別子 |
| `is_test` | 訓練/試験か | 真偽値 |
| `message_id` | どのメッセージか | `==` で等しいレポートなら同じ値。[Duplicates](#duplicates) を参照 |
| `series` | ほかのメッセージとどうつながるか | [Series](#series) を参照。つながりのないレポートでは省きます |
| `reception` | いつ、どの衛星で受けたか | 受信ごとに変わる値 |
| `texts` | 何と言っているか | 言語ごとの文章 |
| `data` | その中身を項目ごとに | 種類ごとに定めた内容 |

`is_test` は、DCR では通報区分のコードが 7（訓練/試験）のとき、DCX では A1 のコードが 0（Test）のときに `true` です。
DCX の空メッセージ（`qzss.dcx.null`）は警報を持たないので、`is_test` は常に `false` です。
`is_test` の元のコードは、DCR では `data.report_classification`、DCX では `data.message_type` にあります。

### Reception

| キー | 内容 |
|---|---|
| `at` | UTC の受信時刻。ミリ秒まで書き、末尾は `Z` |
| `satellite` | `{"system": "qzss", "prn": 186}`。不明なら `null` |
| `nmea` | azarashi が生成した QZQSM センテンス。省きません。行末の改行は含みません |

QZQSM センテンスは `$QZQSM,<衛星 ID>,<メッセージの16進63桁>*<チェックサム>` の形です。
衛星 ID は、L1S の PRN の下位6ビットを十進で書いたもので、PRN183 なら 55 です。
hex のように衛星のわからない入力では、azarashi は衛星 ID を 55 にします。
受信した衛星は `satellite` で確かめてください。衛星がわからないときは、`satellite` は `null` です。

### Texts

`texts` は、言語コードをキーにした文章です。`texts` の中身は、`report.get_texts()` と同じです。

| レポート | `ja` | `en` |
|---|---|---|
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | あり | あり |
| DCR の南海トラフ地震に関連する情報 | あり | なし |
| DCR の北西太平洋津波情報 | なし | あり |
| DCX | なし | あり |

DCX の `en` には、`str(report)` にある日本語の行、「A11 - Instruction (ja)」「EX1 - Target area (ja)」「EX9 - Target area list (ja)」は入りません。
日本語の指示と地名は、`data` のそれぞれのコードの `labels.ja` にあります。

## Duplicates

同じメッセージは、複数の衛星から、違うプリアンブルで繰り返し届きます。
`message_id` は、メッセージの種類とレポートの `raw` から作る文字列です。同じメッセージなら、衛星やプリアンブルが違っても、`message_id` は同じ値です。

`message_id` の形は「システムとメッセージの種類」「:」「レポートの `raw` の16進」です。

- システムとメッセージの種類は、`type` の先頭の2つです。例：`qzss.dcr`、`qzss.dcx`。
- `raw` は、メッセージから、プリアンブルや CRC など、衛星ごと・送信ごとに変わる部分を除いたものです。DCX では、衛星指定マスクも除きます。
  `message_id` には、`raw` を小文字の16進で書きます。

```text
qzss.dcr:af89a820000324000050400548c5e2c000000003dff8001c000010
qzss.dcx:0de102111de000000000000000000001134000000000000000
```

別の発表のメッセージでも、`message_id` が同じになることがあります。`raw` の中の時刻に、DCR では年がなく、DCX では日付がないからです。

- DCR の `raw` は、発表時刻を月・日・時・分で持ちます。たとえば、2026年3月10日10時0分の発表と、2027年3月10日10時0分の発表は、ほかの中身も同じなら、`message_id` が同じです。
- DCX の `raw` は、災害の始まる時刻を、受信した週から数えた週（A6）と、週の中の曜日と時分（A7）で持ちます。たとえば、ある週に受信した「その週の月曜日13時0分に始まる」警報と、次の週に受信した「その週の月曜日13時0分に始まる」警報は、ほかの中身も同じなら、`message_id` が同じです。

そのため、重複を除くときは、`message_id` が同じレコードのうち、受信時刻の差が、DCR では1年、DCX では1週間より短いものを、同じ発表の繰り返しとして捨ててください。
A7 が 0 の DCX の警報は、始まる時刻を持たないので、受信時刻の差を使っても別の発表と見分けられません。

レポートの `==` と、CLI の `--unique`・`decode_stream()` の `unique` も、`message_id` が同じレポートを同じものとみなします。

## Series

`lifecycle` は、そのレポートが発表・訂正・取消・更新・解除のどれに当たるかを表します。

| レポート | 元のコード | `lifecycle` |
|---|---|---|
| DCR | 情報形態 0 発表 | `issue` |
| DCR | 情報形態 1 訂正 | `correction` |
| DCR | 情報形態 2 取消 | `cancellation` |
| DCR | 表にない情報形態 | `null` |
| DCX | A1 1 Alert | `issue` |
| DCX | A1 2 Update | `update` |
| DCX | A1 3 All Clear | `all_clear` |

DCX の A1 0 Test と空メッセージは、そのどれにも当たらないので `lifecycle` を省きます。

`key` は、更新や解除のレポートが、どの警報に当たるかを表す文字列です。
IS-QZSS-DCX-004 の 4.2.3.1 は、更新（Update）と解除（All Clear）が指す警報を、項目の値が一致することで見分けると定めています。L-Alert と地方公共団体からの情報では A2・A3・A4・EX1、J-Alert では A2・A3・A4 です。`key` は、これらの値を `.` でつないだものです。

| レポート | `key` の元 | 例 |
|---|---|---|
| DCX の L-Alert と地方公共団体からの情報 | A2・A3・A4・EX1 | `111.1.36.43213` |
| DCX の J-Alert | A2・A3・A4 | `111.2.95` |
| DCR の南海トラフ地震に関連する情報 | 発表時刻・通報区分・情報形態・情報番号・総ページ数 | `2026-08-21T01:35Z.7.0.5.27` |

表の例の `111.1.36.43213` は、日本（A2=111）の L-Alert（A3=1）が出した、地震（A4=36）の、熊本県宇城市（EX1=43213）の警報です。`111.2.95` は、日本の消防庁（A3=2）が出した Safety warning（A4=95）です。
南海トラフ地震に関連する情報は、1つの発表を複数のページに分けて送ります。同じ発表のページは、どれも同じ `key` を持ちます。
ほかの DCR、国外の機関からの情報、種類のわからない DCX には `key` がありません。

`lifecycle` も `key` もないレポートでは、`series` を省きます。

## Status

`data` のコード・数量・時刻・位置・楕円には、どれにも `status` があります。その値をそのまま使ってよいかは、`status` だけで判断できます。
`hazard` や `instruction`、`forecasts` の要素のように、ほかのオブジェクトをまとめるオブジェクトと、南海トラフの `page` には、`status` はありません。

| `status` | 意味 |
|---|---|
| `valid` | そのまま使ってよい値 |
| `assumed` | 仮の値。緊急地震速報の仮定震源（仕様書の assumptive hypocenter）の深さとマグニチュード |
| `special` | 仕様が定めた特殊な値。そのまま使える値ではありません。意味は `labels` にあり、`labels` は空になりません |
| `undefined` | 表にないコード |

`special` のコードには、次のようなものがあります。

- 値がわからない：「不明 / Unknown」
- 値がない：「なし / None」「該当情報なし / No data」「指示なし / No instruction」
- 仕様が値のない印として割り当てた値：「Not used」
- 気象庁が表にない値を送るときのコード：「その他の警報」「北海道のその他の市町村」など。IS-QZSS-DCR-017 は、このコードを、気象庁のシステムの改修で
  表にない値を送るときに使う、と注で説明しています。地域ごとの「その他」は、`labels` でどの都道府県や地方かがわかります
- 月や年までしかわからない時刻：火山の日時で Du が 6（Approximate time (month)）・7（Approximate time (year)）のとき。メッセージの時刻の部分は日・時・分なので、月や年の精度の時刻を表せません

仕様が割り当てていない値は `undefined` です。

## Codes and Labels

```json
{
  "status": "valid",
  "code": "610",
  "table": "qzss.dcr.tsunami_forecast_region",
  "labels": {"ja": "高知県", "en": "Kochi Prefecture"}
}
```

`table` と `code` を合わせて、1つのコードを表します。
`code` は非負整数の十進文字列で、先頭にゼロを付けません。
コード表のファイルのキーも文字列なので、`code` の値でそのまま表を引けます。

`table` は `<仕様の名前>.<表の名前>` です。国や版で中身が変わる表は、そのあとに `.` で国や版を続けます。

| `table` | 表 |
|---|---|
| `qzss.dcr.<表の名前>` | DCR の表。例：`qzss.dcr.tsunami_height` |
| `camf.a1_message_type` など | CAMF の A1〜A10、A17、C7〜C10、D1〜D36 |
| `camf.a3_provider_identifier.country_N` | A2 の国 N が割り当てる提供者 |
| `camf.a11_instruction_library.international.version_V.list_a`、`camf.a11_instruction_library.international.version_V.list_b` | CAMF の国際ライブラリ（A9=0）の版 V の List A と List B |
| `camf.a11_instruction_library.country_N.version_V` | 国 N のライブラリ（A9=1）の版 V |
| `qzss.dcx.ex1_target_area_code` | DCX の EX1 の地域コード。EX8=1 のときの EX9 の地域コードも同じ表です |
| `qzss.dcx.ex2_evacuate_direction_type` | DCX の EX2 |
| `qzss.dcx.ex9_target_area_code_list` | DCX の EX9 の都道府県。`code` は都道府県の番号（北海道1〜沖縄47）で、DCR の都道府県のコードと同じです |

N と V は、伝送されたコード値です。

`labels` は、コードの名前を言語ごとに持ちます。日本語の名前があるときだけ `ja` を、英語の名前があるときだけ `en` を持ちます。
`labels` の値が空文字列になることはありません。`undefined` のコードは、`labels` が空オブジェクトです。

DCR の英語は、気象庁の多言語辞書や気象庁のページ、DCR 仕様書の英語から取っています。
気象庁が英語を出していないものは、azarashi の訳です。
英訳の方針と、azarashi の訳の一覧は [English Translation Policy](english-translation-policy.md) にあります。
azarashi が訳した防災事項の文には、末尾に `(Translated by azarashi)` を付けています。
この印がない英語が、気象庁の英語だとは限りません。
意味の基準は、常に日本語の `ja` です。

日本のライブラリのコード0は、DCX 仕様書が本文で no instruction と定めるコードです。`status` は `special`、`labels` は
`{"ja": "指示なし", "en": "No instruction"}` です。このコードは表にないので、この名前は日本語も英語も azarashi が付けたものです。
国際ライブラリの List A と List B のコード0も、CAMF の注記が指示なしと定めているので、`status` は `special`、`labels.en` は `No instruction` です。
List B のコード29と30は、表で reserved なので `undefined` です。
C10 のコード0は、CAMF の注記が指示なしと定めているので、`status` は `special`、`labels.en` は `No instruction` です。
A4 のコード0と、4か国（日本、オーストラリア、フィジー、タイ）の A3 のコード0は、仕様が not used と定めているので、
`status` は `special`、`labels.en` は `Not used` です。azarashi はほかの国の A3 の表を持たないので、ほかの国の A3 は、コード0も `undefined` です。

### Instruction

`data.instruction` は、A9 のライブラリ（`library`）、A10 の版（`library_version`）、A11 の指示（`content`）を持ちます。
国際ライブラリ（A9=0）では、`content.list_a` と `content.list_b` がそれぞれ5ビットのコードオブジェクトです。
各オブジェクトには、CAMF の指示の名前 `identifier`（`IC-A-04`、`IC-B-02` など）があります。
azarashi が対応していない A10 の版では、両方のオブジェクトの `status` は `undefined`、`identifier` は `null` です。
`source.a11` は、分割前の10ビット全体の整数です。

国のライブラリ（A9=1）では、`content` が10ビット全体のコードオブジェクトです。
`identifier` と `source` は省きます。

## Code Tables

コード表は、レコードの `table` と `code` で引ける1つの JSON です。
[docs/json/code-tables-v2.json](json/code-tables-v2.json) にあります。Python では `json_code_tables()` で同じ中身が取れます。
コード表にあるコードでは、レコードの `status` と `labels` は、コード表の `status` と `labels` と同じです。

```json
{
  "schema_version": 2,
  "tables": {
    "qzss.dcr.seismic_intensity_lower_limit": {
      "source": "IS-QZSS-DCR-017 Table 4.1.2-8",
      "codes": {
        "1": {"status": "valid", "labels": {"ja": "震度0", "en": "Seismic intensity of 0"}},
        "15": {"status": "special", "labels": {"ja": "不明", "en": "Unknown"}}
      }
    }
  }
}
```

| キー | 内容 |
|---|---|
| `source` | コードを定める仕様書の表 |
| `codes` | 表にあるコードごとの `status` と `labels`。`status` は `valid` か `special` です |

コードの数の大小は、値の大小を表しません。たとえば、国内津波の高さのコード15「その他の津波の高さ」は、コード6「10m超」より高いという意味ではありません。値を比べるときは、数量の `value` や `range` を使ってください。
国や版で中身が変わる表は、azarashi が持っている国と版の分だけ、コード表に入っています。
持っていない国や版の表（たとえば `camf.a3_provider_identifier.country_103`）は、ファイルにありません。
そうした表を指すコードは、`status` が `undefined`、`labels` が `{}` です。

`labels` の決め方は、どの表も同じです。表がコードに言葉を付けていればその言葉、数だけを定めていれば、その数に仕様の単位を付けた文字列です。
たとえば、DCR の深さの `labels.en` は `10 km`、CAMF の D3 は `22.5°` です。単位のない数の `labels` は数だけで、マグニチュードは `7.2`、CAMF の D4 は `0.25` です。

## Quantities

深さや高さなど、コードが数を表す値は、コードオブジェクトに数を足した形です。

```json
{
  "status": "valid",
  "value": 40,
  "unit": "km",
  "code": "40",
  "table": "qzss.dcr.depth_of_hypocenter",
  "labels": {"ja": "40km", "en": "40 km"}
}
```

| キー | 内容 |
|---|---|
| `value` | コードが表す1つの数 |
| `range` | コードが表す範囲。`{"lower": 数, "upper": 数}`。片側がなければその側が `null` |
| `unit` | UCUM の単位。`Cel` は ℃、`"1"` は単位のない数（マグニチュードや倍率など） |
| `relative_to` | 値が倍率や相対的な角度のとき、何に対する値か。同じレコードの項目を指します。CAMF の D4 と C7〜C9 だけです |

1つのオブジェクトに、`value` と `range` が両方あることはありません。
`special` のコードで数がないものは、`value` が `null` です。「不明」や「その他の津波の高さ」がこれに当たります。
`valid` のコードで数を表さないものは、`value` と `range` のどちらも省きます。北西太平洋津波の高さの「巨大」「高い」がこれに当たります。
範囲が端を含むかどうかは、`labels` の「未満」「超」などの言い回しで判断してください。

震源のマグニチュードのコード126「不明(8.0より大きい)」は、`status` が `special` で、`range` が `{"lower": 8, "upper": null}` です。

### Tsunami Height

国内津波の表示区分と範囲は次のとおりです。h は津波の高さ（m）です。

| コード | 表示 | 範囲 |
|---|---|---|
| 1 | 0.2m未満 | h < 0.2 |
| 2 | 1m | 0.2 ≤ h ≤ 1 |
| 3 | 3m | 1 < h ≤ 3 |
| 4 | 5m | 3 < h ≤ 5 |
| 5 | 10m | 5 < h ≤ 10 |
| 6 | 10m超 | 10 < h |
| 13 / 14 | 該当情報なし / 不明 | `special`、`value` は `null` |
| 15 | その他の津波の高さ | `special`、`value` は `null` |

この範囲の境界は[気象庁の高さ区分](https://www.jma.go.jp/jma/kishou/know/jishin/joho/tsunamiinfo.html)に対応します。

北西太平洋津波の高さのコード1〜4では、`range` は仕様の表の範囲です。たとえば 0.3〜1 です。
508「10m 超」の `range` は `{"lower": 10, "upper": null}` です。
511「不明」の `status` は `special` です。

CAMF の災害別詳細（D1〜D36）のうち、数値や数値の範囲を表す12項目も同じ形で出力します。

| 項目 | 形 | 単位 |
|---|---|---|
| D1 マグニチュード | `range` | `1` |
| D3 主楕円中心から震央への方位 | `value` | `deg` |
| D4 主楕円中心から震央への距離 | `value` | `1`。主楕円の半長軸の何倍か。km は `value` × `main_ellipse.value.semi_major_axis_km` |
| D5 波の高さ | `range` | `m` |
| D6 気温 | `range` | `Cel`（℃） |
| D8 風速 | `range` | `km/h` |
| D9 降水量 | `range` | `mm/h` |
| D13 視程 | `range` | `m` |
| D14 積雪深 | `range` | `cm` |
| D26 10万人あたりの患者数 | `range` | `1` |
| D27 騒音 | `range` | `dB` |
| D29 停電の見込み時間 | `range` | `min` |

仕様の表には `1.0-1.9` と `2.0-2.9`、`1km/h < v < 5km/h` と `6km/h < v < 11km/h` のように丸めた数で
書かれた範囲があります。azarashi は、D26 以外の表を、すきまのない範囲の並びとして読みます。各範囲の上限は次の範囲の下限です。
たとえば、D1 のコード0「1.0-1.9」の `range` は `{"lower": 1.0, "upper": 2.0}`、D8 のコード2「6km/h < v < 11km/h」の `range` は `{"lower": 6, "upper": 12}` です。
azarashi は、表によって単位が違う項目を、1つの単位にそろえます。視程はメートル、停電時間は分です。

D2 の地震係数は日本の震度の段階（5弱・5強など）なので、azarashi は数値にせず、コードで出力します。
上の表にないほかの項目も、数値ではない区分なのでコードで出力します。

## Time

```json
{
  "status": "valid",
  "value": "2026-08-21T00:01:00Z",
  "precision": "minute",
  "source": {"day": 21, "hour": 0, "minute": 1}
}
```

| キー | 内容 |
|---|---|
| `value` | UTC の日時。末尾は `Z`。`status` が `valid` でなければ `null` |
| `precision` | どこまでわかっている時刻か。`minute`、`hour`、`day` |
| `labels` | `special` の時刻が何を意味するか |
| `source` | メッセージにある時刻の部分。`status` によらず省きません |

`precision` は、`status` が `valid` のときだけあります。

azarashi は、メッセージにない年や月、週を、次の時刻から補います。

| フィールド | 取り得る `status` | `source` | 補う元の時刻 |
|---|---|---|---|
| `report_time` | `valid` | 月・日・時・分 | `reception.at` |
| `occurrence_time`、`reference_time`、降灰の `activity_time` | `valid`、`undefined` | 日・時・分 | `report_time` |
| 火山の `activity_time` | `valid`、`special`、`undefined` | 日・時・分 | `report_time` |
| 津波と北西太平洋津波の `arrival` | `valid`、`special`、`undefined` | 日・時・分 | `report_time` |
| DCX の `onset` | `valid`、`special`、`undefined` | 週・週内分 | `reception.at` |

メッセージの時刻の部分が時刻でない値を表すときは、`status` が `special` で、その意味は `labels` にあります。

| フィールド | `labels` |
|---|---|
| 津波の `arrival` | 「津波到達中と推測」、「該当情報なし」と、その英語 |
| 北西太平洋津波の `arrival` | `Arrived or Unknown` |
| 火山の `activity_time` | Du が 6・7 のときの Du の名前。例 `Approximate time (month)` |
| DCX の `onset` | `Not used`（A7 が 0） |

火山の `activity_time` の `precision` は、日時の曖昧さ（Du）で決まります。Du が 0〜3 なら `minute`、4 なら `hour`、5 なら `day` です。
火山のレコードは、`activity_time_ambiguity` も省きません。`activity_time_ambiguity` は Du のコードオブジェクトで、表は `qzss.dcr.ambiguity_of_activity_time` です。
この表の英語のラベルは DCR 仕様書の文言です。日本語の表はないので、`labels` に `ja` はありません。

## Regions, Forecasts and Positions

地域ごとに繰り返す項目は、1つの地域を1つのオブジェクトにした配列です。
津波の `forecasts` の要素は、`region`・`arrival`・`height` を省きません。
ほかの警報の配列の要素も、地域とその警報内容を一緒に持ちます。洪水の `warnings` の要素も `{region, warning}` です。

DCX の `target_regions` は地域のコードオブジェクトの配列です。
EX1 が 0 のときは、対象地域の指定がないので、`target_regions` は空の配列です。
EX9 のコードは、EX8 によって都道府県か市町村かが変わります。
都道府県なら `qzss.dcx.ex9_target_area_code_list`、市町村なら EX1 と同じ `qzss.dcx.ex1_target_area_code` の表のコードになります。

DCR の位置は、次の形です。

```json
{
  "status": "valid",
  "value": {"latitude": 26.6, "longitude": 127.6},
  "unit": "deg",
  "source": {
    "latitude_hemisphere": 0, "latitude_degrees": 26, "latitude_minutes": 36, "latitude_seconds": 0,
    "longitude_hemisphere": 0, "longitude_degrees": 127, "longitude_minutes": 36, "longitude_seconds": 0
  }
}
```

緯度経度は符号付きで、北緯と東経が正です。メッセージの位置のコードが位置を表さないときは、`status` は `undefined`、`value` は `null` です。
azarashi は、DCR の緯度経度を小数点以下9桁に、DCX の楕円の中心を小数点以下6桁に丸めます。

DCX の楕円は、次の形です。

```json
{
  "status": "valid",
  "value": {
    "centre": {"latitude_deg": 5.11284, "longitude_deg": 95.769926},
    "semi_major_axis_km": 165.324,
    "semi_minor_axis_km": 90.407,
    "azimuth_deg": -45.0
  },
  "source": {"centre_latitude": 34629, "centre_longitude": 100404, "semi_major_axis": 22, "semi_minor_axis": 20, "azimuth": 16}
}
```

`value` の中の軸の長さは km、座標と角度は度です。単位は、キーの名前の末尾に付いています。
角度は、仕様の規約どおり、東を0度として、東から北へ回る向きを正とします。
航海用の北基準の方位角と混同しないでください。

緯度は ±90 度、経度は ±180 度を超えることがあります。
補正楕円の中心は、主楕円の中心に C1・C2 の小さな補正（最大で約0.0024度）を足すので、極や経度180度をわずかに越えることがあります。
追加楕円の中心の経度は、EX4 が東経45度から数えるので、45〜225度です。
災害の中心は主楕円の中心から最大10度ずれるので、緯度は±100度、経度は±190度までになります。楕円の方位 `azimuth_deg` は、どの楕円も -90 度以上 90 度未満です。

楕円の `source` は、その楕円を組み立てた伝送コードです。
`source` がどのフィールドのコードかは、どの楕円かで決まります。`main_ellipse` は A12〜A16、
`specific_settings.refined_ellipse` は C1〜C4 と A16、`evacuation.ellipse` は EX3〜EX7 です。

`specific_settings` は、A17 のコードオブジェクト `type` と、その種類のグループを1つ持ちます。

| A17 | グループ | 内容 |
|---|---|---|
| 0 | `refined_ellipse` | 補正楕円 |
| 1 | `hazard_centre` | 災害の中心。`source` は主楕円の中心からの相対コード（C5・C6） |
| 2 | `second_ellipse` | 主楕円から作る第二楕円。下の表のとおり |
| 3 | `hazard_details` | 災害別詳細 |

第二楕円は、主楕円を動かし、拡げ、回して作ります。

| キー | CAMF | 形 | 単位 | `relative_to` | 意味 |
|---|---|---|---|---|---|
| `shift` | C7 | 数量 | `1` | `main_ellipse.semi_major_axis` | 第二楕円の中心を、主楕円の中心から半長軸に沿ってずらす距離。km は `value` × `main_ellipse.value.semi_major_axis_km` |
| `scale_factor` | C8 | 数量 | `1` | `main_ellipse` | 軸の長さの倍率。第二楕円の半長軸は `value` × `semi_major_axis_km`、半短軸は `value` × `semi_minor_axis_km` |
| `bearing` | C9 | 数量 | `deg` | `main_ellipse.azimuth` | 主楕円の方位からの回転角。第二楕円の方位は `main_ellipse.value.azimuth_deg` + `value`（東から北へ） |
| `instruction` | C10 | コード | | | 第二楕円の中にいる人への指示 |

JSON には、第二楕円の中心の緯度経度と、軸の長さは入りません。上の表の式で求めてください。

`evacuation` は、追加楕円 `ellipse` と、避難方向 `direction`（EX2 のコードオブジェクト）を持ちます。

## Report Types and Field Mapping

この節は、レポートのクラスと `type` の対応と、レポートのフィールドが JSON のどのキーになるかを示します。

レポートの次のフィールドとメソッドは、レコードの `data` の外のキーになります。

| レポート | JSON |
|---|---|
| `timestamp` | `reception.at` |
| `satellite_prn` | `reception.satellite` |
| `nmea` | `reception.nmea` |
| `raw` | `message_id` |
| `get_texts()` | `texts` |

### DCR

どの DCR のレコードの `data` にも、次のキーがあります。

| レポート | `data` のキー |
|---|---|
| `version` | `version` |
| `report_time` | `report_time` |
| `report_classification_no`（通報区分） | `report_classification` |
| `information_type_no`（情報形態） | `information_type` |

災害種別（`disaster_category_no`）は、`type` で表します。

DCR の `version` は `{"status": …, "value": …}` です。`value` が仕様の定める1なら、`status` は `valid`、それ以外なら `undefined` です。

DCR のコードオブジェクトの `code` は、レポートの `_raw` か `_no` のフィールドの値を、十進の文字列にしたものです。
レポートの表示用のフィールド（たとえば `magnitude`）に当たるのは、`labels` です。

災害種別ごとに、`data` には次のキーもあります。

| クラス | `type` | `data` のキー |
|---|---|---|
| `dcr.EarthquakeEarlyWarning` | `qzss.dcr.earthquake_early_warning` | `occurrence_time`、`depth`、`magnitude`、`epicenter`、`intensity_lower`、`intensity_upper`、`long_period_ground_motion_lower`、`long_period_ground_motion_upper`、`target_regions`、`notifications` |
| `dcr.Hypocenter` | `qzss.dcr.hypocenter` | `occurrence_time`、`depth`、`magnitude`、`epicenter`、`position`、`notifications` |
| `dcr.SeismicIntensity` | `qzss.dcr.seismic_intensity` | `occurrence_time`、`observations`（要素のキーは `region`、`intensity`） |
| `dcr.NankaiTroughEarthquake` | `qzss.dcr.nankai_trough_earthquake` | `information_serial`、`page`（キーは `number`、`total`、`content_hex`） |
| `dcr.Tsunami` | `qzss.dcr.tsunami` | `warning`、`notifications`、`forecasts`（要素のキーは `region`、`height`、`arrival`） |
| `dcr.NorthwestPacificTsunami` | `qzss.dcr.northwest_pacific_tsunami` | `tsunamigenic_potential`、`forecasts`（要素のキーは `region`、`height`、`arrival`） |
| `dcr.Volcano` | `qzss.dcr.volcano` | `volcano`、`warning`、`activity_time`、`activity_time_ambiguity`、`target_regions` |
| `dcr.AshFall` | `qzss.dcr.ash_fall` | `volcano`、`warning_type`、`activity_time`、`forecasts`（要素のキーは `region`、`elapsed_time`、`warning`） |
| `dcr.Weather` | `qzss.dcr.weather` | `warning_state`、`warnings`（要素のキーは `region`、`warning`） |
| `dcr.Flood` | `qzss.dcr.flood` | `warnings`（要素のキーは `region`、`warning`） |
| `dcr.Typhoon` | `qzss.dcr.typhoon` | `reference_time`、`reference_time_type`、`elapsed_time`、`number`、`scale_category`、`intensity_category`、`position`、`central_pressure`、`maximum_wind_speed`、`maximum_gust_wind_speed` |
| `dcr.Marine` | `qzss.dcr.marine` | `warnings`（要素のキーは `region`、`warning`） |

長周期地震動の上下限は、コード0「該当情報なし」のときも、`special` のコードオブジェクトです。

### DCX

`qzss.dcx.null` 以外の DCX のレコードの `data` には、次の警報共通のキーがあります。

| CAMF の項目 | `data` のキー |
|---|---|
| Vn | `version` |
| A1 | `message_type` |
| A2 | `country` |
| A3 | `provider` |
| A4 | `hazard` |
| A5 | `severity` |
| A6・A7 | `onset` |
| A8 | `duration` |
| A9・A10・A11 | `instruction` |

`message_type` は CAMF の A1 です。L1S の Message Type（43・44）ではありません。
`hazard` は、`type`・`category`・`definition` の3つのコードオブジェクトを持ちます。
この3つは、1つの A4 のコードを、種類・区分・説明の3つの表で引いたものです。`code` はどれも同じです。

DCX の `version` も同じ形です。L-Alert、J-Alert、地方公共団体からの情報では、`value` が仕様の定める1なら、`status` は `valid`、それ以外なら `undefined` です。
国外の機関からの情報では、`status` は値によらず `valid` です。
種類のわからない DCX では、`status` は値によらず `undefined` です。

クラスごとに、`data` には次のキーもあります。

| クラス | `type` | 警報共通のキーのほかのキー |
|---|---|---|
| `dcx.NullMsg` | `qzss.dcx.null` | なし。`data` は `{}` で、警報共通のキーもありません |
| `dcx.OutsideJapan` | `qzss.dcx.outside_japan` | `main_ellipse`、`specific_settings` |
| `dcx.LAlert` | `qzss.dcx.l_alert` | `main_ellipse` か `target_regions` のどちらか一方、`specific_settings` |
| `dcx.JAlert` | `qzss.dcx.j_alert` | `target_regions` |
| `dcx.MTInfo` | `qzss.dcx.mt_info` | `main_ellipse`、`target_regions`、`specific_settings`、`evacuation` |
| `dcx.Unknown` | `qzss.dcx.unknown` | `main_ellipse`、`specific_settings` |

`specific_settings` があるかどうかと、その中身は、A17 に応じて決まります。
`evacuation` は、追加楕円の EX3〜EX7 がすべて0のときは省きます。

CAMF と DCX の項目は、次のキーに入ります。

| CAMF と DCX の項目 | `data` のキー |
|---|---|
| A12〜A16 | `main_ellipse` |
| A17、C1〜C4 | `specific_settings.refined_ellipse` |
| A17、C5〜C6 | `specific_settings.hazard_centre` |
| A17、C7〜C10 | `specific_settings.second_ellipse` |
| A17、D1〜D36 | `specific_settings.hazard_details`。キーは、レポートのフィールド名から `d1_` などを除いた名前です。たとえば `d1_magnitude_on_richter_scale` は `magnitude_on_richter_scale` です。数値を表す12項目は数量、ほかはコードです |
| EX1 | `target_regions` |
| EX2〜EX7 | `evacuation` |
| EX8〜EX9 | `target_regions` |
| SDMT・SDM（衛星指定マスク）、EX10（予備）、種類ごとに使われない拡張領域 | 出力しません。元のビット列は `reception.nmea` にあります |

## Corrections, Cancellations and All Clears

DCX の L-Alert、J-Alert、地方公共団体からの情報の更新と解除は、`series.key` が同じレポートの警報を指します。
DCR の訂正と取消、国外の機関からの情報には、元のレポートと対応づける項目がありません。

レポートを取り消すことと、警報そのものが終わることは別のものです。

| 意味 | レポート | どこで読むか |
|---|---|---|
| レポートの取消 | DCR | `series.lifecycle` が `cancellation`（情報形態 2） |
| 危険の終わり | DCX | `series.lifecycle` が `all_clear`（A1 3） |
| 警報の解除（警報すべて） | 気象 | `data.warning_state` のコード 2 解除 |
| 警報の解除 | 津波 | `data.warning` のコード 2 警報解除 |
| 警報の解除（地域ごと） | 洪水 | `data.warnings[].warning` のコード 1 警報解除 |
| 警報の解除（地域ごと） | 海上 | `data.warnings[].warning` のコード 0 海上警報解除 |

## Nankai Trough Pages

`page` は1ページ分です。ページの境界で UTF-8 の文字が切れることがあるので、`page` は本文を `content_hex` に16進で持ちます。
同じ発表のページは、`series.key` でまとめられます。
`texts.ja` は、変換する時点までに受信したページから組み立てた文章です。後からページが届くと、同じページを変換し直したときに文章が変わります。

## Validation and Versioning

`$id` は `urn:azarashi:report:2` です。外部スキーマの参照はありません。
スキーマは形を検証します。下限≦上限のような項目間の関係と、コードと名前の一致は検証しません。名前が正しいかは、コード表と照らして確かめられます。
スキーマで検証するときは、format の検証を有効にしてください。

azarashi は、同じ版の中でも、キーとレポートの種類を足すことがあります。読む側は、知らないキーと知らない `type` を無視してください。
スキーマも、知らないキーと、`qzss.dcr.tsunami` と同じ形の知らない `type` を受け付けます。

既存のキーの意味・形・単位を変えるとき、既存のキーに新しい値（`status` や `lifecycle` の種類など）を足すとき、
キーを消すときは、`schema_version` を上げます。コード表に新しいコードが加わるのと、表示の文言の修正は、このどれにも当たりません。
azarashi が Galileo EWS に対応するときは、v3 にします。v2 の `reception.satellite.system` は `qzss` だけです。

`schema_version` は整数で、azarashi 自身のバージョンとは独立です。

公開しているのは、レポートの `to_json_dict()`・`to_ndjson()` と、`azarashi` から取れる `json_schema()`・`json_code_tables()`・`JsonValue` です。
`azarashi.json` の中の内部名は互換性の対象ではありません。

`to_json_dict()` は、返すレコードをスキーマで検証しません。検証が必要なときは、`json_schema()` でスキーマを取得し、検証ライブラリに渡してください。
