<img src="https://raw.githubusercontent.com/A-vrice/azaraC/refs/heads/main/logo.png" width="256">

# AzaraC

A QZSS DCR DCX Decoder for Arduino.

## Description

AzaraCは準天頂衛星みちびきが送信する災危通報メッセージのデコーダーであるazarashiをArduino向けに移植したものです。QZSS L1S信号を用いた災危通報の**DCX/CAMF**(MT=44)および**DC Report/QZQSM**(MT=43)に対応しており，ESP32シリーズなどのArduino互換ボード向けに設計されています。外部ライブラリには依存していません。

定義テーブル(`definition/*.h`)は[azarashi](https://github.com/nbtk/azarashi)の
`definition/*.py`からGitHub Actionsでの自動生成を行っています。azarashiのバージョンが
更新されるとPRが自動作成されるため、常にazarashiと同じ定義が維持されます。

## 対応メッセージ

| msg_type | 規格            | 内容                             |
| -------- | --------------- | -------------------------------- |
| 43       | IS-QZSS-DCR-016 | JMA DC Report (QZQSM) — 全12種   |
| 44       | IS-QZSS-DCX-003 | DCX / CAMF (L-Alert, J-Alert 等) |

### MT=43 防災カテゴリ一覧

| カテゴリID | 内容                              | 規格セクション |
| ---------- | --------------------------------- | -------------- |
| 1          | 緊急地震速報 (EEW)                | §5.1.2.3.1     |
| 2          | 震源情報 (Hypocenter)             | §5.1.2.3.2     |
| 3          | 震度情報 (Seismic Intensity)      | §5.1.2.3.3     |
| 4          | 南海トラフ地震 (Nankai Trough)    | §5.1.2.3.4     |
| 5          | 津波警報・注意報 (Tsunami)        | §5.1.2.3.5     |
| 6          | 北太平洋津波 (NW Pacific Tsunami) | §5.1.2.3.6     |
| 8          | 火山情報 (Volcano)                | §5.1.2.3.7     |
| 9          | 降灰情報 (Ash Fall)               | §5.1.2.3.8     |
| 10         | 気象警報・注意報 (Weather)        | §5.1.2.3.9     |
| 11         | 洪水警報 (Flood)                  | §5.1.2.3.10    |
| 12         | 台風情報 (Typhoon)                | §5.1.2.3.11    |
| 14         | 海上警報 (Marine)                 | §5.1.2.3.12    |

### MT=44 サービス種別

| service_kind    | 内容                             | 判定条件                 |
| --------------- | -------------------------------- | ------------------------ |
| LAlert          | L-Alert (地方自治体向け緊急速報) | A2=111 (Japan) & A3=1-4  |
| JAlert          | J-Alert (全国瞬時警報システム)   | A2=111 (Japan) & A3=0    |
| LocalGovernment | 地方自治体送信情報               | A2=111 (Japan) & A3=5-31 |
| OutsideJapan    | 国外向け情報                     | A2≠111                   |
| NullMessage     | Null Message                     | A1=0                     |
| Unknown         | 不明                             | 上記以外                 |

## 動作環境

| 項目            | 値                                          |
| --------------- | ------------------------------------------- |
| 主要ターゲット  | ESP32-C3 (FreeRTOS / Arduino framework)     |
| Arduino コア    | esp32 ≥ 3.x                                 |
| ホストテスト    | g++ -std=c++17 (Linux / macOS / WSL)        |
| GNSS モジュール | u-blox (UBX-RXM-SFRBX) / NMEA $QZQSM 出力機 |

[注意] AzaraCはC++17で記述されています。利用の際は、お使いのIDEのC++コンパイラ設定を17以上にしてください。多くのボード/エディタでは標準設定がC++11となっており、AzaraCライブラリのコンパイル時にエラーが発生する可能性があります。

## インストール

### Arduino IDE（手動）

```bash
git clone https://github.com/A-vrice/azaraC \
  <PROJECT_DIR>/libraries/azaraC
```

### PlatformIO（手動）

```bash
git clone https://github.com/A-vrice/azaraC \
  <PROJECT_DIR>/.pio/libdeps/<TARGET_BOARD>/azaraC
```

---

## クイックスタート

### NMEA ($QZQSM) を使用する場合

```cpp
#include <azaraC.h>

azaraC::Parser  parser;
azaraC::Message msg;

void setup() {
    Serial.begin(115200);
    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
}

void loop() {
    while (Serial1.available()) {
        if (parser.feed(Serial1.read(), msg)) {
            azaraC::toJson(msg, Serial);
            Serial.println();
        }
    }
}
```

### UBX (RXM-SFRBX) を使用する場合

u-blox の設定:

```
CFG-MSGOUT-UBX_RXM_SFRBX_UART1 = 1
CFG-SIGNAL-QZSS_L1S_ENA        = 1
```

コードはNMEAと同じです。`Parser`が自動判別します。

### UNIX時刻付き（メッセージから年月を含めた日時情報を取得したい場合）

```cpp
// SNTP/GPS等で取得したUNIX時刻を渡す
uint32_t now = (uint32_t)time(nullptr);
if (parser.feed(byte, msg, now)) { ... }
```

詳細は[`examples/with_sntp/`](examples/with_sntp/)を参照。

---

## API

### `azaraC::Parser`

```cpp
// 1バイト投入。新しい有効メッセージが揃ったら true を返す
bool feed(uint8_t byte, Message& out, uint32_t now_unix = 0);

void reset();  // フレーマ・重複フィルタをリセット
```

重複除去は **{svid, msg_type, crc24}** のリングバッファで行います。
デフォルトスロット数は 8 としています。複数 SV を受信する場合は 32 や 128 などに適宜調整してください:

```cpp
#define AZARAC_DEDUP_SLOTS 32
#include <azaraC.h>
```

### 言語テーブルの選択的コンパイル

定義テーブルの言語を選択してFlash使用量を削減できます。
デフォルトは日本語のみ有効です:

```cpp
// 日本語のみ（デフォルト）- 英語テーブルを除外して約15KB削減
#include <azaraC.h>

// 英語のみ
#define AZARAC_LANG_JA 0
#define AZARAC_LANG_EN 1
#include <azaraC.h>

// 両方有効
#define AZARAC_LANG_JA 1
#define AZARAC_LANG_EN 1
#include <azaraC.h>
```

### `azaraC::toJson(msg, out)`

`Message`をJSONにシリアライズして任意の`Print&` に出力します。
`Serial`, `WiFiClient`, `StringPrint`（テスト用）などを渡せます。

### `azaraC::Message`

```cpp
struct Message {
    uint8_t  svid;
    uint8_t  msg_type;   // 43 or 44
    uint32_t crc24;
    bool     valid;

    // MT=44 フィールド: service_kind, a1_message_type, a2_country_code ...
    // MT=43 フィールド: report_classification, disaster_category,
    //                   information_type, event_time
    //                   + サブタイプ別フィールド (eew_*, seis_*, tsu_* ...)
};
```

フィールド詳細は[`src/Message.h`](src/Message.h)を参照してください。

### 安全なアクセサ

```cpp
azaraC::Message msg;
// ...
if (msg.msg_type == 43) {
    const azaraC::Mt43Data* mt43 = msg.getMt43();
    if (mt43) {
        // MT=43 フィールドにアクセス
        uint8_t category = mt43->disaster_category;
    }
} else if (msg.msg_type == 44) {
    const azaraC::Mt44Data* mt44 = msg.getMt44();
    if (mt44) {
        // MT=44 フィールドにアクセス
        auto kind = mt44->service_kind;
    }
}
```

---

## JSON 出力例

### MT=43 EEW (緊急地震速報)

```json
{
  "svid": 193,
  "msg_type": 43,
  "crc24": 12345678,
  "report_classification": 1,
  "report_classification_label": "警報",
  "disaster_category": 1,
  "disaster_category_label": "緊急地震速報",
  "information_type": 0,
  "information_type_label": "発表",
  "report_time": { "day": 19, "hour": 14, "min": 30, "unix": 0 },
  "detail": {
    "depth": 60,
    "magnitude": 65,
    "epicenter": 42,
    "epicenter_label": "千葉県北西部",
    "intensity_lower": 5,
    "intensity_lower_label": "5弱",
    "intensity_upper": 6,
    "intensity_upper_label": "6強",
    "regions": [
      { "code": 1, "label": "北海道道央" },
      { "code": 12, "label": "東京都" }
    ]
  }
}
```

### MT=43 台風情報

```json
{
  "svid": 193,
  "msg_type": 43,
  "disaster_category": 12,
  "disaster_category_label": "台風情報",
  "detail": {
    "reference_time": { "day": 15, "hour": 9, "min": 0 },
    "ref_type": 1,
    "ref_type_label": "Analysis",
    "number": 202401,
    "scale": 3,
    "scale_label": "大型",
    "intensity": 2,
    "intensity_label": "強い",
    "lat_deg": 28.5,
    "lon_deg": 135.2,
    "pressure": 965,
    "max_wind": 33,
    "max_gust": 50
  }
}
```

### MT=44 DCX (L-Alert)

```json
{
  "svid": 193,
  "msg_type": 44,
  "crc24": 11259375,
  "service_kind": 1,
  "service_kind_label": "L_ALERT",
  "a1_msg_type": "Alert",
  "a2_country": 111,
  "a2_country_label": "Japan",
  "a3_provider": 1,
  "a4_hazard": 10,
  "a4_hazard_category": "Geological",
  "a4_hazard_type": "Earthquake",
  "a5_severity": 3,
  "a5_severity_label": "Extreme",
  "onset_time": { "day": 19, "hour": 14, "min": 30, "unix": 1745123400 },
  "main_ellipse": {
    "lat_deg": 35.6,
    "lon_deg": 139.6,
    "semi_major_km": 10.933,
    "semi_minor_km": 8.085,
    "azimuth_deg": 30.0
  },
  "ex1_target_area": 1100,
  "ex1_target_area_label": "Sapporo-shi",
  "alert_identity": { "a2": 111, "a3": 1, "a4": 10, "ex1": 1100 }
}
```

### MT=44 DCX (J-Alert)

```json
{
  "svid": 193,
  "msg_type": 44,
  "service_kind": 2,
  "service_kind_label": "J_ALERT",
  "a4_hazard": 10,
  "a4_hazard_type": "Earthquake",
  "jalert_prefecture_mode": true,
  "prefecture_positions": [1, 12, 13, 14],
  "prefecture_count": 4
}
```

---

## Examples

詳細な使用例は[`examples/`](examples/)ディレクトリを参照してください。

| Example                                            | 説明                           |
| -------------------------------------------------- | ------------------------------ |
| [basic_nmea](examples/basic_nmea/)                 | NMEA $QZQSM の基本的な使用例   |
| [basic_ubx](examples/basic_ubx/)                   | UBX-RXM-SFRBX の基本的な使用例 |
| [with_sntp](examples/with_sntp/)                   | SNTP時刻解決 + EEWフィルタ     |
| [filter_by_category](examples/filter_by_category/) | 災害カテゴリ別フィルタリング   |
| [error_handling](examples/error_handling/)         | エラーハンドリングと統計       |
| [wifi_client](examples/wifi_client/)               | Wi-Fiクライアント出力          |

---

## 定義ファイルの自動生成

```
azarashi (PyPI)
  └── definition/*.py
        ↓  .github/workflows/update-definitions.yml (毎日 06:00 UTC)
  scripts/gen_definitions.py  → src/definition/*.h
        ↓  PR 自動作成 (peter-evans/create-pull-request)
  レビュー → マージ
```

手動実行:

```bash
pip install azarashi
python scripts/gen_definitions.py
```

---

## ホストテスト

ESP32 不要でビルド・実行できます:

```bash
make -C test run
```

```
=== azaraC unit tests ===
  PASS  crc_known_zeros
  PASS  crc_known_a5
  ...
  PASS  mt44_synthetic
=== all passed ===
=== azaraC JSON tests ===
  PASS  json_dcx_keys
  PASS  json_eew_keys
  ...
  PASS  json_balanced_mt44
=== all passed ===
```

---

## トラブルシューティング

### メッセージが受信されない場合

1. **配線を確認**: GNSSのTXがESP32のRXに接続されているか確認
2. **ボーレートを確認**: 9600 baudがデフォルト
3. **QZSS L1S信号が有効か確認**: u-bloxの設定を確認
4. **アンテナを確認**: 屋外または窓際でテスト

### コンパイルエラーが発生する場合

1. **C++17を有効化**: Arduino IDE → ツール → C++ Standard → C++17
2. **ボードサポートを確認**: ESP32 コア ≥ 3.x
3. **ライブラリのインストール**: azaraCがlibrariesフォルダにあるか確認

### JSON出力が不正な場合

1. **バッファサイズを確認**: 大きなメッセージの場合、Serialのバッファを増やす
2. **メモリ不足を確認**: ESP32-C3のメモリ使用量を確認

---

## 仕様書リファレンス

| 規格            | 内容                        | バージョン     |
| --------------- | --------------------------- | -------------- |
| IS-QZSS-DCR-016 | DC Report Service (MT=43)   | April 03, 2026 |
| IS-QZSS-DCX-003 | DCX Service (MT=44)         | March 28, 2025 |
| EWSS CAMF v1.1  | Common Alert Message Format | Version 1.1    |

---

## ライセンス

MIT

---

## 謝辞

メッセージ定義は [azarashi](https://github.com/nbtk/azarashi)(MIT)の
`definition/*.py` をもととさせていただきました。
また，ビット構造の解析の参照実装としてもazarashiのデコーダを参照させていただきました。

## Acknowledgements

The original project `azarashi` was developed by [NBTK](https://github.com/nbtk) during his time at BitMeister Inc., with support and resources generously provided by the company.

AzaraC is maintained independently by [A-vrice](https://github.com/A-vrice).

## 不具合など

何か不具合、疑問点があれば[Issue](https://github.com/A-vrice/azaraC/issues)，作者メールアドレス[AzaraC@vrice.f5.si]，およびTwitter(現X)のDMまでお願いします。
