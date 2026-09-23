[azarashi](README.md) / TODO

# TODO

2026-09-23 時点で開いている項目です。実装済みの一覧ではありません。
各項目に「なぜ」と「いつ着手するか」を書きます。着手条件が来ていないものは、来るまで触りません。

| # | 項目 | 状態 |
|---|---|---|
| 1 | A11 の公開フィールド名が日本を名指し | 2か国目のライブラリが現れたら |
| 2 | ライブラリ版 #2 以降 | 仕様が公開したら |
| 3 | EX1 と JIS X 0402 の一致確認 | 確認できるまで scheme は据え置き |
| 4 | 設定ミスが `AzarashiReadOn` に入る | 非互換を扱うときに再分類 |
| 5 | 弱参照できない読み取り元の明示的解放 | 具体的な要求が出たら |
| 6 | Galileo EWS 対応 | 実際に必要になったら |

## 1. A11 の公開フィールド名

`a11_japanese_library` と `a11_japanese_library_ja` は国名を含む公開フィールドで、
[docs/dcx.md](docs/dcx.md) にも載っています。2か国目のライブラリを足すとき、
デコーダは「どの国ならどの属性に入れるか」を知る必要があり、ここが成長の障害になります。

`definitions/` 側をマップにしても解決しません。障害は公開名のほうです。
2か国目が実際に現れたときに、`a11_country_library` のような名前へ変える破壊的変更として扱います。
それまでは変えません。一様性だけを理由に公開名を変えないためです。

ライブラリの選択規則は [a11_library.py](azarashi/definitions/camf/a11_library.py) の1か所にまとめ済みで、
デコーダと JSON 変換の両方がそこを使います。JSON の scheme は国別ライブラリも既に
`camf.instruction.country_N.library_1.version_V` なので、2か国目で変わるのはレポートの公開名だけです。

## 2. ライブラリ版 #2 以降

`a10_library_version` はコード0（#1）だけを持ち、他はコメントアウトされています。
`a11_library()` は `a10 != 0` で空を返し、レポートは版だけを報告して指示文を出しません。
仕様が版 #2 を公開したら、表に項目を足し、`a11_library()` に版を渡す形にします。

## 3. EX1 と JIS X 0402

[ex1_target_area_code.py](azarashi/definitions/qzss/dcx/ex1_target_area_code.py) の1,980件は
JIS X 0402 の市区町村コードと同じ形です（`1100` → 北海道札幌市、`13101` → 東京都千代田区）。
ただし全件の一致は確認していません。モジュールの先頭にもそう書いてあります。

確認できるまで scheme は `qzss.dcx.area_code` のままにします。
[docs/json.md](docs/json.md) の「確認していないものは別の体系として扱う」に従います。
確認できた場合も、外部の体系名を名乗るかは別途判断します。

## 4. 設定ミスが `AzarashiReadOn` に入る

`msg_type` の誤りや `readline()` のない入力は `AzarashiInvalidMessageError`、すなわち
`AzarashiReadOn` になります。入力を消費せず、同じ引数では解消しません。
[docs/api.md](docs/api.md) の Minimal Loop の形のまま、毎秒254万回空転することを実測しています。

旧例外での捕捉と互換性があるため今は維持し、[test_disconnect.py](tests/test_disconnect.py) が
「入力を読まずに再試行する」ことを固定しています。再分類は、他の非互換変更を扱うときに一緒に検討します。

## 5. 弱参照できない読み取り元の明示的解放

弱参照できず `closed` も公開しないストリームや callable は、`StreamKeyedDict` が強参照で保持し、
自動では解放されません。`reset_reading_state()` は抽出状態を捨てますが、管理情報の解放 API ではありません。
公開 API を増やす価値があるかは、具体的な要求が出てから判断します。

## 6. Galileo EWS

CAMF を運ぶ他のサービスが必要になった場合の準備は済んでいます。

- 封筒は `$defs/envelope` の1か所で、`nmea` は種別ごとに必須です。QZQSM 文を持たない種別では必須にしません。
- `satellite.system` は列挙です。
- CAMF のフィールドの表と scheme は、伝送路の名前を含みません。提供者と国別ライブラリも含めて `camf.*` です。

残るのは、`type` の値と `satellite.system` の項目を足すことです。

## 参考にしている仕様

リポジトリ直下に置いてあります（追跡対象外）。

- `EWSS-CAMF_in_force.pdf` — CAMF Issue 1.2（2026年3月）
- `is-qzss-dcx-004.pdf` — DCX。A11 は10ビット1つ（p31）で、CAMF の List A/B 表記とは異なります
- `is-qzss-dcr-017.pdf`、`is-qzss-l1s-009.pdf`

暗号化されており、空パスワードと `cryptography` で開きます。
