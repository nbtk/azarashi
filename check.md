# J-Alert 都道府県デコードバグ修正計画

## 背景と問題の概要

`DcxHelper.cpp` の `decodePrefectureBitmask` 関数に **2重のバグ** を発見しました。
仕様書の例（IS-QZSS-DCX-003 §4.2.4.2.2）より:

> `"00000000000000000000000000000000000000000000111"` = Hokkaido, Aomori, Iwate

つまり、47-bit の都道府県コードは以下の整数値として定義されています:

- **bit 0 (LSB)** = 北海道 (JIS code 1)
- **bit 1** = 青森県 (JIS code 2)
- **bit 46 (MSB)** = 沖縄県 (JIS code 47)

## バグ原因の詳細分析

### EX9 のビット抽出（DecoderDcx.cpp）

`getBits` は MSB-first で抽出します。EX9 64-bit フィールドは `[47-bit prefecture][17-bit reserved]` の構成で、以下のように展開されます:

```
Stream bit 147 → ex9 bit 63 (Okinawa / MSB of 47-bit field)
Stream bit 193 → ex9 bit 17 (Hokkaido / LSB of 47-bit field)
Stream bits 194..210 → ex9 bits 16..0 (reserved)
```

つまり47-bit の都道府県コードは **ex9 bits [63:17]** に配置されます。
ex9 bits [16:0] はすべて reserved（ゼロ）です。

### 検証（仕様書の例で確認）

Hokkaido + Aomori + Iwate のとき 47-bit integer = 7 = `0b111`:

- Hokkaido: bit 0 → ex9 bit 17
- Aomori: bit 1 → ex9 bit 18
- Iwate: bit 2 → ex9 bit 19

→ `ex9 = 0x000E0000`

### 現在のコード（誤り）

```cpp
for (uint8_t i = 0; i < 47; ++i) {
    if (ex9 & (1ULL << i)) {      // ← bits [46:0] を検査（reserved 含む、北海道ビット[17]を miss）
        out_positions[count++] = 47 - i;  // ← JIS code と対応しない
    }
}
```

上記を `ex9 = 0x000E0000` で実行した場合:

- i=17 → bit 17 = 1 → `47-17 = 30` → 長野県 ❌（本来は北海道=1）
- i=18 → bit 18 = 1 → `47-18 = 29` → 山梨県 ❌（本来は青森県=2）
- i=19 → bit 19 = 1 → `47-19 = 28` → 長野県 ❌（本来は岩手県=3）

### 正しいコード

```cpp
// 47-bit prefecture field は ex9[63:17] に格納されているため、17bit 右シフトで揃える
uint64_t pref = ex9 >> 17;
for (uint8_t i = 0; i < 47; ++i) {
    if (pref & (1ULL << i)) {
        // i=0 (LSB) = bit 0 of 47-bit integer = Hokkaido = JIS code 1
        // i=46 (MSB) = bit 46 of 47-bit integer = Okinawa = JIS code 47
        out_positions[count++] = i + 1;
    }
}
```

検証: `pref = 0x000E0000 >> 17 = 7 = 0b111`:

- i=0 → bit 0 = 1 → JIS 1 = 北海道 ✅
- i=1 → bit 1 = 1 → JIS 2 = 青森県 ✅
- i=2 → bit 2 = 1 → JIS 3 = 岩手県 ✅

---

## 変更ファイル一覧

### [MODIFY] [DcxHelper.cpp](file:///d:/documents/azaraC/src/internal/DcxHelper.cpp)

`decodePrefectureBitmask` 関数の修正:

1. `uint64_t pref = ex9 >> 17;` を追加
2. `ex9 & (1ULL << i)` → `pref & (1ULL << i)` に変更
3. `47 - i` → `i + 1` に変更
4. コメントを正しい内容に書き直す

### [MODIFY] [DcxHelper.h](file:///d:/documents/azaraC/src/internal/DcxHelper.h)

`decodePrefectureBitmask` のコメントを正確な説明に更新

### [MODIFY] [test_decoder.cpp](file:///d:/documents/azaraC/test/test_decoder.cpp)

`decodePrefectureBitmask` の単体テストを追加:

```cpp
TEST_CASE("decodePrefectureBitmask: 仕様書例（北海道・青森・岩手）") {
    // IS-QZSS-DCX-003 §4.2.4.2.2 の例: 0b111 → Hokkaido, Aomori, Iwate
    // 47-bit integer = 7, EX9 64-bit = 7 << 17 = 0x000E0000
    uint64_t ex9 = (uint64_t)7 << 17;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 3);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[1] == 2);   // 青森県
    CHECK(positions[2] == 3);   // 岩手県
}

TEST_CASE("decodePrefectureBitmask: 沖縄のみ（MSB）") {
    // Okinawa = bit 46 of 47-bit integer = ex9 bit 63
    uint64_t ex9 = (uint64_t)1 << 63;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 47);  // 沖縄県
}

TEST_CASE("decodePrefectureBitmask: 全都道府県（全ビット=1）") {
    // All 47 bits set: 47-bit all-ones = (1ULL<<47)-1, shifted to ex9[63:17]
    uint64_t ex9 = ((1ULL << 47) - 1) << 17;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 47);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[46] == 47); // 沖縄県
}
```

---

## 検証計画

### 自動テスト

```bash
cd d:\documents\azaraC\test && make run
```

新規テストが `decodePrefectureBitmask` を直接検証し、PASS することを確認する。

### 確認すべき既存テスト

- `test_json.cpp` 内の「JSON Serialization: MT=44 DCX J-Alert」は、現状 `prefecture_positions` をモック手動設定しているため、バグ修正後も引き続き通過する（このテストはデコーダを経由しないため副作用なし）。
- 将来的にはエンドツーエンドのテスト追加を推奨。

---

## Open Questions

> [!NOTE]
> `test_json.cpp` の J-Alert テストは内部で `prefecture_positions` を手動設定しており、デコーダのロジックをバイパスしています。バグ修正後もこのテストは引き続き通過しますが、エンドツーエンドの検証として、修正後に `decodePrefectureBitmask` を通じて得られた positions を使った JSON テストも追加しますか？
