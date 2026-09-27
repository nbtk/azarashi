[azarashi](../README.md) / JSON

# JSON Output v2

`to_json_dict()` と `to_ndjson()`、CLI の `--json` が出力する JSON の形式と、各項目の意味を説明します。

- [JSON Schema](../azarashi/json/schemas/report-v2.schema.json)：Draft 2020-12、全18種類
- [コード表](json/code-tables-v2.json)：レコードの `table` と `code` で引ける表
- [整形した完全な出力例](json/report-v2.examples.pretty.json)
- [同じ内容の NDJSON](json/report-v2.examples.ndjson)

出力例は、受信したログと合成したテストメッセージから作りました。受信日時は固定の値です。

## API

```python
import sys
import azarashi

report = azarashi.decode(sentence, 'nmea')
record = azarashi.to_json_dict(report)
sys.stdout.write(azarashi.to_ndjson(report))
schema = azarashi.json_schema()
tables = azarashi.code_tables()
```

`to_json_dict(report)` は独立した辞書を返します。戻り値を変更しても、レポートや次の出力に影響しません。
`to_ndjson(report)` は末尾の改行を含む1件分の文字列です。`print()` を使う場合は `end=''` を指定します。
`json_schema()` はパッケージに同梱されたスキーマを、`code_tables()` はコード表を辞書として返します。
どちらも呼び出すたびに新しい辞書を返します。
辞書の戻り値の型は `dict[str, JsonValue]` です。`JsonValue` は JSON で表せる値の型で、`azarashi` からインポートできます。

レポートのサブクラスは基底クラスと同じ形式で出力し、追加した属性は含めません。
レポートでないものを渡すと `AzarashiArgumentTypeError` になります。これは `TypeError` の一種です。
azarashi がデコードしたレポートは、必ず JSON にできます。あとから属性に NaN や無限大、要素数の
そろわない予報の配列などを設定すると、変換が失敗します。
コードの名前はコード表から取ります。レポートの表示用の属性だけを変更しても、`data` の `labels` は変わりません。

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

