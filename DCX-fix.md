# DCX MT44 フィールド構造・実装指針メモ（EX拡充版）

## 1. 目的

この文書は、`IS-QZSS-DCX-003` に基づいて MT44 デコーダを実装し直すための、実装用の構造整理メモである。
主眼は、`Extended Message` を含めた **ビット配置、種別判定、フィールド責務、実装に必要な構造** を抜けなく固定することにある。
既存実装の `decodeDcx()` は `typebits` 前提で SD/CAMF/Extended Message を読んでおり、DCX-003 の MT44 構造と一致しないため、部分修正ではなく再実装が妥当である。

## 2. 実装方針

- 生ビット抽出層と意味解釈層を分離する。
- `MT44` は `PAB | MT | SD | CAMF | EX | Reserved | CRC` の固定構造として読み、独自の先頭 `typebits` は廃止する。
- サービス種別は `A2 Country/Region Name` と `A3 Provider Identifier` で判定する。
- `Extended Message` は 74bit 固定だが、L-Alert/local government、J-Alert、outside Japan で **完全に別構造** として扱う。
- Atarashi 側の変換テーブルは「コード値の意味付け」にのみ使い、ビット配置や variant 判定には使わない。

## 3. MT44 全体構造

DCX の MT44 は、`PAB(8) | MT(6) | SD(10) | CAMF(122) | Extended Message(74) | Reserved(6) | CRC(24)` の順で構成される。
受信機出力推奨形式では、250bit の DCX メッセージに `00` を追加して 252bit とし、16進 63文字で出力する。

### 3.1 絶対オフセット

| 領域             |  幅 | 絶対bit範囲 | 備考                    |
| ---------------- | --: | ----------- | ----------------------- |
| PAB              |   8 | 0..7        | プリアンブル。          |
| MT               |   6 | 8..13       | MT44 は `101100`。      |
| SD               |  10 | 14..23      | Satellite Designation。 |
| CAMF             | 122 | 24..145     | A1〜A18。               |
| Extended Message |  74 | 146..219    | 種別依存。              |
| Reserved         |   6 | 220..225    | 予約領域。              |
| CRC              |  24 | 226..249    | CRC24。                 |

## 4. SD

SD は `SDMT(1) + SDM(9)` で構成される。

| Field |  幅 | 絶対bit範囲 | 内容                                             |
| ----- | --: | ----------- | ------------------------------------------------ |
| SDMT  |   1 | 14          | `0=service type`, `1=MT44 transmission status`。 |
| SDM   |   9 | 15..23      | 9衛星分のビットマスク。                          |

### 4.1 SD の意味

- `SDMT=0` のとき、各ビットは各衛星が `For Japan` か `For use outside Japan` かを示す。
- `SDMT=1` のとき、各ビットは各衛星が `Transmission in progress` か `Transmission stopped` かを示す。
- SD はアプリケーションが本文を破棄する場合でも処理対象であると仕様にあるため、本文 parse 失敗と切り離して扱う必要がある。

## 5. CAMF

CAMF の定義は以下で固定である。

| Field |  幅 | 絶対bit範囲 |
| ----- | --: | ----------- |
| A1    |   2 | 24..25      |
| A2    |   9 | 26..34      |
| A3    |   5 | 35..39      |
| A4    |   7 | 40..46      |
| A5    |   2 | 47..48      |
| A6    |   1 | 49          |
| A7    |  14 | 50..63      |
| A8    |   2 | 64..65      |
| A9    |   1 | 66          |
| A10   |   3 | 67..69      |
| A11   |  10 | 70..79      |
| A12   |  16 | 80..95      |
| A13   |  17 | 96..112     |
| A14   |   5 | 113..117    |
| A15   |   5 | 118..122    |
| A16   |   6 | 123..128    |
| A17   |   2 | 129..130    |
| A18   |  15 | 131..145    |

### 5.1 CAMF の主要意味

- `A1`: `00=Test`, `01=Alert`, `10=Update`, `11=All Clear`。
- `A2`: Country/Region Name、日本向けメッセージでは `001101111 = Japan` 固定。
- `A3`: Provider Identifier、日本では `00001=FMMC`, `00010=FDMA`, `00011=Related Ministries`, `00100=Local Government` が使用される。
- `A4`: Hazard Category and Type。
- `A5`: Severity。
- `A6`: Hazard Onset Week Number。
- `A7`: Hazard Onset Time of the Week。
- `A8`: Hazard Duration。
- `A9`: Selection of Library。
- `A10`: Version of Library。
- `A11`: Guidance to react library。
- `A12..A16`: 楕円ターゲット領域。
- `A17..A18`: Specific settings。

