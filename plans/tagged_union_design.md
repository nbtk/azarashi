# Tagged Union 実装計画

## 概要

メモリ効率と読みやすさ、変更度合いの折衷案として**Tagged Union**を採用する。

---

## 設計方針

### 現在の問題点

`Message`構造体はMT43/MT44のデータをフラットに格納しており、約1000+ bytesのメモリを使用している。これらは排他的であるため、Union化で約50%削減可能。

### Tagged Union の利点

| 項目 | 評価 |
|---|---|
| メモリ効率 | ◎（union部分のみ共有） |
| 読みやすさ | ○（enumによる明示的なタグ） |
| 変更度合い | ○（既存コードの修正が最小限） |
| C互換性 | ◎（維持可能） |
| 型安全性 | ○（enumチェックで保証） |

---

## 実装デザイン

### Phase 1: MT43/MT44 のトップレベルUnion化

```cpp
// src/Message.h

// MT43 災害カテゴリデータ
struct Mt43Data {
    // ---- MT=43 outer frame ----
    uint8_t  report_classification;
    uint8_t  disaster_category;
    uint8_t  information_type;
    TimeFields event_time;
    
    // ---- EEW (disaster_category == 1) ----
    uint8_t  eew_long_period_lower;
    uint8_t  eew_long_period_upper;
    uint16_t eew_notification[3];
    uint8_t  eew_notification_count;
    TimeFields eew_quake_time;
    uint16_t eew_depth;
    uint8_t  eew_magnitude;
    uint16_t eew_epicenter;
    uint8_t  eew_intensity_lower;
    uint8_t  eew_intensity_upper;
    uint8_t  eew_regions[80];
    uint8_t  eew_region_count;
    
    // ---- Hypocenter (disaster_category == 2) ----
    uint16_t         hypo_notification[3];
    uint8_t          hypo_notification_count;
    TimeFields       hypo_quake_time;
    uint16_t         hypo_depth;
    uint8_t          hypo_magnitude;
    uint16_t         hypo_epicenter;
    LatLon           hypo_coords;
    
    // ---- Seismic Intensity (disaster_category == 3) ----
    TimeFields       seis_quake_time;
    SeismicEntry     seis_entries[16];
    uint8_t          seis_count;
    
    // ---- Nankai Trough (disaster_category == 4) ----
    uint8_t          nankai_info_code;
    uint8_t          nankai_text[18];
    uint8_t          nankai_page;
    uint8_t          nankai_total_page;
    
    // ---- Tsunami (disaster_category == 5) ----
    uint8_t          tsunami_warning_code;
    TsunamiEntry     tsunamis[5];
    uint8_t          tsunami_count;
    
    // ---- NW Pacific Tsunami (disaster_category == 6) ----
    uint8_t          nw_pac_potential;
    NwPacTsunamiEntry nw_pac_tsunamis[5];
    uint8_t          nw_pac_count;
    
    // ---- Volcano (disaster_category == 8) ----
    uint8_t          vol_ambiguity;
    TimeFields       vol_activity_time;
    uint8_t          vol_warning_code;
    uint16_t         vol_volcano_name;
    uint32_t         vol_local_govs[5];
    uint8_t          vol_lg_count;
    
    // ---- Ash Fall (disaster_category == 9) ----
    TimeFields       ash_activity_time;
    uint8_t          ash_warning_type;
    uint16_t         ash_volcano_name;
    uint8_t          ash_entries_time[4];
    uint8_t          ash_entries_code[4];
    uint32_t         ash_entries_lg[4];
    uint8_t          ash_count;
    
    // ---- Weather (disaster_category == 10) ----
    uint8_t          wx_warning_state;
    WeatherEntry     wx_entries[6];
    uint8_t          wx_count;
    
    // ---- Flood (disaster_category == 11) ----
    FloodEntry       flood_entries[3];
    uint8_t          flood_count;
    
    // ---- Typhoon (disaster_category == 12) ----
    TimeFields       typh_reference_time;
    uint8_t          typh_ref_type;
    uint8_t          typh_elapsed;
    uint8_t          typh_number;
    uint8_t          typh_scale;
    uint8_t          typh_intensity;
    LatLon           typh_coords;
    uint16_t         typh_pressure;
    uint8_t          typh_max_wind;
    uint8_t          typh_max_gust;
    
    // ---- Marine (disaster_category == 14) ----
    MarineEntry      marine_entries[8];
    uint8_t          marine_count;
};

// MT44 DCX データ
struct Mt44Data {
    Mt44ServiceKind service_kind;
    bool            is_null_message;
    
    Mt44Sd          sd;
    Mt44CamfRaw     camf;
    TimeFields      onset_time;
    
    ExtendedKind        ex_kind;
    Mt44ExLAlertOrLocal ex_lalert_local;
    Mt44ExJAlert        ex_jalert;
    Mt44ExOutside       ex_outside;
    
    Mt44Decoded      mt44_decoded;
};

// メッセージタイプタグ
enum class MsgPayloadType : uint8_t {
    Empty,
    Mt43,
    Mt44
};

// Tagged Union
struct Message {
    // ---- common ----
    uint8_t  svid;
    uint8_t  msg_type;    // 43 or 44
    uint32_t crc24;
    bool     valid;
    
    // ---- payload (tagged union) ----
    MsgPayloadType payload_type;
    union {
        Mt43Data mt43;
        Mt44Data mt44;
    };
};
```

