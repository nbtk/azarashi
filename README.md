<img src="https://raw.githubusercontent.com/A-vrice/azaraC/refs/heads/main/logo.png" width="256">

# AzaraC

A QZSS DCR DCX Decoder for Arduino.

## Description

azarashi は準天頂衛星みちびきが送信する災危通報メッセージのデコーダーであるazarashiをArduino向けに移植したものです。QZSS L1S **DCX/CAMF** (MT=44) および **DC Report / QZQSM** (MT=43) に対応しており，Arduino / ESP32-C3 向けに設計されています。メモリアロケーションなしや外部ライブラリへの依存はありません。

定義テーブル (`definition/*.h`) は [azarashi](https://github.com/nbtk/azarashi) の
`definition/*.py` から **GitHub Actions が自動生成** します。azarashi のバージョンが
更新されると CI が PR を自動作成するため、定義ファイルを手書きする必要はありません。

## 対応メッセージ

| msg_type | 規格            | 内容                             |
| -------- | --------------- | -------------------------------- |
| 43       | IS-QZSS-DCR-010 | JMA DC Report (QZQSM) — 全12種   |
| 44       | IS-QZSS-DCX-005 | DCX / CAMF (L-Alert, J-Alert 等) |

## 動作環境

| 項目            | 値                                          |
| --------------- | ------------------------------------------- |
| 主要ターゲット  | ESP32-C3 (FreeRTOS / Arduino framework)     |
| Arduino コア    | esp32 ≥ 3.x                                 |
| ホストテスト    | g++ -std=c++17 (Linux / macOS / WSL)        |
| GNSS モジュール | u-blox (UBX-RXM-SFRBX) / NMEA $QZQSM 出力機 |

[注意] AzaraCはC++17で記述されています。利用の際は，お使いのIDEのC++コンパイラ設定を17にしてください。標準設定だとC++11となっているボードが多く、本ライブラリ利用の際にコンパイルエラーが発生する可能性があります。

<!--
### IDF Component Manager（現在未対応）

```bash
idf.py add-dependency "A-vrice/azaraC"
```
-->

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

### NMEA ($QZQSM)

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

### UBX (RXM-SFRBX)

u-blox の設定:

```
CFG-MSGOUT-UBX_RXM_SFRBX_UART1 = 1
CFG-SIGNAL-QZSS_L1S_ENA        = 1
```

コードは NMEA と同じです。`Parser` が自動判別します。

### UNIX 時刻付き（発生時刻を解決）

```cpp
// SNTP 等で取得した UNIX 時刻を渡す
uint32_t now = (uint32_t)time(nullptr);
if (parser.feed(byte, msg, now)) { ... }
```

詳細は `examples/with_sntp/` を参照。

---

## API

### `azaraC::Parser`

```cpp
// 1バイト投入。新しい有効メッセージが揃ったら true を返す
bool feed(uint8_t byte, Message& out, uint32_t now_unix = 0);

void reset();  // フレーマ・重複フィルタをリセット
```

重複除去は **{svid, msg_type, crc24}** のリングバッファで行います。
デフォルトスロット数は 8。複数 SV を受信する場合は増やしてください:

```cpp
#define AZARAC_DEDUP_SLOTS 16
#include <azaraC.h>
```

### `azaraC::toJson(msg, out)`

`Message` を JSON にシリアライズして任意の `Print&` に出力します。
`Serial` / `WiFiClient` / `StringPrint`（テスト用）などを渡せます。

### `azaraC::Message`

```cpp
struct Message {
    uint8_t  svid;
    uint8_t  msg_type;   // 43 or 44
    uint32_t crc24;
    bool     valid;

    // MT=44 フィールド: dcx_type, a1_message_type, a2_country_code ...
    // MT=43 フィールド: report_classification, disaster_category,
    //                   information_type, event_time
    //                   + サブタイプ別フィールド (eew_*, seis_*, tsu_* ...)
};
```

フィールド詳細は `src/Message.h` を参照してください。

---

## JSON 出力例

### MT=43 EEW

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

### MT=44 DCX (L-Alert)

```json
{
  "svid": 193,
  "msg_type": 44,
  "crc24": 11259375,
  "dcx_type": 1,
  "a1_msg_type": 2,
  "a1_msg_type_label": "Alert",
  "a2_country": 111,
  "a2_country_label": "Japan",
  "a4_hazard": 1,
  "a4_hazard_category": "Geological",
  "a4_hazard_type": "Earthquake",
  "a5_severity": 3,
  "a5_severity_label": "Extreme",
  "onset_time": { "day": 0, "hour": 14, "min": 30, "unix": 1745123400 },
  "lat_e2": 356,
  "lon_e2": 1396
}
```

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

## ライセンス

MIT

---

## 謝辞

メッセージ定義は [azarashi](https://github.com/nbtk/azarashi) (MIT) の
`definition/*.py` をもととさせていただきました。
また，ビット構造の解析の参照実装としてもazarashiのデコーダを参照させていただきました。

## Acknowledgements

The original project `azarashi` was developed by [NBTK](https://github.com/nbtk) during his time at BitMeister Inc., with support and resources generously provided by the company.

AzaraC is maintained independently by [A-vrice](https://github.com/A-vrice).