### 5.2 A12〜A18 の補足

- `A12` は 16bit 緯度コードで、`-90..90` を等分した値を表す。
- `A13` は 17bit 経度コードで、`-180..180` を等分した値を表す。
- `A14` と `A15` は 5bit の半径コードで、半径 km はテーブル変換を使うのが実装上安全である。
- `A16` は 6bit 方位角コードで、`-90..90` を等分した値を表す。
- `A17` は Main Subject for Specific Settings で、日本向けの L-Alert / local government では `00 = B1 - Improved Resolution of Main Ellipse` 固定である。
- `A18` は Specific Settings で、日本向けの L-Alert / local government では B1 解釈に用いられるが、詳細ビット解釈は本会話では未展開である。
- J-Alert では `A12..A18` は未使用で全0固定である。

## 6. サービス種別判定

MT44 のサービス種別は `A2` と `A3` によって決定する。

- `A2 != Japan` なら `DCX message information from organizations outside Japan`。
- `A2 = Japan` かつ `A3 = 00001` なら `DCX message L-Alert`。
- `A2 = Japan` かつ `A3 = 00010` または `00011` なら `DCX message J-Alert`。
- `A2 = Japan` かつ `A3 = 00100` なら `DCX message information from local government`。
- `A2 = Japan` なのに `A3` が上記以外なら、そのメッセージは intended information ではないので discard とされる。

### 6.1 実装上の帰結

- `preamble` で J/L を分ける実装は不要である。
- `typebits` のような仕様外フィールドは廃止すべきである。
- `Message.h` 上は `enum class Mt44ServiceKind` を設け、`LAlert / JAlert / LocalGovernment / OutsideJapan / NullMessage / Unknown` に分けるのが妥当である。

## 7. Extended Message 総論

Extended Message は 74bit の固定長だが、サービス種別ごとに中身が異なる。
このため、実装では `variant` または明示的 union 構造で表す必要がある。

- L-Alert と local government: `EX1..EX7 + Vn`。
- J-Alert: `EX8..EX10 + Vn`。
- outside Japan: `EX11 + Vn`。

## 8. EX: L-Alert / local government

### 8.1 ビット構造

| Field |  幅 | 絶対bit範囲 | 備考                                  |
| ----- | --: | ----------- | ------------------------------------- |
| EX1   |  16 | 146..161    | Target Area Code。                    |
| EX2   |   1 | 162         | Evacuate Direction Type。             |
| EX3   |  17 | 163..179    | Additional Ellipse Centre Latitude。  |
| EX4   |  17 | 180..196    | Additional Ellipse Centre Longitude。 |
| EX5   |   5 | 197..201    | Additional Ellipse Semi-Major Axis。  |
| EX6   |   5 | 202..206    | Additional Ellipse Semi-Minor Axis。  |
| EX7   |   7 | 207..213    | Additional Ellipse Azimuth。          |
| Vn    |   6 | 214..219    | Version Number。                      |

### 8.2 EX1: Target Area Code

- `EX1` は 16bit の city/town/village コードで、JIS X 0402 の 6桁コードから最下位のチェック digit を落とした値を入れる。
- 例として、札幌市 `011002` は末尾桁を落として `01100` となり、これを 16bit 二進数にしたものを `EX1` に入れる。
- 指定がない場合は `ALL0` を入れる。
- `A12..A16` がすべて 0 の場合に `EX1` を参照する。
- したがって L-Alert では「楕円指定が無い場合の地域コード fallback」として扱うべきである。

### 8.3 EX2: Evacuate Direction Type

- `EX2=0` は `Leave the additional target area range`。
- `EX2=1` は `Head to the additional target area range`。
- これは **local government 専用** であり、L-Alert では未使用である。
- A11 と同様に避難行動を表すが、EX2〜EX7 のほうがより精密な地域指定を伴う。

### 8.4 EX3〜EX7: Additional Ellipse

