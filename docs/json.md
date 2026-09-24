[azarashi](../README.md) / JSON

# JSON Output v1

`to_json_dict()` と `to_ndjson()`、CLI の `--json` が出力する JSON の形式と、各項目の意味を説明します。
既存の Python API やレポートの動作は変わりません。

- [JSON Schema](../azarashi/json/schemas/report-v1.schema.json)：Draft 2020-12、全18種類
- [整形した完全な出力例](json/report-v1.examples.pretty.json)
- [同じ内容の NDJSON](json/report-v1.examples.ndjson)

例は既存のログと合成したテストメッセージをデコードしたものです。受信日時は検証用の固定値です。
スキーマは JSON の構造を定義します。各項目の意味は、Azarashi が対応する DCR/DCX の仕様とコード表に従います。
コードの意味はコード表から取得し、仕様上の区分をそのまま出力します。

## API

```python
import sys
import azarashi

report = azarashi.decode(sentence, 'nmea')
record = azarashi.to_json_dict(report)
sys.stdout.write(azarashi.to_ndjson(report))
schema = azarashi.json_schema()
```

`to_json_dict(report)` は独立した辞書を返します。戻り値を変更してもレポートや次の出力に影響しません。
`to_ndjson(report)` は末尾の改行を含む1件分の文字列です。`print()` を使う場合は `end=''` を指定します。
`json_schema()` はパッケージに同梱されたスキーマを辞書として返します。呼び出すたびに新しい辞書を返します。
辞書の戻り値の型は `dict[str, JsonValue]` です。`JsonValue` は JSON で表せる値の型で、`azarashi` からインポートできます。

全18種類のレポートとそのサブクラスに対応しています。サブクラスも基底クラスと同じ形式で出力し、追加した属性は含めません。
レポートでないものを渡すと `AzarashiArgumentTypeError` になります。これは `TypeError` の一種です。
azarashi がデコードしたレポートは、必ず JSON にできます。コンストラクタで生成したレポートも、
各フィールドで定められた型と意味に合う値を渡していれば JSON にできます。日時はタイムゾーンが
なくても受け付けます。NaN や無限大、要素数のそろわない予報の配列などを渡したり、あとから属性を
書き換えて設定したりすると、変換が失敗します。azarashi はこれらの値を確かめません。
コードに対応する表示名はコード表から取得するため、レポートの表示用属性だけを変更しても `data` 内の `labels` には反映されません。
`text` には `str(report)` の結果をそのまま出力します。

## CLI

```shell
azarashi nmea --input messages.log --json > reports.ndjson
azarashi ublox --input /dev/ttyUSB0 --json --unique
```

標準出力には1行に1件の JSON を出力し、レポートごとに出力バッファをフラッシュします。エラーや入力の終わり（EOF）を知らせるメッセージは標準エラー出力に書き込みます。
JSON にできないレポートがあっても読み取りは止めません。その電文を標準エラー出力に記録して読み飛ばし、次の電文へ進みます。
標準出力には、変換が終わったレポートだけを1行単位で書き込みます。途中まで変換した内容は出力しません。
入力・記録・重複除外・DCR/DCX の除外・受信日時指定は通常表示と同じです。
`--source` または `--verbose` と `--json` の併用は引数エラーです。

## Record

| 必須キー | 内容 |
|---|---|
| `schema_version` | JSON 出力形式のバージョン。整数 `1` |
| `type` | `qzss.dcr.tsunami` などの固定識別子 |
| `received_at` | UTC の受信日時。末尾は `Z` |
| `satellite` | `{ "system": "qzss", "prn": 186 }`、不明なら `null` |
| `nmea` | ライブラリが生成した QZQSM 文。行末改行なし |
| `text` | 変換時点の `str(report)` |
| `data` | 種類ごとに定めた内容 |

受信日時と警報に記載された日時は別です。
衛星番号が不明な入力から NMEA を生成するときは、既定値の55が入ります。
そのため、受信した衛星を確認するときは NMEA 内の番号ではなく `satellite` を参照してください。

`text` は `print(report)` の本文です。print が追加する末尾改行、CLI の時刻や区切り線は含めません。
文章中の改行はエスケープされ、NDJSON は UTF-8・1行1オブジェクトです。
表示用の文章ではなく、`type` と `data` を機械的な判断に使います。