| キー | 答える問い | 内容 |
|---|---|---|
| `schema_version` | どの版の形式か | 整数 `2` |
| `type` | 何の報か | `qzss.dcr.tsunami` などの固定識別子 |
| `is_test` | 訓練・試験か | 真偽値 |
| `message_id` | どの電文か | 同じ電文なら同じ値。[Duplicates](#duplicates) を参照 |
| `series` | ほかの電文とどうつながるか | [Series](#series) を参照。つながりのない報では省きます |
| `reception` | いつ、どの衛星で受けたか | 受信ごとに変わる値 |
| `texts` | 何と言っているか | 言語ごとの文章 |
| `data` | 何と言っているか | 種類ごとに定めた内容 |

`is_test` は、DCR では通報区分のコードが 7（訓練/試験）のとき、DCX では A1 のコードが 0（Test）のときに `true` です。
DCX の空メッセージ（`qzss.dcx.null`）は警報を持たないので、常に `false` です。
元のコードは、DCR では `data.report_classification`、DCX では `data.message_type` にあります。

### Reception

| キー | 内容 |
|---|---|
| `at` | UTC の受信日時。ミリ秒まで書き、末尾は `Z` |
| `satellite` | `{"system": "qzss", "prn": 186}`。不明なら `null` |
| `nmea` | ライブラリが生成した QZQSM 文。行末改行なし |

衛星番号が不明な入力から NMEA を生成するときは、既定値の55が入ります。
受信した衛星を確認するときは、NMEA の中の番号ではなく `satellite` を参照してください。

### Texts

`texts` は、言語コードをキーにした文章です。`report.get_texts()` と同じ中身です。

| 報 | `ja` | `en` |
|---|---|---|
| DCR（南海トラフ地震に関連する情報と北西太平洋津波情報を除く） | あり | あり |
| DCR の南海トラフ地震に関連する情報 | あり | なし |
| DCR の北西太平洋津波情報 | なし | あり |
| DCX | なし | あり |

DCX の `en` は英語の行だけです。`str(report)` の「(ja)」の付いた日本語の行は入りません。
DCX の日本語の地名は、`data` の `labels.ja` にあります。

## Duplicates

同じ電文は、複数の衛星から、違うプリアンブルで繰り返し届きます。
`message_id` が同じレコードは、同じ電文です。どの衛星で、どのプリアンブルで受け取っても、同じ値になります。

形は「システムと形式」「:」「電文の中身の16進」です。

- システムと形式は、`type` の先頭の2つです。例：`qzss.dcr`、`qzss.dcx`。
- 電文の中身は、衛星ごと・送信ごとに変わる部分を除いたビット列を、小文字の16進にしたものです。
  除くのは、プリアンブル、CRC、DCX の衛星指定マスクです。DCR は27バイト（54桁）、DCX は CAMF から25バイト（50桁）です。

```text
qzss.dcr:af89a820000324000050400548c5e2c000000003dff8001c000010
qzss.dcx:0de102111de000000000000000000001134000000000000000
```

まったく同じ中身の電文が、ずっと後に送られることもあります。そのときも `message_id` は同じです。
重複を除くときは、時間の範囲と組み合わせてください。DCR は月日時分を持つので1年以内、
DCX は週の中の分を持つので1週間以内なら、同じ値は同じ電文です。
CLI の `--unique` と `decode_stream()` の `unique` も、`message_id` と同じ部分で同じ電文かを判断します。

## Series

`series` は、その電文がほかの電文とどうつながるかを示します。

`lifecycle` は、その電文が一連の報に対して何をするかです。

| 報 | 元のコード | `lifecycle` |
|---|---|---|
| DCR | 情報形態 0 発表 | `issue` |
| DCR | 情報形態 1 訂正 | `correction` |
| DCR | 情報形態 2 取消 | `cancellation` |
| DCR | 表にない情報形態 | `null` |
| DCX | A1 1 Alert | `issue` |
| DCX | A1 2 Update | `update` |
| DCX | A1 3 All Clear | `all_clear` |

DCX の A1 0 Test と空メッセージは、一連の報に何もしないので `lifecycle` を省きます。

`key` は、一連の報を名指す文字列です。同じ `key` の電文は、同じ一連の報です。
仕様が「同じ」と定める項目の値を、`.` でつないでいます。

| 報 | `key` の元 | 例 |
|---|---|---|
| DCX の L-Alert と市町村からの情報 | A2・A3・A4・EX1 | `111.1.36.43213` |
| DCX の J-Alert | A2・A3・A4 | `111.2.95` |
| DCR の南海トラフ地震に関連する情報 | 発表時刻・通報区分・情報形態・情報番号・総ページ数 | `2026-08-21T01:35Z.7.0.5.27` |

DCX は IS-QZSS-DCX-004 の 4.2.3.1 に従います。南海トラフ地震に関連する情報の `key` は、同じ発表のページをまとめます。
ほかの DCR、国外からの情報、種類のわからない DCX には `key` がありません。

`lifecycle` も `key` もない報では、`series` そのものを省きます。

`data.message_type` は CAMF の A1 です。QZSS のメッセージタイプ（43・44）ではありません。
A1 の意味は、`is_test`（A1=0）と `series.lifecycle`（A1=1〜3）でも読めます。
DCR の `report_classification` と `information_type` も、同じように `is_test` と `series.lifecycle` で読めます。

## Status

`data` のコード・数量・時刻・位置・楕円には、どれにも `status` があります。そのまま使ってよいかは、`status` だけで判断できます。
`hazard` や `instruction`、`forecasts` の要素のような入れ物と、南海トラフの `page` には、`status` はありません。

| `status` | 意味 |
|---|---|
| `valid` | そのまま使ってよい値 |
| `assumed` | 仮の値。緊急地震速報の仮定震源（仕様書の assumptive hypocenter）の深さとマグニチュード |
| `special` | 仕様が定めた特殊な値。そのまま使える値ではありません。意味は、必ずある `labels` にあります |
| `undefined` | 表にないコード |

`special` の例です。

- 値がわからない：「不明 / Unknown」
- 値がない：「なし / None」「該当情報なし / No data」「指示なし / No instruction」
- 仕様が値のない印として割り当てた値：「Not used」（IS-QZSS-DCX-004 2.4 の Not used）
- 気象庁が表にない値を送るときのコード：「その他の警報」「北海道のその他の市町村」など。IS-QZSS-DCR-017 は、気象庁のシステムの改修で
  表にない値を送るときに使う、と注で説明しています。地域ごとの「その他」は、`labels` でどの都道府県や地方かがわかります
- 電文自身が無効と言っている値：火山の日時で Du が 6・7 のとき

仕様が割り当てていない値（IS-QZSS-DCX-004 2.4 の Reserved）は `undefined` です。

キーを省くのと `null` は、意味が違います。

- キーを省く：その項目は、このレコードに当てはまらない。
- `null`：当てはまるが、値がない。

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
コード表のファイルのキーも文字列なので、そのまま引けます。

`table` は `<仕様の名前>.<表の名前>` です。国や版で中身が変わる表だけ、`.` で絞り込みを続けます。

| `table` | 表 |
|---|---|
| `qzss.dcr.<表の名前>` | DCR の表。例：`qzss.dcr.tsunami_height` |
| `camf.a1_message_type` など | CAMF の A1〜A10、A17、C7〜C10、D1〜D36 |
| `camf.a3_provider_identifier.country_N` | A2 の国 N が割り当てる提供者 |
| `camf.a11_instruction_library.international.version_V` | CAMF の国際ライブラリ（A9=0）の版 V |
| `camf.a11_instruction_library.country_N.version_V` | 国 N のライブラリ（A9=1）の版 V |
| `qzss.dcx.ex1_target_area_code` | DCX の EX1 の地域コード。EX8=1 のときの EX9 の地域コードも同じ表です |
| `qzss.dcx.ex2_evacuate_direction_type` | DCX の EX2 |
| `qzss.dcx.ex9_target_area_code_list` | DCX の EX9 の都道府県。`code` は表 4.2-25 を上から数えた番号（北海道1〜沖縄47）で、DCR の表 4.1.2-16 の Code と同じです |

N と V は、伝送されたコード値です。

`labels` は、コードの名前を言語ごとに持ちます。日本語・英語がある場合だけ `ja`・`en` を出します。
`labels` の値が空文字列になることはありません。`undefined` のコードは、`labels` が空オブジェクトです。

DCR の英語は、気象庁の多言語辞書や気象庁のページ、DCR 仕様書の英語から取っています。
気象庁が英語を出していないものは、azarashi の訳です。
気象庁の公式の英語が出たら、それに置き換えます。英訳の方針と、azarashi の訳の一覧は [English Translation Policy](english-translation-policy.md) にあります。
防災事項の文のうち azarashi の訳は、末尾に `(Translated by azarashi)` と付けています。
この印がない英語が、気象庁の英語だとは限りません。
意味の正は、常に日本語の `ja` です。

日本のライブラリのコード0は、DCX 仕様書が本文で no instruction と定めるコードです。`status` は `special`、`labels` は
`{"ja": "指示なし", "en": "No instruction"}` です。表にはないので、この名前は日本語も英語も azarashi が付けたものです。
国際ライブラリのコード0は、CAMF の IC-A-01 で、表では reserved です。`status` は `undefined` です。
C10 のコード0は、CAMF の注記が指示なしと定めているので、`status` は `special`、`labels.en` は `No instruction` です。
A4 のコード0と、表 4.2-6 の4か国（日本、オーストラリア、フィジー、タイ）の A3 のコード0は、仕様が not used と定めているので、
`status` は `special`、`labels.en` は `Not used` です。ほかの国の A3 は azarashi が表を持たないので、コード0も `undefined` です。

### Instruction

`data.instruction` は、A9 のライブラリ（`library`）、A10 の版（`library_version`）、A11 の指示（`content`）を持ちます。
国際ライブラリの指示には、CAMF の指示の名前 `identifier`（`IC-A-02` など）を添えます。名前のわからないコードでは `null` です。
国のライブラリには CAMF の名前がないので、`identifier` を省きます。

## Code Tables

コード表は、レコードの `table` と `code` で引ける1つの JSON です。
[docs/json/code-tables-v2.json](json/code-tables-v2.json) にあります。Python では `code_tables()` で同じ中身が取れます。
レコードの `status` と `labels` は、コード表と必ず一致します。

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

コードの並び順に意味はありません。段階で比べたいときは、`labels` や数量の `range` を見てください。
国や版で変わる表は、azarashi が持っている国と版の分だけ並べます。
持っていない国や版の表（たとえば `camf.a3_provider_identifier.country_103`）は、ファイルにありません。
そうした表を指すコードは、必ず `status` が `undefined`、`labels` が `{}` です。

`labels` の決め方は、どの表も同じです。表がコードに言葉を付けていればその言葉、数だけを定めていれば、その数に仕様の単位を付けた文字です。
単位のない数は、数だけです。DCR の深さの `10 km`、マグニチュードの `7.2`、CAMF の D3 の `22.5°`、D4 の `0.25` がその例です。

## Quantities

深さや高さなど、コードが数を表す値は、コードオブジェクトに数を足した形で出力します。

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

`value` と `range` は、どちらか一方だけです。
`special` のコードで数がないものは、`value` が `null` です。「不明」や「その他の津波の高さ」がこれに当たります。
`valid` のコードで数を表さないものは、どちらも省きます。北西太平洋津波の高さの「巨大」「高い」がこれに当たります。
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

境界は[気象庁の高さ区分](https://www.jma.go.jp/jma/kishou/know/jishin/joho/tsunamiinfo.html)に対応します。

北西太平洋津波の高さは、コード1〜4が仕様の数の範囲（例 0.3〜1）です。
508「10m 超」は `{"lower": 10, "upper": null}` です。
511「不明」は `special` です。

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

範囲は CAMF Issue 1.2 の 18.4.35 節の表から書き起こしています。
表には `1.0-1.9` と `2.0-2.9`、`1km/h < v < 5km/h` と `6km/h < v < 11km/h` のように丸めた数で
書かれた範囲がありますが、すきまのない範囲の並びとして読みます。各範囲の上限は次の範囲の下限です。
単位の異なる表は1つにそろえ、視程はメートル、停電時間は分で表します。

D2 の地震係数は日本の震度の段階（5弱・5強など）なので、数値にせずコードで出力します。
残りの項目は数値ではない区分です。

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
| `source` | 電文にある時刻の部分。どの `status` でも必ずあります |

`precision` は、`status` が `valid` のときだけあります。

電文にない年や月、週は、次の時刻から補います。

| フィールド | 取り得る `status` | `source` | 補う元の時刻 |
|---|---|---|---|
| `report_time` | `valid` | 月・日・時・分 | `reception.at` |
| `occurrence_time`、`reference_time`、降灰の `activity_time` | `valid`、`undefined` | 日・時・分 | `report_time` |
| 火山の `activity_time` | `valid`、`special`、`undefined` | 日・時・分 | `report_time` |
| 津波と北西太平洋津波の `arrival` | `valid`、`special`、`undefined` | 日・時・分 | `report_time` |
| DCX の `onset` | `valid`、`special`、`undefined` | 週・週内分 | `reception.at` |

時刻でない値のときは、`status` が `special` で、意味は `labels` にあります。

| フィールド | `labels` |
|---|---|
| 津波の `arrival` | 「津波到達中と推測」、「該当情報なし」と、その英語 |
| 北西太平洋津波の `arrival` | `Arrived or Unknown` |
| 火山の `activity_time` | Du が 6・7 のときの Du の名前。例 `Approximate time (month)` |
| DCX の `onset` | `Not used`（A7 が 0） |

火山の日時の精度は、日時の曖昧さ（Du）で決まります。Du が 0〜3 なら `minute`、4 なら `hour`、5 なら `day` です。
火山には `activity_time_ambiguity` も必ず添えます。Du のコードオブジェクトで、表は `qzss.dcr.ambiguity_of_activity_time` です。
英語のラベルは DCR 仕様書の文言です。日本語の表はないので、`ja` はありません。

## Regions, Forecasts and Positions

繰り返し項目は1件ごとのオブジェクトです。
津波の `forecasts` の各要素は `region`・`arrival`・`height` を必須にします。
ほかの警報も、地域とその警報内容を一緒に持ちます。洪水の `warnings` の要素も `{region, warning}` です。

DCX の `target_regions` は地域のコードオブジェクトの配列です。
EX1 が 0 のときは、対象地域の指定がないので空の配列です。
EX9 は、EX8 によって都道府県か市町村かが変わります（[DCX-004](https://qzss.go.jp/en/technical/download/pdf/ps-is-qzss/is-qzss-dcx-004.pdf) 4.2.4.2）。
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

緯度経度は符号付きで、北緯と東経が正です。位置でないコードなら `status` は `undefined`、`value` は `null` です。
DCR の緯度経度は小数点以下9桁、DCX の楕円の中心は小数点以下6桁に丸めています。

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

軸長は km、座標・角度は度で、単位はキーの末尾に付けています。
角度は東を0、東から北へ正とする仕様の規約です。
航海用の北基準の方位角と混同しないでください（DCX-004 4.2.3.16 / 4.2.4.1.7）。

補正楕円の中心は、主楕円の中心に C1・C2 の小さな補正（最大で約0.0024度）を足すので、極や経度180度をわずかに越えることがあります。
避難方向の追加楕円は EX4 が東経45度起点なので、経度45〜225度です。災害中心は主楕円から±10度ずれるので、
緯度±100・経度±190です。方位は-90度以上90度未満です。

楕円の `source` は、その楕円を組み立てた伝送コードです。
どの仕様フィールドのコードかは、楕円の位置で決まります。`main_ellipse` は A12〜A16、
`specific_settings.refined_ellipse` は C1〜C4 と A16、`evacuation.ellipse` は EX3〜EX7 です。
補正楕円は A12〜A15 との組み合わせで値が決まるので、`main_ellipse` と一緒に出力します。

`specific_settings` は、A17 のコードオブジェクト `type` と、その種類のグループを1つ持ちます。

| A17 | グループ | 内容 |
|---|---|---|
| 0 | `refined_ellipse` | 補正楕円 |
| 1 | `hazard_centre` | 災害の中心。`source` は主楕円の中心からの相対コード（C5・C6） |
| 2 | `second_ellipse` | 主楕円から作る第二楕円。下の表のとおり |
| 3 | `hazard_details` | 災害別詳細 |

第二楕円は、主楕円を動かし、拡げ、回して作ります（CAMF Issue 1.2 の 3.7.3）。

| キー | CAMF | 形 | 単位 | `relative_to` | 意味 |
|---|---|---|---|---|---|
| `shift` | C7 | 数量 | `1` | `main_ellipse.semi_major_axis` | 第二楕円の中心を、主楕円の中心から半長軸に沿ってずらす距離。km は `value` × `main_ellipse.value.semi_major_axis_km` |
| `scale_factor` | C8 | 数量 | `1` | `main_ellipse` | 軸の長さの倍率。第二楕円の半長軸は `value` × `semi_major_axis_km`、半短軸は `value` × `semi_minor_axis_km` |
| `bearing` | C9 | 数量 | `deg` | `main_ellipse.azimuth` | 主楕円の方位からの回転角。第二楕円の方位は `main_ellipse.value.azimuth_deg` + `value`（東から北へ） |
| `instruction` | C10 | コード | | | 第二楕円の中にいる人への指示 |

第二楕円そのものの中心の緯度経度や、軸の長さは出力しません。

追加楕円には、避難方向を `evacuation.direction`（EX2 のコードオブジェクト）として添えます。

## Report Types and Field Mapping

DCR 共通：version → `version`、report_time → `report_time`、通報区分・情報形態 →
`report_classification`・`information_type`。災害分類は `type` にまとめます。
表のコードを持つ項目は、元の `*_raw`・`*_no` とそのコード表から作り、表示用の属性は `labels` にまとめます。

| Python クラス / type の末尾 | data の固有項目 |
|---|---|
| EarthquakeEarlyWarning / earthquake_early_warning | occurrence_time、depth、magnitude、epicenter、intensity_lower/upper、long_period_ground_motion_lower/upper、target_regions、notifications |
| Hypocenter / hypocenter | occurrence_time、depth、magnitude、epicenter、position、notifications |
| SeismicIntensity / seismic_intensity | occurrence_time、observations[{region,intensity}] |
| NankaiTroughEarthquake / nankai_trough_earthquake | information_serial、page{number,total,content_hex} |
| Tsunami / tsunami | warning、notifications、forecasts[{region,height,arrival}] |
| NorthwestPacificTsunami / northwest_pacific_tsunami | tsunamigenic_potential、forecasts[{region,height,arrival}] |
| Volcano / volcano | volcano、warning、activity_time、activity_time_ambiguity、target_regions |
| AshFall / ash_fall | volcano、warning_type、activity_time、forecasts[{region,elapsed_time,warning}] |
| Weather / weather | warning_state、warnings[{region,warning}] |
| Flood / flood | warnings[{region,warning}] |
| Typhoon / typhoon | reference_time、reference_time_type、elapsed_time、number、scale_category、intensity_category、position、central_pressure、maximum_wind_speed、maximum_gust_wind_speed |
| Marine / marine | warnings[{region,warning}] |

長周期地震動の上下限は、コード0「該当情報なし」でも `special` のコードオブジェクトとして出力します。

DCR の `version` は `{"status": …, "value": …}` です。仕様の定める1なら `valid`、それ以外は `undefined` です。

DCX 警報共通：Vn → `version`、A1 → `message_type`、A2 → `country`、A3 → `provider`、A4 → `hazard`、
A5 → `severity`、A6・A7 → `onset`、A8 → `duration`、A9・A10・A11 → `instruction`。
A4 は `hazard` の `type`・`category`・`definition` の3つのコードオブジェクトにします。
1つの A4 のコードを、種類・区分・説明の3つの表で引いたものです。`code` はどれも同じです。

DCX の `version` も同じ形です。L-Alert、J-Alert、市町村からの情報は、仕様の定める1なら `valid`、それ以外は `undefined` です。
2026年9月の実際の放送では、J-Alert と市町村からの情報が0を送っていて、`undefined` になります。
国外からの情報は、どの値でも `valid` です。
種類のわからない DCX は、どの値でも `undefined` です。

| Python クラス / type の末尾 | 警報共通項目以外の項目 |
|---|---|
| NullMsg / null | data={}。警報共通項目も出しません |
| OutsideJapan / outside_japan | main_ellipse、適用される specific_settings |
| LAlert / l_alert | main_ellipse または target_regions の一方、適用される specific_settings |
| JAlert / j_alert | target_regions。楕円と specific_settings はありません |
| MTInfo / mt_info | main_ellipse、target_regions、適用される specific_settings と evacuation |
| Unknown / unknown | デコーダーが解釈した共通項目・main_ellipse・specific_settings |

| DCX の元のフィールド | 出力先 |
|---|---|
| A12〜A16 | main_ellipse |
| A17、C1〜C4 | specific_settings.refined_ellipse |
| A17、C5〜C6 | specific_settings.hazard_centre |
| A17、C7〜C10 | specific_settings.second_ellipse |
| A17、D1〜D36 | specific_settings.hazard_details。元の属性名から d番号の接頭辞を除いた項目名。数値を表す12項目は数量、ほかはコード |
| EX1 | target_regions |
| EX2〜EX7 | evacuation |
| EX8〜EX9 | target_regions |
| SDMT・SDM（衛星指定マスク）、EX10（予備）、種類ごとに使われない拡張領域 | 出力しません。元のビット列は `reception.nmea` にあります |

レポートの属性：timestamp → `reception.at`、satellite_prn → `reception.satellite`、nmea → `reception.nmea`、
raw → `message_id`、`get_texts()` → `texts`。

## Corrections, Cancellations and All Clears

訂正や取消の報には、どの報を訂正・取り消したのかを示す項目がありません。
DCX の L-Alert、J-Alert、市町村からの情報と、南海トラフ地震に関連する情報は、`series.key` で元の報と対応づけられます。
ほかの報は、報の種類・地域・時刻などの内容で対応づけてください。

報を取り消すことと、警報そのものが終わることは別のものです。

| 意味 | 報 | どこで読むか |
|---|---|---|
| 報の取消 | DCR | `series.lifecycle` が `cancellation`（情報形態 2） |
| 危険の終わり | DCX | `series.lifecycle` が `all_clear`（A1 3） |
| 警報の解除（警報すべて） | 気象 | `data.warning_state` のコード 2 解除 |
| 警報の解除 | 津波 | `data.warning` のコード 2 警報解除 |
| 警報の解除（地域ごと） | 洪水 | `data.warnings[].warning` のコード 1 警報解除 |
| 警報の解除（地域ごと） | 海上 | `data.warnings[].warning` のコード 0 海上警報解除 |

## Nankai Trough Pages

`page` は1ページ分です。UTF-8 の文字がページ境界で切れるので、本文は `content_hex` に保持します。
同じ発表のページは、`series.key` でまとめられます。
`texts.ja` は、変換した時点の共有の組み立て状態から作ります。同じページでも、後で変換し直すと文章が変わることがあります。

## Validation and Versioning

`$id` は `urn:azarashi:report:2` です。外部スキーマの参照はありません。
スキーマは形を検証します。下限≦上限のような項目間の関係と、コードと名前の一致は検証しません。名前はコード表と照らせば確かめられます。
JSON Schema の format 検証を有効にしてください。

同じ版の中で、キーとレポートの種類を足すことがあります。読む側は、知らないキーと知らない `type` を無視してください。
スキーマも、知らないキーと、`qzss.dcr.tsunami` と同じ形の知らない `type` を受け付けます。

既存のキーの意味・形・単位を変えるとき、既存のキーに新しい値（`status` や `lifecycle` の種類など）を足すとき、
キーを消すときは、別の版にします。コード表に新しいコードが加わるのと、表示の文言の修正は、このどれにも当たりません。
Galileo EWS に対応するときは、v3 にします。v2 の `reception.satellite.system` は `qzss` だけです。

`schema_version` は整数で、azarashi 自身のバージョンとは独立です。

`reception.nmea` は、QZSS の報では必ずあります。この版の全18種類は QZSS の報です。

## Examples and Tests

スキーマは配布パッケージの `azarashi/json/schemas/report-v2.schema.json` に含まれ、`json_schema()` で取得できます。
公開する名前は `azarashi` から取れる5つだけで、`azarashi.json` の中の内部名は互換性の対象ではありません。
スキーマ、例、docs のコード表のファイルを作り直すコードは `tests/examples/` にあります。

```shell
pip install -e . pytest 'jsonschema[format]'
PYTHONPATH=.:tests python -m examples.generate
python -m pytest tests/test_json_schema.py
```

JSON への変換ではスキーマによる検証を行いません。必要な場合は `json_schema()` でスキーマを取得し、検証ライブラリに渡してください。