- `EX3` は additional ellipse center latitude で、17bit により `-90..90` を等分する。
- `EX4` は additional ellipse center longitude で、17bit により `45..225` を等分する。
- `EX4` が `45..225` なのは、QZSS の運用範囲中心 135 度を含む 180 度幅だけ表せば十分であるという説明がある。
- `EX5` と `EX6` は追加楕円の semi-major / semi-minor で、変換は `A14/A15` と同じ表を用いる。
- `EX7` は additional ellipse azimuth で 7bit 値を持つ。
- `EX3..EX7` は local government 用であり、L-Alert では未使用である。

### 8.5 EX2〜EX7 の意味運用

- local government では、A11 による行動指示に加え、`EX2 + EX3..EX7` で「どこから離れるか、どこへ向かうか」を精密に指定できる。
- `EX2` と `EX3..EX7` がすべて 0 の場合は、この追加指示は存在しないものとして扱う。
- A11 と EX2〜EX7 の両方が送られる場合、仕様は **combined instructions を推奨** している。
- L-Alert と J-Alert では、避難行動指示は A11 のみであり、EX2〜EX7 は使わない。

### 8.6 Vn

- L-Alert / local government の `Vn` は 6bit で、値は固定 `000001` である。
- 実装上は `assert(raw_vn == 1)` または warning 扱いにしてよい。

## 9. EX: J-Alert

### 9.1 ビット構造

| Field |  幅 | 絶対bit範囲 | 備考                         |
| ----- | --: | ----------- | ---------------------------- |
| EX8   |   1 | 146         | Target Area Code List Type。 |
| EX9   |  64 | 147..210    | Target Area Code List。      |
| EX10  |   3 | 211..213    | Reserved。                   |
| Vn    |   6 | 214..219    | Version Number。             |

### 9.2 EX8: Target Area Code List Type

- `EX8=0` は prefecture code。
- `EX8=1` は cities, towns and villages code。

### 9.3 EX9: Target Area Code List

#### 9.3.1 EX8=0 の場合

- `EX9` は 47bit の prefecture code と 17bit reserved から成る。
- 複数の prefecture は OR 結果で表現される。
- すべての bit が 1 の場合、全 prefecture が対象である。
- 仕様書には 47 都道府県のビット位置表がある。
- 例として、`...000111` なら Hokkaido, Aomori, Iwate が対象である。

#### 9.3.2 EX8=1 の場合

- `EX9` は 16bit の city/town/village code を 4 個並べた構造である。
- 最大 4 コードを格納できる。
- コード体系は `EX1` と同じ city/town/village code を使う。
- 指定が無い場合は `ALL0` である。

### 9.4 J-Alert の target area 判定

- J-Alert の target area は `EX8` と `EX9` により表され、`A12..A16` はすべて 0 で未使用である。
- `EX8=0` なら prefecture ベース、`EX8=1` なら city/town/village ベースで解釈する。
- このため、J-Alert を楕円ロジックで処理する実装は誤りである。

### 9.5 J-Alert の運用上の注意

- J-Alert は一般に `A1=Alert` のみを使い、避難呼びかけの解除も `Alert` メッセージで送られる場合がある。
- 解除かどうかの識別は `A1` ではなく `A11 Guidance to react library` の内容を見る必要がある。
- false alert の場合は `All Clear` が送られることがある。
- よって J-Alert では `A1==Alert` をそのまま「発報」とみなす設計は危険である。

### 9.6 Vn

- J-Alert の `Vn` は 6bit で、固定 `000001` である。

## 10. EX: outside Japan

### 10.1 ビット構造

| Field |  幅 | 絶対bit範囲 | 備考                                       |
| ----- | --: | ----------- | ------------------------------------------ |
| EX11  |  68 | 146..213    | Organization outside Japan-Specific Area。 |
| Vn    |   6 | 214..219    | Version Number。                           |

### 10.2 EX11 の意味

- `EX11` は organization outside Japan-specific information を示す 68bit コードである。
- 仕様上、詳細は **undefined** である。
- したがって、現時点では raw 値保持以外の確定実装はできない。
- ここは `std::array<uint8_t, 9>` 相当または 128bit 整数等で raw を保持し、解釈は provider ごとの別層に委ねるべきである。

### 10.3 Vn

- outside Japan の `Vn` は、organization outside Japan 独自の version management system で定義される。
- 日本向けのように固定 `000001` とは限らないため、固定値チェックはしてはならない。

## 11. NULL Message

