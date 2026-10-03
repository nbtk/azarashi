[azarashi](README.md) / Changelog

# Changelog

## 0.17.1 (unreleased)
### Highlights
0.17.1 gives the **JSON output its second version** (`"schema_version": 2`) and every report its
**text in every language it has**, through `get_text()` and `get_texts()`. Both change what 0.17.0
gave, and so does the text of the decoding errors, so read the Upgrade Notes if you use
`get_text_en()`, the JSON output, or the text of an error. Code that reads reports otherwise runs
unchanged.

**The JSON schema is still settling, and we welcome comments.** Please open an
[issue](https://github.com/nbtk/azarashi/issues) with anything that is hard to read, missing, or
not needed. A change that comes of them goes into a new version of the schema, v3. v2 itself
keeps its shape, as [Validation and Versioning](https://github.com/nbtk/azarashi/blob/main/docs/json.md#validation-and-versioning)
says.

### Upgrade Notes
#### Text of a report
- **`get_text_en()` is gone.** Use `get_text('en')`. As before, it returns `None` for a report
  without English, the Nankai Trough information.
- `get_text()` with no language returns the report in the language it is written in, always a
  string. `get_text('en', 'ja')` returns the first language the report has, or `None`.
  `get_texts()` returns every language as a dict keyed by language code, the report's own first.
- **The English of a DCX report leaves out the lines marked "(ja)".** `str(report)` still has
  them. `azarashi ... --english` shows the English the same way.

See [Reports](https://github.com/nbtk/azarashi/blob/main/docs/reports.md) for which report has
which language.

#### JSON v2
A program that reads v1 records has to be changed.

- **Top level**: `test` is `is_test`. `received_at`, `satellite` and `nmea` are now in `reception`,
  as `reception.at`, `reception.satellite` and `reception.nmea`. `text` and `text_en` are now
  `texts`, as `{"ja": "...", "en": "..."}`. `message_id` and `series` are new.
- **Code objects**: `scheme` is `table`, and `recognized` is `status`.
- **Quantities**: `kind` is gone; a quantity has `status` and either `value` or `range`. A range no
  longer has `inclusive`, and `qualifier` is gone. Units are UCUM.
- **`status`**: every value says whether it can be used as it is with one of `valid`, `assumed`,
  `special` and `undefined`.
- **Times**: `precision` is new, `basis` is gone, and `source` is always there.
- **Positions and ellipses** have `status` and `value`. The keys of a position's `source` are
  spelled out.
- **Table names**: `qzss.dcx.area_code` is `qzss.dcx.ex1_target_area_code`,
  `qzss.dcx.prefecture_bit` is `qzss.dcx.ex9_target_area_code_list`, `camf.provider.country_N` is
  `camf.a3_provider_identifier.country_N`, and `camf.instruction.…` is
  `camf.a11_instruction_library.…`.
- **EX9 prefecture codes are 1 (Hokkaido) to 47 (Okinawa)**, the same as the prefecture codes of
  the DCR, instead of bit positions 0 to 46. The same number now names the neighbouring
  prefecture: **a filter on `code` alone gives wrong prefectures until it is changed.**
- **DCX**
  - `version` is `{"status": ..., "value": ...}`.
  - `instruction.version` is `instruction.library_version`, and `instruction.identifier` is given
    for the international library only.
  - EX2 and A17 are code objects.
  - `target_regions` is an empty list when EX1 is 0.
  - The second ellipse is given as the C7 to C9 quantities and the C10 code, and the shift of its
    centre (C7) is now given too.
- **DCR**
  - The assumed hypocenter of an Earthquake Early Warning is `"status": "assumed"` on `depth` and
    `magnitude`, instead of `assumptive`.
  - A flood's `level` is `warning`.
  - The long-period ground motion limits are given for code 0 too.
- **Code tables** are new: `code_tables()`, and the same in
  [code-tables-v2.json](https://github.com/nbtk/azarashi/blob/main/docs/json/code-tables-v2.json).

See [JSON](https://github.com/nbtk/azarashi/blob/main/docs/json.md) for the whole format.

#### Codes with new names
These codes read differently in `str(report)`, in the report attributes and in the JSON.

| Code | 0.17.0 | 0.17.1 |
| --- | --- | --- |
| A11 code 0 of the Japanese library, in Japanese | empty | 指示なし (the DCX text now shows its "(ja)" line) |
| C10 code 0 | empty | No instruction |
| A3 code 0 of Japan, Australia, Fiji and Thailand | Undefined Provider Identifier of ... (Code: 0) | Not used |
| A4 code 0 | Undefined hazard type (Code: 0), and the like | Not used |
| Tsunami height code 13, in English | No information | No data |
| Tsunamigenic potential code 7 | There is a Possibility of a Tsunami | Other Tsunamigenic Potential |

The long-period ground motion limits of code 0 are named 該当情報なし / No data in the JSON. The
report attributes stay `None` for that code.

#### Text of a decoding error
A program that matches the text of an error has to be changed. The classes stay the same.

- **A message that is not DCR or DCX** reads
  `The Message is not DCR or DCX: expected Message Type 43 or 44, but got 47`, instead of
  `Undefined Message Type: 47`.
- **A wrong length, checksum or CRC** gives the expected and the actual value, as in
  `Too Short Sentence: expected 76 characters, but got 75` and
  `CRC Mismatch: expected 1510FF, but got 1510FC`. `Checksum Mismatch, should be 05` reads
  `Checksum Mismatch: expected 05, but got 00`, and a UBX frame that is not from QZSS or not of
  the L1S signal gives the expected ID the same way.
- **After `->`, an error found before the message is known to be DCR or DCX shows what was
  received**: the UBX frame, the datagram or the archive record as bytes, or the hex text. These
  errors are a CRC mismatch and a message that is not DCR or DCX. They showed a QZQSM sentence
  that azarashi had built, and `instance.nmea` held it; it is now empty.

### Added
- `get_text()` with any number of languages, and `get_texts()`.
- `code_tables()`, the code tables the JSON records name.
- Tests that hold azarashi to code written for 0.16.4: the examples of the 0.16.4 README, and every
  attribute and method its reports had.
- Tests that run every Python example in the documents and check that the help they show is what
  the commands print, so the documents keep up with the code.

### Fixed
- The Field Receiver example in the [API docs](https://github.com/nbtk/azarashi/blob/main/docs/api.md#field-receiver)
  now stops on SIGTERM while data keeps coming. Before, a receiver that kept sending kept it
  reading.
- The Minimal Loop example catches `AzarashiStopReading`, as its text says.
- The help of `--unique` spells suppress right.
- The documents say only what a reader needs, and no longer link to pages that are gone.
- A message type that IS-QZSS-L1S-009 defines, such as an augmentation message (MT 47 to 50), was
  called undefined ([#28](https://github.com/nbtk/azarashi/issues/28)).
- An error no longer shows a QZQSM sentence for a message that is not known to be DCR or DCX. The
  QZQSM sentence is defined for DCR and DCX messages only. The Upgrade Notes say what it shows now.
- The [API docs](https://github.com/nbtk/azarashi/blob/main/docs/api.md#decode) say that
  `decode()` gives a report for a DCR or DCX message only, and what `decode_stream()` skips.

Tested on Python 3.11 to 3.14.

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.17.0...v0.17.1

## 0.17.0 (2026-09-24)
### Highlights
0.17.0 follows **IS-QZSS-DCR-017**, whose DCR codes changed incompatibly, and adds **JSON output**,
an **English text** of every DCR report and reading of **L1S archives**. Code written for 0.16.x
keeps running: the earlier names of the exceptions and report classes still work, as listed under
Earlier Names. Some values and texts change, as listed under Upgrade Notes.

### Upgrade Notes
- **IS-QZSS-DCR-017.** Flood forecast regions, tsunami heights and other codes follow the new
  edition, which changed some of them incompatibly. A code azarashi does not know is kept and named,
  e.g. `深さ(コード番号：502)`, instead of failing the whole report.
- **Times are timezone-aware UTC.** Every `datetime` of a report is aware and in UTC. A time the
  message gives but that is not a time, such as February 30th, is `None`, with its fields kept in
  `*_raw`. A `timestamp` you pass without a zone is read as local time.
- **Exceptions are named for azarashi.** They form one hierarchy under `AzarashiException`, sorted
  by what to do next: `AzarashiReadOn` (read on), `AzarashiReopenStream` (reopen the stream),
  `AzarashiStopReading` (stop) and `AzarashiFixTheCall` (fix the call).
- **Report classes live by message format.** `azarashi.reports.dcr` (MT43), `azarashi.reports.dcx`
  (MT44) and `azarashi.reports.base`, e.g. `reports.dcr.Tsunami`.
- **DCX texts follow CAMF Issue 1.2** for A11 and A17, and a Japanese instruction code 0 reads
  `No instruction`. Target areas (EX1, EX9) are named in English as the DCR tables name them, e.g.
  `Uki City, Kumamoto Prefecture` instead of `Uki-shi, Kumamoto`.
- **Reports are made by `decode()` and `decode_stream()`.** Their constructors are no longer part
  of the compatible API; reading a report is.

### Earlier Names
The names of 0.16.x still work, so that code written for it runs unchanged.

| Earlier name | Current name |
| --- | --- |
| `QzssDcrDecoderException` | `AzarashiInvalidMessageError` |
| `QzssDcrDecoderNotImplementedError` | `AzarashiNotImplementedError` |
| `QzssDcReportJmaTsunami`, `QzssDcxJAlert`, ... (23 report classes) | `reports.dcr.Tsunami`, `reports.dcx.JAlert`, ... |

- The earlier report class names are found where 0.16.x had them,
  `azarashi.qzss_dc_report.QzssDcReportJmaTsunami`, and also as `azarashi.QzssDcReportJmaTsunami`.
  `azarashi.qzss_dc_report` gives the current modules `base`, `dcr` and `dcx` as well.
- Each earlier name is the current class itself, so `isinstance()` and `except` work with either.
- Two things differ. A mistake in the call is `AzarashiFixTheCall`, raised before anything is read,
  and `QzssDcrDecoderException` does not catch it: a reading loop that caught it would repeat a
  mistake that no read can put right. Logs and tracebacks show the current names.
- New code should use the current names. The earlier names may be deprecated in a later release.

See [Earlier Names](https://github.com/nbtk/azarashi/blob/main/docs/api.md#earlier-names) for the full list.

### Added
- **JSON output**: `to_json_dict()`, `to_ndjson()`, `json_schema()` and `azarashi ... --json`, one
  record per message, described by a JSON Schema (v1). See [JSON](https://github.com/nbtk/azarashi/blob/main/docs/json.md).
- **English text**: `report.get_text_en()`, `text_en` in the JSON and `azarashi ... --english`.
  The English of the DCR code tables comes from JMA wherever JMA gives it; see the
  [English Translation Policy](https://github.com/nbtk/azarashi/blob/main/docs/english-translation-policy.md).
- **L1S archives**: `azarashi l1s -f Q002_20260917.l1s` and `decode_stream(stream, 'l1s')`, with the
  satellite and the reception time of every record taken from the archive.
- **Recording and replay**: `azarashi ... --record FILE`, and `--time` to replay with the time the
  input was received.
- **Streams**: read timeouts (`AzarashiTimeoutError`), USB reconnection (`AzarashiReopenStream`),
  `reset_reading_state()`, and `unique=` counting a report as seen once it is delivered.
- **Type hints** (`py.typed`), checked with mypy and Pyright in strict mode.
- **Documentation** in `docs/`, with every report class and field listed.

### Fixed
- A Nankai Trough announcement is assembled per announcement, from pages that may arrive out of
  order and from several satellites.
- The DCX hazard onset follows the spec's time of week; a volcano's activity time follows its
  ambiguity.
- NMEA, hex and u-blox input that is malformed is reported as a message that cannot be decoded, and
  the stream reads on.

Tested on Python 3.11 to 3.14.

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.16.4...v0.17.0

## 0.16.4 (2026-06-30)
### Recommended Upgrade
This release fixes a regression in 0.16.3 that produced incorrect output for DCX J-Alert
messages. If you installed 0.16.3, please upgrade.

#### Fixed
- **DCX J-Alert prefecture list (regression in 0.16.3).** The EX9 target-area
  bitmask lost the 17-bit shift that aligns the 47-bit prefecture code, so
  `report.ex9_target_area_list` / `ex9_target_area_list_ja` decoded the wrong
  prefectures. The correct decoding is restored.

#### Changed
- **Refined ellipse (B1/B2) computed at full precision.** The refined centre
  and axes (C1–C6) are now derived from the full-precision grid values and
  rounded once at the end, instead of from the already-rounded A12–A15 display
  values. This follows the spec's "round the calculation result" rule and
  removes intermediate-rounding error (up to 1×10⁻⁶ deg on the refined centre).
  Display precision is unchanged: 10⁻⁶ deg for latitude/longitude, 10⁻⁵ deg for
  angles, 1 m for distances.

#### Added
- A decoding test suite covering DCR, DCX (L-Alert / J-Alert), the refined
  ellipse values, and `decode_stream` deduplication.

#### Note
0.16.4 supersedes the withdrawn 0.16.3 and carries forward its changes
(`unique=<seconds>` duplicate-expiry option, hashable reports, and assorted
fixes/cleanups). Existing code keeps working unchanged.

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.16.3...v0.16.4

## 0.16.3 (2026-06-21)
### New features
- **`decode_stream`'s `unique` now accepts a number of seconds** — pass `unique=<seconds>` (int or float) to re-report a duplicate message that was last seen longer ago than that threshold. `unique=True` keeps suppressing duplicates indefinitely (**default behavior unchanged**), and `unique=False` disables deduplication. Useful when a still-active alert is re-broadcast later and you want it surfaced again.
- **Report objects are now hashable** — they can be used as `set` members or `dict` keys (added `__hash__` consistent with the existing `__eq__`).

### Bug fixes
- **DCX (J-Alert)**: fixed an operator-precedence bug in the EX9 prefecture target-area bitmask that could yield an incorrect prefecture list.
- **DCX (B4)**: fixed `d35` (infection type) and `d36` (typhoon category) being omitted from `str(report)` output.
- **DCX (B1)**: fixed the delta calculation for the refined semi-major/semi-minor axes of the main ellipse.
- **DCX**: aligned the display precision of latitude/longitude and azimuth fields with the spec's rounding rules.
- Fixed `__str__` on reports being able to return `None` (missing `return`).
- Fixed mutable default arguments (shared dict) in `decode_stream`, `Receiver.start`, and the message extractors.
- Fixed an error message that was never formatted (missing f-string prefix).
- `QzssDcReportBase` now honors the `raw` argument.

### Internal improvements (no behavior change)
- Decomposed the monolithic DCX `decode()` into per-phase methods for readability; centralized rounding/precision in the decoder; simplified NULL-message detection; moved the CAMF helper to module level; assorted idiom cleanups (type checks, etc.).

### Documentation
- Updated the README for IS-QZSS-DCX-004 and the current output format/precision.

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.16.2...v0.16.3

## 0.16.2 (2026-06-20)
### DCX: Updated to IS-QZSS-DCX-004

- Renamed fields to follow updated CAMF terminology:
  - `a9_selection_of_library` → `a9_type_of_library`
  - `a17_main_subject_for_specific_settings` → `a17_type_of_specific_settings`
  - `c10_guidance_library_for_second_ellipse` → `c10_instruction_library_for_second_ellipse`
- `a9_type_of_library` value changed: `'Country/region guidance library'` → `'Country/region library'`
- Improved coordinate precision: latitude/longitude rounded to 1e-6 degrees, distances to 1 m, azimuth to 1e-5 degrees

### Other

- Bumped `python_requires` to `>=3.11`

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.16.1...v0.16.2

## 0.16.1 (2026-06-05)
### What's Changed
* 誤字と思われるもの，コピペミスと思われるものをいくつか修正 by @A-vrice in https://github.com/nbtk/azarashi/pull/26

### New Contributors
* @A-vrice made their first contribution in https://github.com/nbtk/azarashi/pull/26

Thank you so much, @A-vrice!

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.16.0...v0.16.1

## 0.16.0 (2026-05-10)
### What's Changed
* Revision corresponding to IS-QZSS-DCR-016. pp. 93–94 by @nezumi-tech in https://github.com/nbtk/azarashi/pull/24
* Typo fix pointed out by @A-vrice

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.15.1...v0.16.0

## 0.15.1 (2025-12-06)
### What's Changed
* UBX-RXM-SFRBXのsvidと、L1SのPRNの対応関係を修正。 by @nezumi-tech in https://github.com/nbtk/azarashi/pull/22

Special thanks to @nezumi-tech!

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.15.0...v0.15.1

## 0.15.0 (2025-10-17)
### What's Changed
* NEO-M9NのUBX-RXM-SFRBXメッセージが正常にデコードされるよう修正 by @nezumi-tech in https://github.com/nbtk/azarashi/pull/18
* UBX-RXM-SFRBXから変換された$QZQSMのSatIDが仕様内になるよう修正 by @nezumi-tech in https://github.com/nbtk/azarashi/pull/19
* IS-QZSS-DCR-015 への対応 by @nezumi-tech in https://github.com/nbtk/azarashi/pull/21

### New Contributors
* @nezumi-tech made their first contribution in https://github.com/nbtk/azarashi/pull/18

This release is based on the many achievements of @nezumi-tech. I truly appreciate all the effort and contributions. Thank you so much!

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.12.0...v0.15.0

## 0.12.0 (2025-05-21)
### What's Changed
* 火山(DC=8)のActivity TimeをJSTで表示するように変更 by @9SQ in https://github.com/nbtk/azarashi/pull/14
* 台風(DC=12)のタイポを修正 intencity - > intensity https://github.com/nbtk/azarashi/commit/ce0811552b6af0584c0cce72745a514b0752d1f1
* IS-QZSS-DCX-003 と IS-QZSS-DCR-014 をサポート

### New Contributors
* @9SQ made their first contribution in https://github.com/nbtk/azarashi/pull/14
Super thanks!

**Full Changelog**: https://github.com/nbtk/azarashi/compare/v0.11.0...v0.12.0

## 0.11.0 (2024-12-09)
- 760dada17ee724253aeee8334d950174ab35f670
#13 の指摘を受けて修正。

- d6e572f3023fede85c5907a66780e97aabbedd3e
それに付随して変数名を変更した。
ex7_ellipse_azimuth -> ex7_additional_ellipse_azimuth
ex7_ellipse_azimuthを使用しているアプリケーションは修正が必要になる。
ごめんなちゃい。

- 128fc2b8433d5cfbf13b30936a062847127aa069
IS-QZSS-DCX-002 で追加されたメッセージを追加した。

## 0.10.3 (2024-08-03)
DCXメッセージ受信時の不具合の修正 #12 をマージした。
この修正によってazarashiはデコードされたDCXメッセージを適切なレポートクラスにセットして返す。

Special thanks to @dragonkomat

## 0.10.2 (2024-06-26)
後方互換性のために `azarashi.decode_stream()` メソッドに `ignore_dcr` と `ignore_dcx` オプションを追加した。
デフォルトでは `ignore_dcr=False`、`ignore_dcx=True` が設定され旧バージョンと同様にDCRのみを返し、DCXは破棄される。
`azarashi.decode_stream()` がDCXを返すためには `ignore_dcx=False` を設定する。

## 0.10.1 (2024-06-21)
DCXをサポートした。

## 0.9.1 (2024-02-11)
イシュー #10 #11 に暫定的な対処を行った。
当該メッセージを受信したときQzssDcrDecoderExceptionではなくQzssDcrDecoderNotImplementedErrorを送出する。

## 0.9.0 (2023-12-04)
- [IS-QZSS-DCR-011 をサポートした](https://github.com/nbtk/azarashi/commit/bd67efe84e1c5c19d38cafdf6a21474c55192305)
緊急地震速報に長周期地震動階級を追加した。
レポートオブジェクトに下記の4つのメンバ変数が追加された。
`report.long_period_ground_motion_lower_limit_raw`
`report.long_period_ground_motion_upper_limit_raw`
`report.long_period_ground_motion_lower_limit`
`report.long_period_ground_motion_upper_limit`
なお、長周期地震動階級が設定されていないとき、 `*_limit_raw` には 0 、`*_limit` には `None` が設定される。

- イシュー #8  を修正した

- イシュー #9 を修正した

## 0.8.0 (2023-08-25)
-  生値をレポートオブジェクトに突っ込む
受信したパケットのビットフィールドから抽出した生値をレポートオブジェクトに追加した。
ライブラリをフォークすることなく、ハンドラ内でやりたいことが完結できるようにするため。
 関連イシュー:  #7 生値をレポートオブジェクトに突っ込む

- タイポ修正
レポートオブジェクトのメンバ変数名occurrence_time_of_eathquakeにタイポがあったのでoccurrence_time_of_earthquakeに変更した。
使っている場合は置換してほしい。(ごめんなさい！)
影響を受ける災害クラスはQzssDcReportJmaEarthquakeEarlyWarning、QzssDcReportJmaHypocenterならびにQzssDcReportJmaSeismicIntensity。

## 0.7.4 (2023-06-23)
- [石神井川問題](https://github.com/nbtk/azarashi/issues/6) を修正した
ロバストネス原則を踏まえて設計を見直した。
Be conservative in what you do, be liberal in what you accept from others.
- [README.md](https://github.com/nbtk/azarashi#tips) に Tips を追加した
フィードバックを反映した。
- リファクタリングした

## 0.7.3 (2023-03-15)
- hexメッセージタイプをCLIで処理するときにAttributeErrorが出る問題を修正しました。ところで、hexいらないんじゃないかなとおもう今日このごろ。

## 0.7.2 (2023-03-15)
- pySerialに対応しました。必須ではないので依存関係を張っていません。pySerialを使いたいときは自分でインストールしてください。
- DCRメッセージをUDPパケットにのせて配信する transmitter / receiver を実装しました。
- 細かな修正を行いました。

## 0.7.1 (2023-03-08)
- Ubloxのチップから受信したDCRメッセージをデコードしたときにもreportオブジェクトにNMEA QZQSMセンテンスを復元して出力するようにしました。
- hex形式のDCRメッセージをデコードしたときにもNMEA QZQSMセンテンスを出力しますが、hex形式は衛星IDをもたないため、QZQSMセンテンスの衛星IDは55固定です。
- 受信したDCRメッセージをUDPパケットに乗せてネットワークに再送するスクリプトを追加しました。詳細はREADME.mdを参照してください。
- decode_stream()のuniqueオプションで重複を判断するためのキャッシュのサイズを大きくし、キャッシュに有効期限を設けました。これにより、南海トラフ地震情報を重複して受信することを抑止します。
- 未実装のメッセージを受信した場合には、新たに定義した例外QzssDcrDecoderNotImplementedErrorを発生させるように変更しました。多くの運用シチュエーションでは、未実装エラーを無視したいためです。無視するときにはこの例外を握りつぶしてください。

## 0.7.0 (2023-02-22)
- 緊急地震速報メッセージに存在しない緯度経度フィールドをデコードして失敗する問題を修正しました。クソみたいなバグでした。ごめんなさい。
- その他、軽微な修正とリファクタリングを行いました。
- リリース0.7.0からPython 3.9以降をサポートします。Python 3.8以前を使用する場合は最新のリリース0.6.Xを使用してください。

## 0.6.10 (2023-02-22)
- 緊急地震速報メッセージに存在しない緯度経度フィールドをデコードして失敗する問題を修正しました。クソみたいなバグでした。ごめんなさい。
- Python 3.7の互換性を保持したブランチを作成しました。

## 0.6.8 (2022-11-07)
- 気象庁が仮定震源要素として緊急地震速報を発表した場合に、"De is 10: 深さ10km"、"Ma is 10: マグニチュード0.1"として発表する仕様に対応しました。
- 北西太平洋津波情報のとき ep == 0 になる仕様に対応しました。

## 0.6.7 (2022-06-22)
南海トラフ地震情報に対応しました。
IS-QZSS-DCR-010をサポートしています。

## 0.6.6 (2022-04-08)
インポートに失敗する問題を修正しました。ごめんなさい。もうだいじょうぶです。どんどんインポートしてください。
CLIとAPIにuniqueオプションを追加しました。とっても便利です。
CLIにデコード前のメッセージを表示するsourceオプションを追加しました。まぁまぁ便利です。