### アクセスパターン

```cpp
// デコード時
void Decoder::decodeQzqsm(const uint8_t* bits, Message& out, uint32_t report_unix) {
    out.payload_type = MsgPayloadType::Mt43;
    Mt43Data& d = out.mt43;  // 直接参照取得
    
    d.report_classification = getBits(bits, 14, 3);
    d.disaster_category = getBits(bits, 17, 4);
    // ...
}

// アクセス時
void processMessage(const Message& msg) {
    if (msg.payload_type == MsgPayloadType::Mt43) {
        const Mt43Data& d = msg.mt43;
        // MT43処理
    } else if (msg.payload_type == MsgPayloadType::Mt44) {
        const Mt44Data& d = msg.mt44;
        // MT44処理
    }
}
```

---

## 実装手順

### Step 1: Message.h の変更

1. `Mt43Data` 構造体を定義（MT43関連フィールドを移動）
2. `Mt44Data` 構造体を定義（MT44関連フィールドを移動）
3. `MsgPayloadType` enum を定義
4. `Message` 構造体を修正（union追加）

### Step 2: Decoder の変更

| ファイル | 変更内容 |
|---|---|
| `Decoder.cpp` | `out = {}` の初期化を修正 |
| `DecoderQzqsm.cpp` | `out.mt43.xxx` にアクセス変更 |
| `DecoderDcx.cpp` | `out.mt44.xxx` にアクセス変更 |

### Step 3: JsonSerializer の変更

| ファイル | 変更内容 |
|---|---|
| `JsonSerializer.cpp` | `msg.mt43.xxx` / `msg.mt44.xxx` にアクセス変更 |
| `JsonSerializerQzqsm.cpp` | `m.mt43.xxx` にアクセス変更 |
| `JsonSerializerDcx.cpp` | `m.mt44.xxx` にアクセス変更 |

### Step 4: テストコードの変更

| ファイル | 変更内容 |
|---|---|
| `test_decoder.cpp` | フィールドアクセス修正 |
| `test_json.cpp` | フィールドアクセス修正 |
| その他テスト | フィールドアクセス修正 |

---

## メモリ使用量の比較

### 変更前

```
Message構造体: 約1000+ bytes
├── common: ~16 bytes
├── MT43 data: ~500 bytes (常に確保)
├── MT44 data: ~200 bytes (常に確保)
└── MT44 decoded: ~300 bytes (常に確保)
```

### 変更後

```
Message構造体: 約550 bytes
├── common: ~16 bytes
├── payload_type: ~1 byte
└── union: ~533 bytes (max(Mt43Data, Mt44Data))
    ├── Mt43Data: ~500 bytes
    └── Mt44Data: ~533 bytes
```

**削減率: 約45%**

---

## 既存コードとの互換性

### 影響を受ける箇所

| 箇所 | 影響 | 修正方法 |
|---|---|---|
| `msg.eew_magnitude` | `msg.mt43.eew_magnitude` に変更 | 検索置換 |
| `msg.service_kind` | `msg.mt44.service_kind` に変更 | 検索置換 |
| `msg.camf.a1` | `msg.mt44.camf.a1` に変更 | 検索置換 |
| `msg.disaster_category` | `msg.mt43.disaster_category` に変更 | 検索置換 |

### 影響を受けない箇所

- `msg.svid`
- `msg.msg_type`
- `msg.crc24`
- `msg.valid`

---

## リスクと対策

| リスク | 対策 |
|---|---|
| 初期化漏れ | `payload_type` を必ず設定するコメント追加 |
| 間違えたunionメンバーアクセス | enumチェックを推奨するコメント追加 |
| テスト漏れ | 全テストファイルの修正をチェックリスト化 |

---

## 将来の拡張

### Phase 2: MT44 Extended MessageのUnion化（任意）

```cpp
struct Mt44Data {
    // ...
    ExtendedKind ex_kind;
    union {
        Mt44ExLAlertOrLocal lalert_local;
        Mt44ExJAlert jalert;
        Mt44ExOutside outside;
    } ex;
};
```

### Phase 3: MT43災害カテゴリのUnion化（任意）

メモリ削減効果が小さいため、実装コストに見合うか要検討。