MT44 NULL Message は、送る DCX 本文が無いときでも `SD` を受信機へ伝えるための専用メッセージである。
仕様上、これは DCX message として処理しない。

### 11.1 NULL Message の固定値

| Field            | 値                |
| ---------------- | ----------------- |
| MT               | `101100` (MT44)   |
| SD               | 通常どおり        |
| A1               | all 0             |
| A2               | `001101111` Japan |
| A3               | all 0             |
| A4               | all 0             |
| A5               | all 0             |
| A6               | 0                 |
| A7               | all 0             |
| A8               | all 0             |
| A9               | 0                 |
| A10              | all 0             |
| A11              | all 0             |
| A12..A18         | all 0             |
| Extended Message | all 0             |
| Reserved         | 6bit reserved     |
| CRC              | CRC24             |

### 11.2 NULL Message 実装条件

以下をすべて満たす場合、`NullMessage` 扱いが妥当である。

- `MT == 44`。
- `A2 == Japan`。
- `A3 == 0`。
- `A1, A4..A18, EX, Reserved` が規定どおり 0。

NULL Message は `SD` は処理するが、alert 一覧へ入れてはならない。

## 12. target area 判定ロジック

### 12.1 L-Alert

- target area は `A12..A16` の楕円、または `EX1` の city/town/village code により表される。
- `A12..A16` がすべて 0 の場合のみ `EX1` を参照する。

### 12.2 J-Alert

- target area は `EX8/EX9` により表される。
- `A12..A16` は使わない。

### 12.3 local government

- 主 target area は `A12..A16` の楕円および `EX1` の code を持ちうる。
- さらに `EX2..EX7` により additional target area を指定できる。
- 「主要領域」と「追加領域」は別概念として保持する必要がある。

### 12.4 inside / outside 判定

- 楕円 inside / outside 判定は `A12..A16` と `EX3..EX7` の両方に同じ方法が使えると仕様にある。
- 地理計算は WGS84 の ENU local Cartesian への変換を使う手順が示されている。
- したがって、additional ellipse も main ellipse も共通の幾何関数へ流す設計が望ましい。

## 13. A11 と EX の優先関係

DCX の避難行動指示には 2 系統ある。

- `A11 Guidance to react library`。
- `EX2 + EX3..EX7` による additional ellipse 指示。

運用上の整理は以下でよい。

- L-Alert: A11 のみ有効。
- J-Alert: A11 のみ有効。
- local government: A11 と EX2〜EX7 の両方が有効になりうる。
- local government で両方来た場合、combined instructions として扱うのが推奨である。

## 14. 重複判定と alert 同一性

仕様上、Update / All Clear における alert の同一性は以下で識別される。

- L-Alert / local government: `A2 + A3 + A4 + EX1`。
- J-Alert: `A2 + A3 + A4`。

一方、現行実装の dedup は `svid + msg_type + crc24` に依存しているため、仕様上の alert identity とは別概念である。
このため、以下の二層に分離すべきである。

- **受信重複抑止**: burst / same frame 対策。
- **alert identity**: Update / All Clear 対応のための仕様準拠キー。

## 15. 実装に必要な構造の姿

### 15.1 生構造

```cpp
enum class Mt44ServiceKind {
    NullMessage,
    LAlert,
    JAlert,
    LocalGovernment,
    OutsideJapan,
    Unknown
};

enum class ExtendedKind {
    None,
    LAlertOrLocal,
    JAlert,
    OutsideJapan
};

struct Mt44Sd {
    uint8_t sdmt;   // 1 bit
    uint16_t sdm;   // 9 bits
};

struct Mt44CamfRaw {
    uint8_t  a1;    // 2
    uint16_t a2;    // 9
    uint8_t  a3;    // 5
    uint8_t  a4;    // 7
    uint8_t  a5;    // 2
    uint8_t  a6;    // 1
    uint16_t a7;    // 14
    uint8_t  a8;    // 2
    uint8_t  a9;    // 1
    uint8_t  a10;   // 3
    uint16_t a11;   // 10
    uint16_t a12;   // 16
    uint32_t a13;   // 17
    uint8_t  a14;   // 5
    uint8_t  a15;   // 5
    uint8_t  a16;   // 6
    uint8_t  a17;   // 2
    uint16_t a18;   // 15
};

struct Mt44ExLAlertOrLocal {
    uint16_t ex1;   // 16
    uint8_t  ex2;   // 1
    uint32_t ex3;   // 17
    uint32_t ex4;   // 17
    uint8_t  ex5;   // 5
    uint8_t  ex6;   // 5
    uint8_t  ex7;   // 7
    uint8_t  vn;    // 6
};

struct Mt44ExJAlert {
    uint8_t  ex8;   // 1
    uint64_t ex9;   // 64
    uint8_t  ex10;  // 3 reserved
    uint8_t  vn;    // 6
};

struct Mt44ExOutside {
    std::array<uint8_t, 9> ex11_raw; // 68bit raw を格納
    uint8_t vn;                      // 6
};

struct Mt44Raw {
    uint8_t pab;        // 8
    uint8_t mt;         // 6
    Mt44Sd sd;
    Mt44CamfRaw camf;

    ExtendedKind ex_kind;
    Mt44ExLAlertOrLocal ex_lalert_local{};
    Mt44ExJAlert ex_jalert{};
    Mt44ExOutside ex_outside{};

    uint8_t reserved6;  // 6
    uint32_t crc24;     // 24
};
```