`camf` オブジェクトや Python の `ignore_*` フィールドは出力に含めません。内部情報を追加する診断モードもありません。
元のメッセージは必須項目の `nmea` で確認できます。入力フレームをそのまま保存するには記録機能を、
レポートの属性を調べるには Python API を使ってください。情報の識別に必要なコードは JSON に含めます。

## Key Names

`data` のキーは JSON のための名前です。Python の属性名とは別に決めています。
どの属性がどのキーになるかは、下の「Report Types and Field Mapping」の表にまとめています。
名前は次の規則で付けます。

- 種別から明らかな語は省きます。例：緊急地震速報の `depth` は震源の深さです。
- 意味を持つ語は省きません。例：台風の `maximum_wind_speed` は最大風速です。
- 同じキーは、どの種別でも同じ意味です。例：対象地域の一覧は、DCR でも DCX でも `target_regions` です。
- つづりは、その名前の元の仕様に従います。キーのほか、type の名前と status などの列挙値も同じです。
  DCR から来た名前は米国式です。例：`epicenter`、`qzss.dcr.hypocenter`。
  CAMF から来た名前は英国式です。例：`centre`、`hazard_centre`。
  どちらにも共通の名前は米国式です。例：`recognized`、`unrecognized_code`。
- ただの数値は、単位をキーの末尾に付けます。例：`semi_major_axis_km`、`latitude_deg`。
  数量オブジェクトは、単位を `unit` に入れます。
- `code` は、コードオブジェクトとその中のコード値にだけ使います。

scheme はコード表の名前をそのまま使います。

## Codes and Labels

```json
{
  "scheme": "qzss.dcr.tsunami_forecast_region",
  "code": "610",
  "recognized": true,
  "labels": {"ja": "高知県"}
}
```

コードオブジェクトは4項目を必須とします。
`scheme` と `code` を合わせて識別します。code は非負整数の十進文字列（不要な先頭ゼロなし）です。
JIS などの外部のコード体系と同じであることを確認していないものは、別の体系として扱います。

`scheme` の先頭は、その表を索くフィールドを定めている仕様です。CAMF のフィールドの表は
`camf.` で始まり、伝送路によらず同じ意味です。A1〜A11、C10、D1〜D36 が該当します。
値を各国が割り当てる A3 と国別ライブラリも、CAMF が国ごとの体系として定めているので `camf.` です。
サービスが CAMF に足したフィールドの表は、そのサービスの名前で始まります。DCX では EX1 の
`qzss.dcx.area_code` と EX9 の `qzss.dcx.prefecture_bit` の2つ、気象庁の DCR は `qzss.dcr.` です。
どの伝送路で受信したかは `type` と `satellite` が示すので、`camf.` の scheme からその情報は失われません。

`recognized` は既存のコード表で意味が定義されているかを表し、本番／試験や信頼度を表しません。
定義済みの「不明」は true、未定義コードは false です。
未定義コードも code を保持し、labels は空オブジェクトにします。
未定義コードの代わりに表示する「コード番号：…」は名称ではないため含めません。
定義済みでも表示文字列がない場合は、`labels` は空オブジェクトになります。
`labels` の値が空文字列になることはありません。スキーマも空文字列を拒否します。
日本語・英語がある場合だけ `ja`・`en` を出します。変換のときに翻訳を足すことはしません。
DCR の英語は、気象庁の多言語辞書や気象庁のページ、DCR 仕様書の英語から取っています。
気象庁が英語を出していないものは、azarashi の訳です。英語の利用者にも危険が伝わるように付けています。
気象庁の公式の英語が出たら、それに置き換えます。英訳の方針と、azarashi の訳の一覧は [English Translation Policy](english-translation-policy.md) にあります。
防災事項の文のうち azarashi の訳は、末尾に `(Translated by azarashi)` と付けています。文がどこに表示されても、印が一緒に付いていくようにするためです。
この印がない英語が、気象庁の英語だとは限りません。
訳は、日本語より弱い伝え方にならないようにしています。それでも、意味の正は常に日本語の `ja` です。

提供者の scheme は `camf.provider.country_N` とし、国が違えば別体系になります。
CAMF Issue 1.2 の 3.1.3 は、提供者の識別子を「その国の中で一意」とし、一覧を国・地域ごとに
用意するものと定めています。どの伝送路が運んでも同じ国の同じ番号は同じ提供者です。

