# Union型使用に関する分析

## 概要

メッセージのデコーダにおいて、MT43/MT44、J-alert/L-alertなどの排他的なデータが現在フラットな構造体に格納されている。Union型を使用することによるメリット・デメリット・実装コスト・正確性を分析する。

---

## 現在の構造体の問題点

現在の`Message`構造体（`src/Message.h`）は、排他的なデータをフラットに格納しているため、**メモリ効率が悪い**。

| フィールドグループ | 使用条件 | サイズ（概算） |
|---|---|---|
| MT43 JMA災害カテゴリ別データ | `msg_type == 43` の時のみ | ~500 bytes |
| MT44 DCX CAMF/Extended | `msg_type == 44` の時のみ | ~200 bytes |
| MT44 Decoded | `msg_type == 44` の時のみ | ~300 bytes |

これらは**同時に有効にならない**ため、Union化によりメモリを大幅に削減可能。

---

## Union型を使用するメリット

### 1. メモリ使用量の大幅削減

```
現在のMessage構造体サイズ: 約1000+ bytes
Union化後: 約400-500 bytes（最大メンバーに依存）
```

Arduino/ESP32などのメモリ制約のある環境では**大きなメリット**。

### 2. 型安全性の向上

- `msg_type`や`service_kind`による分岐が明確になる
- 無効なフィールドへのアクセスをコンパイル時に検出可能（C++17 `std::variant`使用時）

### 3. コードの意図が明確化

- 「これらのフィールドは排他的である」という設計意図が型システムに反映される
- ドキュメント不要な自己説明的なコードになる

---

## Union型を使用するデメリット

### 1. C言語互換性の喪失

- `std::variant`（C++17）はC言語では使用できない
- 従来のCスタイル`union`は型安全性が低い

### 2. アクセスの複雑化

- 現在: `out.eew_magnitude`（直接アクセス）
- Union化後: `out.mt44.ex_jalert.vn`（階層アクセス）
- 既存の全アクセス箇所を修正する必要がある

### 3. シリアライズの複雑化

- `JsonSerializer`などの出力処理で分岐が増える
- 現在のフラット構造の方がJSON変換がシンプル

### 4. デバッグの困難さ

- Unionのメンバーが上書きされるため、デバッガでの値の追跡が難しくなる

---

## 実装コストの見積もり

### 必要な変更箇所

| ファイル | 変更内容 | 難易度 |
|---|---|---|
| `src/Message.h` | Union構造体の定義 | 中 |
| `src/internal/Decoder.cpp` | 初期化ロジックの変更 | 低 |
| `src/internal/DecoderQzqsm.cpp` | MT43フィールドアクセス | 中 |
| `src/internal/DecoderDcx.cpp` | MT44フィールドアクセス | 中 |
| `src/internal/JsonSerializer*.cpp` | シリアライズロジック | 高 |
| `test/*.cpp` | テストコードの更新 | 中 |
| その他全ソース | フィールドアクセス箇所の修正 | 高 |

### 推奨される実装アプローチ

#### 案A: C++17 `std::variant`（型安全）

```cpp
struct Mt43Data {
    uint8_t disaster_category;
    // ... MT43固有フィールド
};

struct Mt44Data {
    Mt44ServiceKind service_kind;
    Mt44CamfRaw camf;
    // ... MT44固有フィールド
};

struct Message {
    uint8_t svid;
    uint8_t msg_type;
    uint32_t crc24;
    bool valid;
    
    std::variant<Mt43Data, Mt44Data> payload;
};
```

#### 案B: 従来のCスタイルUnion（C互換）

```cpp
union MessagePayload {
    struct {
        uint8_t disaster_category;
        // ... MT43固有フィールド
    } mt43;
    
    struct {
        Mt44ServiceKind service_kind;
        Mt44CamfRaw camf;
        // ... MT44固有フィールド
    } mt44;
};

struct Message {
    uint8_t svid;
    uint8_t msg_type;
    uint32_t crc24;
    bool valid;
    
    MessagePayload payload;
};
```

---

## 正確性に関する注意点

### 1. 規格準拠の確認

- IS-QZSS-DCR-016 / IS-QZSS-DCX-003において、MT43/MT44は**確かに排他的**
- `msg_type`（bit[8..13]）が43または44のみを取るため、同時に両方のデータが存在することはない

### 2. 災害カテゴリの排他性

- MT43内でも`disaster_category`（bit[17..20]）によりサブタイプが排他的
- これもUnion化の候補だが、メモリ削減効果は小さい

### 3. Extended Messageの排他性

- MT44内で`ex_kind`によりL-Alert/Local/J-Alert/OutsideJapanが排他
- これもUnion化可能

---

## 推奨事項

### 段階的アプローチを推奨

1. **Phase 1**: MT43/MT44のトップレベルUnion化（最大のメリット）
2. **Phase 2**: MT44 Extended MessageのUnion化（中程度のメリット）
3. **Phase 3**: MT43災害カテゴリのUnion化（小さいメリット、実装コスト高）

### 判断基準

| 条件 | 推奨 |
|---|---|
| メモリ制約が厳しい（Arduino Uno等） | **Union化を強く推奨** |
| ESP32等の比較的大きなメモリ | 任意（可読性優先で現状維持も可） |
| C言語互換性が必要 | CスタイルUnionまたは現状維持 |
| 新規開発・大規模リファクタリング | `std::variant`を推奨 |

---

## 結論

**Union化は技術的に正当であり、メモリ制約のある環境では有効**。

| 項目 | 評価 |
|---|---|
| メモリ削減効果 | 大きい（50%以上削減可能） |
| 実装コスト | 中〜高（全ソースの修正が必要） |
| リスク | 中（シリアライズ周りのバグ混入リスク） |
| メリット | 型安全性、メモリ効率、設計意図の明確化 |

**最終判断は、ターゲットハードウェアのメモリ制約と、今後のメンテナンス性を考慮して決定**することを推奨する。