### 15.2 解釈後構造

```cpp
struct DecodedEllipse {
    double lat_deg;
    double lon_deg;
    double semi_major_km;
    double semi_minor_km;
    double azimuth_deg;
};

struct DecodedAdditionalArea {
    bool present;
    bool head_to_area;  // false=leave, true=head
    std::optional<DecodedEllipse> ellipse;
};

struct Mt44Decoded {
    Mt44ServiceKind service_kind;
    bool is_null_message;

    Mt44Raw raw;

    std::string country_name;
    std::string provider_name;
    std::string hazard_name;
    std::string severity_name;
    std::string guidance_text;

    std::optional<DecodedEllipse> main_ellipse;
    std::optional<uint16_t> target_area_code;
    std::vector<uint16_t> target_area_code_list;
    std::vector<uint8_t> prefecture_bit_positions;

    std::optional<DecodedAdditionalArea> additional_area;
};
```

## 16. デコード手順

1. 250bit を PAB 基準で保持する。
2. `MT == 44` を確認する。
3. `SD` を抽出する。
4. `CAMF A1..A18` を仕様幅どおり抽出する。
5. NULL Message 条件を先に判定する。
6. `A2/A3` により `Mt44ServiceKind` を決定する。
7. service kind に応じて `Extended Message` を対応 variant で抽出する。
8. `A12..A16`, `EX3..EX7`, `EX8/EX9` を種別別に解釈する。
9. Atarashi テーブルで `A2/A3/A4/A5/A11/地域コード` を文言化する。
10. alert identity key と receive dedup key を分離して生成する。

## 17. Atarashi 変換テーブルの適用点

使うべき箇所は以下である。

- `A2` Country/Region 名称。
- `A3` Provider 名称。
- `A4` Hazard 名称。
- `A5` Severity 名称。
- `A11` Guidance 文面。
- `EX1` / `EX9(city list)` の自治体コード解決。
- `EX9(prefecture)` の都道府県名展開。
- `A14/A15` と `EX5/EX6` の半径値変換。
- `A17/A18` の specific settings 解釈。

使うべきでない箇所は以下である。

- ビット幅。
- ビットオフセット。
- service kind 判定。
- NULL Message 判定。
- EX variant 分岐。
- CRC 抽出。

## 18. 未確認事項

- `A18 Specific Settings` の B1 の厳密ビット内訳は、この会話内では表本体未展開であるため、ここでは未確定とする。
- `EX11` は仕様上 undefined であり、raw 保持以外の意味解釈は未定義である。
- `EX7` の 7bit 方位角の厳密復元式は、例と説明断片は確認できるが、式の完全転記はこの会話では未整形であるため、実装時は PDF 原本で再確認すべきである。

## 19. 最小結論

- まず固定すべきは **MT44 ビット配置**、次に **A2/A3 ベースの service kind 判定**、最後に **EX variant ごとの個別実装** である。
- J-Alert は `EX8/EX9`、local government は `EX2..EX7` が本体であり、ここを省くと実装は仕様適合にならない。
- outside Japan は `EX11` が未定義なので、raw 保持を仕様上の完成形とみなすしかない。
- 実装の最初の到達点は、`Mt44Raw` を漏れなく埋め、次に `Mt44Decoded` を積み増す二層構造である。