指示の scheme は、どのライブラリを指すかで変わります。国際ライブラリ（A9=0）は
`camf.instruction.library_0.version_V` です。国に依存しない1つの表なので、国は含めません。
国別ライブラリ（A9=1）は `camf.instruction.country_N.library_1.version_V` です。
3.5.1 が国別ライブラリを「その国のもの」と定めているので、伝送路の名前は含めません。
N・L・V は伝送されたコード値です。指示オブジェクトにはライブラリと版を保持します。国は `country` です。
未知のライブラリ版でも指示コードを落としません。

## Quantities

深さや高さなどの数量は、次の形式で出力します。元のコード情報は `code` に含めます。

| `kind` | 必須の値 | 意味 |
|---|---|---|
| `scalar` | `value`, `unit` | 仕様が示す単一の数値。物理的な厳密値という意味ではない |
| `bounds` | `lower`, `upper`, `unit` | 仕様上の範囲・片側境界 |
| `category` | コードのみ | 定性的な区分、数値境界を付けない区分 |
| `missing` | `reason` | `unknown`, `no_information`, `unrecognized_code` |

上下限は `{ "value": 500, "inclusive": false }` のように表します。下限または上限がない場合、その側を `null` にします。
`bounds` では少なくとも片方の値が必要です。`unit` は項目ごとに決まっており、スキーマで検証します。
単位のないマグニチュードでは `unit` は `null` です。
「不明だが8.0超」のマグニチュードは境界を保持し、`qualifier: "unknown_value"` を付けます。

### Tsunami Height

国内津波の表示区分と範囲は次のとおりです。「3m」は1m超〜3m以下の範囲として出力します。

| コード | 表示 | JSON の内容 |
|---|---|---|
| 1 | 0.2m未満 | 上限0.2、含まない |
| 2 | 1m | 下限0.2を含み、上限1を含む |
| 3 | 3m | 下限1を含まず、上限3を含む |
| 4 | 5m | 下限3を含まず、上限5を含む |
| 5 | 10m | 下限5を含まず、上限10を含む |
| 6 | 10m超 | 下限10、含まない |
| 13 / 14 | 該当情報なし / 不明 | missing |
| 15 | その他の津波の高さ | category |

境界は[気象庁の高さ区分](https://www.jma.go.jp/jma/kishou/know/jishin/joho/tsunamiinfo.html)に対応します。
北西太平洋津波のコード1〜4は既存実装の範囲表示を category の labels に保持します。
国内の境界規則を流用しません。508は10m超、509・510は定性的区分、511は不明です。
未定義コードは両形式とも保持します。

その他、深さ・マグニチュード・気圧・風速・経過時間は既存コード表の数値と特殊値に従います。
震度・警報・DCXの災害別区分はコードオブジェクトであり、区分番号を物理量として扱いません。
CAMF の災害別詳細（D1〜D36）のうち、数値や数値の範囲を表す12項目も同じ形で出力します。

| 項目 | kind | 単位 |
|---|---|---|
| D1 マグニチュード | `bounds` | なし |
| D3 主楕円中心から震央への方位 | `scalar` | `deg` |
| D4 主楕円中心から震央への距離 | `scalar` | `semi_major_axis`（主楕円の半長軸を1とする倍率） |
| D5 波の高さ | `bounds` | `m` |
| D6 気温 | `bounds` | `degC` |
| D8 風速 | `bounds` | `km/h` |
| D9 降水量 | `bounds` | `mm/h` |
| D13 視程 | `bounds` | `m` |
| D14 積雪深 | `bounds` | `cm` |
| D26 10万人あたりの患者数 | `bounds` | なし |
| D27 騒音 | `bounds` | `dB` |
| D29 停電の見込み時間 | `bounds` | `min` |

範囲は CAMF Issue 1.2 の 18.4.35 節の表から書き起こしています。表示文字列から読み取ってはいません。
表には `1.0-1.9` と `2.0-2.9`、`1km/h < v < 5km/h` と `6km/h < v < 11km/h` のように丸めた数で
書かれた範囲がありますが、すきまのない範囲の並びとして読みます。各範囲の上限は次の範囲の下限です。
境界を表の文言が示しているときは文言に従います。D8 と D13 のように両側とも `<` で書かれて
文言が決めていない境界は、他の表の多くと同じく下側の範囲に含めます。5.9km/h も 6km/h も
ビューフォート1です。単位の異なる表は1つにそろえ、視程はメートル、停電時間は分で表します。

D2 の地震係数は日本の震度の段階（5弱・5強など）なので、数値にせずコードで出力します。
残りの項目は数値ではない区分です。

どのフィールドがどの `kind` と `reason` を取り得るかは、フィールドごとにスキーマで絞ってあります。
津波の高さは `bounds`・`category`・`missing` だけで、`scalar` にはなりません。
`qualifier` を付けられるのは震源のマグニチュードだけです。

「500km超」だけから600km超かどうかは決まりません。
missing や category も含め、判断不能を false と同一視しないでください。

## Time

警報内の時刻は `status`, `value`, `basis` を持ちます。
通常は status=time、value は UTC 日時、basis は `received_at` または `report_time` です。
`basis` は、電文に含まれない年・月・日などを補う際に使った基準日時を示します。

時刻が得られない場合は `value` と `basis` を `null` にし、`status` に次のいずれかを設定します。

| 状態 | 意味 |
|---|---|
| `arrival_estimated` | 国内津波の「津波到達中と推測」 |
| `arrived_or_unknown` | 北西太平洋津波の「到達済みまたは不明」。一方に決めない |
| `no_information` | 国内津波の「該当情報なし」 |
| `not_used` | DCX の時刻フィールドが未使用 |
| `unrecognized_code` | 日時に変換できないコード。source に元の時刻成分を保持 |

火山の日時には `activity_time_ambiguity` を必須で併記します。電文の日時の曖昧さのコード値で、整数です。
日時の精度・概数の解釈にはこのコードを使い、補完された日時を正確な観測日時だとみなしません。
台風の基点分類も `reference_time_type`、経過時間も `elapsed_time` として保持します。
状態はフィールドごとに絞ってあります。どのフィールドがどの状態を取り得るかはスキーマで検証するので、
利用者は「この組み合わせはありえない」を機械的に判断できます。

| フィールド | 取り得る status | `basis` | `source` |
|---|---|---|---|
| `report_time` | `time` のみ | `received_at` | なし |
| `occurrence_time`、`activity_time`、`reference_time` | `time`、`unrecognized_code` | `report_time` | 日・時・分 |
| 国内津波の `arrival` | 上記＋`arrival_estimated`、`no_information` | `report_time` | 日・時・分 |
| 北西太平洋津波の `arrival` | `time`、`arrived_or_unknown`、`unrecognized_code` | `report_time` | 日・時・分 |
| DCX の `onset` | `time`、`not_used`、`unrecognized_code` | `received_at` | 週・週内分 |

`report_time` は DCR の電文が必ず発表時刻を持つため `time` だけです。自分自身を基準にすることも
ありません。国内津波と北西太平洋津波は、相手側の状態を受け付けません。

## Regions, Forecasts and Positions

繰り返し項目は1件ごとのオブジェクトです。
地域・高さ・時刻の並列配列は作らず、津波の `forecasts` の各要素は region・arrival・height を必須にします。
他の警報も地域とその警報内容を一緒に持ちます。
Python レポートの対応する配列どうしで要素数が異なる場合は、変換時にエラーになります。

Jアラートの `target_regions` は地域コードオブジェクトの配列です。
都道府県の scheme は `qzss.dcx.prefecture_bit`、code は下位から0始まりのビット位置です。
市区町村等の scheme は `qzss.dcx.area_code`、code は16ビットの伝送コードです。
EX9の元の64ビット整数は出さず、元ビット列は nmea に保持します。
この違いは [DCX-004](https://qzss.go.jp/en/technical/download/pdf/ps-is-qzss/is-qzss-dcx-004.pdf) 4.2.4.2 に対応します。

DCR の位置は符号付きの緯度経度と度分秒の source を保持し、status で有効／未定義を区別します。
無効なら緯度経度は null です。source は元の分解能と未定義の組み合わせを保持します。
DCX の楕円は中心・半長軸・半短軸・角度・`source` を必須にします。
軸長はkm、座標・角度は度です。角度は東を0、東から北へ正とする仕様の規約です。
航海用の北基準の方位角と混同しません（DCX-004 4.2.3.16 / 4.2.4.1.7）。

数値の範囲もスキーマで検証します。範囲は楕円の種類ごとに違います。主楕円の中心は緯度±90・経度±180、
補正楕円は A12・A13 の刻みの 7/8 まで足せるため極や経度180度をわずかに越え得ます。
避難方向の追加楕円は EX4 が東経45度起点なので経度45〜225度、災害中心は主楕円から±10度ずれるため
緯度±100・経度±190です。軸長は正、方位は-90度以上90度未満です。

楕円の `source` は、その楕円を組み立てた伝送コードです。
キーは `centre_latitude`、`centre_longitude`、`semi_major_axis`、`semi_minor_axis`、`azimuth` です。
どの仕様フィールドのコードかは楕円の位置で決まります。`main_ellipse` は A12〜A16、
`refined_ellipse` は C1〜C4 と A16、`evacuation.ellipse` は EX3〜EX7 です。
補正楕円は A12〜A15 との組み合わせで値が決まるため、`main_ellipse` と併せて出力します。
km や度への換算式を逆算しなくても、伝送された値を取り出せます。

補正楕円・災害中心・相対的な第二楕円・災害別詳細は `specific_settings` の kind で分けます。
元の楕円と補正楕円は別々の項目に出力します。相対距離や相対角度も、そのままの値で出力します。
災害中心の `source` は主楕円の中心からの相対コード（C5・C6）です。
第二楕円の `source` は移動方向・拡大率・方位のコード（C7〜C9）です。
追加楕円には避難方向を `evacuation.direction` として併記します。

対象外のグループは省略し、グループが存在するときに必要な構成要素は必須です。
0・false を省略しません。受信衛星が不明なら null、適用される配列に要素がなければ空配列です。
EEW の長周期地震動コード0は未使用なので、該当する上下限を省略します。

## Report Types and Field Mapping

DCR共通：version → version、report_time → report_time、報告区分・情報区分のコードと日英名 →
report_classification / information_type。災害分類の名前・コードは type に集約します。
表のコード付き項目は元の `*_raw` / `*_no` とそのコード表から作り、対応する表示属性は labels に集約します。
同じ値の表示を別キーに重ねません。

| Pythonクラス / typeの末尾 | JSON data の固有項目（元の内容） |
|---|---|
| EarthquakeEarlyWarning / earthquake_early_warning | occurrence_time、depth、magnitude、epicenter、intensity_lower/upper、long_period_ground_motion_lower/upper、assumptive、target_regions、notifications |
| Hypocenter / hypocenter | occurrence_time、depth、magnitude、epicenter、position、notifications |
| SeismicIntensity / seismic_intensity | occurrence_time、observations[{region,intensity}] |
| NankaiTroughEarthquake / nankai_trough_earthquake | information_serial、page{number,total,content_hex} |
| Tsunami / tsunami | warning、notifications、forecasts[{region,height,arrival}] |
| NorthwestPacificTsunami / northwest_pacific_tsunami | tsunamigenic_potential、forecasts[{region,height,arrival}] |
| Volcano / volcano | volcano、warning、activity_time、activity_time_ambiguity、target_regions |
| AshFall / ash_fall | volcano、warning_type、activity_time、forecasts[{region,elapsed_time,warning}] |
| Weather / weather | warning_state、warnings[{region,warning}] |
| Flood / flood | warnings[{region,level}] |
| Typhoon / typhoon | reference_time、reference_time_type、elapsed_time、number、scale_category、intensity_category、position、central_pressure、maximum_wind_speed、maximum_gust_wind_speed |
| Marine / marine | warnings[{region,warning}] |

これらの type は `qzss.dcr.` で始まります。

DCX 警報共通：vn → version、A1 → message_type、A2 → country、A3 → provider、A4 → hazard、
A5 → severity、A6/A7 → onset、A8 → duration、A9/A10/A11 → instruction。
A4 は hazard の `type`・`category`・`definition` の3つのコードオブジェクトにします。
1つの A4 のコードを、種類・区分・説明の3つの表で引いたものです。code はどれも同じです。

| Pythonクラス / typeの末尾 | 警報共通項目以外の項目 |
|---|---|
| NullMsg / null | data={}。警報共通項目も出さない |
| OutsideJapan / outside_japan | main_ellipse、適用される specific_settings |
| LAlert / l_alert | main_ellipse または target_regions の一方、適用される specific_settings |
| JAlert / j_alert | target_regions。楕円・specific_settings は禁止 |
| MTInfo / mt_info | main_ellipse、target_regions、適用される specific_settings / evacuation |
| Unknown / unknown | デコーダーが解釈した共通項目・main_ellipse・specific_settings |

これらの type は `qzss.dcx.` で始まります。

| DCX元フィールド | 出力先 |
|---|---|
| A12〜A16 | main_ellipse |
| A17、C1〜C4 | specific_settings.refined_ellipse |
| A17、C5〜C6 | specific_settings.hazard_centre |
| A17、C7〜C10 | specific_settings.second_ellipse |
| A17、D1〜D36 | specific_settings.hazard_details。元の属性名から d番号の接頭辞を除いた項目名。数値を表す12項目は数量、他はコード |
| EX1 | target_regions |
| EX2〜EX7 | evacuation |
| EX8〜EX9 | target_regions |
| SDMT/SDM、A18、EX10、適用されない拡張領域 | 通常出力に展開しない。nmea に保持 |

このスキーマは、現在のデコーダーが返す情報を JSON で表すための仕様です。未対応の海外固有領域などを JSON 変換時に新たに解読することはありません。
仕様上の運用制約と、現在のデコーダーが受け入れるビットパターンは別です。
デコーダーが受け入れた情報は、JSON 変換時にも出力に含めます。

共通の入力属性：timestamp → received_at、satellite_prn → satellite、nmea → nmea、str(report) → text。
sentence/message/raw/message_header/preamble、別体系の satellite_id/svid は別途出しません。
元入力が必要なら記録機能を使います。計算プロパティと任意の追加属性は自動的に出しません。

## Nankai Trough Pages

page は1ページ分です。UTF-8の文字がページ境界で切れるため、本文は content_hex に保持します。
ページ番号が未定義の場合も番号を落としません。
text は変換時点の共有組み立て状態を反映します。同じページでも後で再変換すれば文章は変わり得ます。
出力済みの JSON は変わりません。`text` には他のページの内容も含まれるため、`data` 内の1ページ分の情報だけでは再現できない場合があります。

## Validation and Versioning

`$id` は `urn:azarashi:report:1`。取得URLではなく識別子です。外部スキーマ参照はありません。
レポートの種類、必須項目の有無、未定義のキーがないこと、数量の形式と単位、グループ内の項目が揃っていることを検証します。
コード表の全文、CRC、コードと名称の一致、すべての条件付き項目の適用条件はスキーマに再実装しません。
下限≦上限、短軸≦長軸、ページ番号≦総ページ数のような項目間の関係も、JSON Schema では表現できません。
これらは変換処理のテストで担保しています。
それらはデコーダーと変換処理のテストで検証します。B4 の災害分類に応じた項目の選択も、変換処理で行います。
JSON Schema の format 検証を有効にしてください。NaN・無限大は JSON として出力しません。

v1 の構造は固定し、未定義の項目は拒否します。フィールド・種類の追加を含む構造変更は別の版にします。
表示文言の修正は構造変更ではありません。コード体系・意味・単位の変更は互換性の検討対象です。
正式リリース前は、レビュー結果に応じてこの仕様を変更することがあります。

`schema_version` は整数です。未定義の項目を拒否する以上、「構造を変えたが既存の検査器で通る」
という変更が存在しないので、`1.2` のような副番号に割り当てる意味がありません。
文言修正ではこの値は動かず、azarashi 自身のバージョンとも独立です。

封筒の構造は `$defs/envelope` の1か所で定義し、各レポート種別がそれを参照して `type` と `data` を
絞り込みます。`nmea` は種別ごとに必須とします。この版の全18種別は QZSS DCR/DCX なので、
実際にはすべての記録で必須です。QZQSM 文を持たない伝送路が加わる場合は、その種別で必須にしません。

## Examples and Tests

スキーマは配布パッケージの `azarashi/json/schemas/report-v1.schema.json` に含まれ、
`json_schema()` で取得できます。公開する名前は `azarashi` から取れる4つだけで、
`azarashi.json.model` の内部名は互換性の対象ではありません。
例の再生成コードは `tests/examples/` にあります。
例の生成にコード表を使い、既存の全レポート型・C/D分岐・特殊値を検証します。
コード表の仕様適合性を JSON テストだけで証明するものではありません。

```shell
pip install -e . pytest 'jsonschema[format]'
PYTHONPATH=.:tests python -m examples.generate
python -m pytest tests/test_json_schema.py
```

スキーマの検証ライブラリはテスト時に使うもので、azarashi の実行には不要です。
JSON への変換時にはスキーマによる検証を行いません。必要な場合は `json_schema()` でスキーマを取得し、検証ライブラリに渡してください。
