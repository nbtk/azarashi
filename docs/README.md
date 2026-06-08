<img src="https://raw.githubusercontent.com/A-vrice/azaraC/refs/heads/main/logo.png" width="256">

# AzaraC

A QZSS DCR DCX Decoder for Arduino.

## Description

AzaraCは準天頂衛星みちびきが送信する災危通報メッセージのデコーダーであるazarashiをArduino向けに移植したものです。QZSS L1S信号を用いた災危通報の**DCX/CAMF**(MT=44)および**DC Report/QZQSM**(MT=43)に対応しており，ESP32シリーズなどのArduino互換ボード向けに設計されています。外部ライブラリには依存していません。

定義テーブル(`definition/*.h`)は[azarashi](https://github.com/nbtk/azarashi)の`definition/*.py`からGitHub Actionsでの自動生成を行っています。

## 対応メッセージ

| msg_type | 規格            | 内容                             |
| -------- | --------------- | -------------------------------- |
| 43       | IS-QZSS-DCR-016 | JMA DC Report (QZQSM) — 全12種   |
| 44       | IS-QZSS-DCX-003 | DCX / CAMF (L-Alert, J-Alert 等) |

### MT=43 防災カテゴリ一覧

| カテゴリID | 内容                              |
| ---------- | --------------------------------- |
| 1          | 緊急地震速報 (EEW)                |
| 2          | 震源情報 (Hypocenter)             |
| 3          | 震度情報 (Seismic Intensity)      |
| 4          | 南海トラフ地震 (Nankai Trough)    |
| 5          | 津波警報・注意報 (Tsunami)        |
| 6          | 北太平洋津波 (NW Pacific Tsunami) |
| 8          | 火山情報 (Volcano)                |
| 9          | 降灰情報 (Ash Fall)               |
| 10         | 気象警報・注意報 (Weather)        |
| 11         | 洪水警報 (Flood)                  |
| 12         | 台風情報 (Typhoon)                |
| 14         | 海上警報 (Marine)                 |

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

> **注意:** AzaraCはC++17で記述されています。IDEのC++コンパイラ設定を17以上にしてください。

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

### UNIX時刻付き

```cpp
uint32_t now = (uint32_t)time(nullptr);
if (parser.feed(byte, msg, now)) { ... }
```

詳細は[`examples/with_sntp/`](examples/with_sntp/)を参照。

---

## API

詳細なAPIリファレンスは[api-reference.md](docs/api-reference.md)を参照してください。

### コンパイル時設定

| マクロ               | デフォルト | 説明                               |
| -------------------- | ---------- | ---------------------------------- |
| `AZARAC_DEDUP_SLOTS` | 8          | 重複除去リングバッファのスロット数 |
| `AZARAC_LANG_JA`     | 1          | 日本語ラベルを有効化               |
| `AZARAC_LANG_EN`     | 0          | 英語ラベルを有効化                 |

```cpp
#define AZARAC_DEDUP_SLOTS 16
#define AZARAC_LANG_JA 1
#define AZARAC_LANG_EN 1
#include <azaraC.h>
```

---

## JSON 出力例

### MT=43 EEW (緊急地震速報)

```json
{
  "svid": 193,
  "msg_type": 43,
  "report_classification_label": "警報",
  "disaster_category_label": "緊急地震速報",
  "detail": {
    "depth": 60,
    "magnitude": 65,
    "epicenter_label": "千葉県北西部",
    "intensity_lower_label": "5弱",
    "intensity_upper_label": "6強"
  }
}
```

### MT=44 DCX (L-Alert)

```json
{
  "svid": 193,
  "msg_type": 44,
  "service_kind_label": "L_ALERT",
  "a4_hazard_type": "Earthquake",
  "a5_severity_label": "Extreme",
  "main_ellipse": {
    "lat_deg": 35.6,
    "lon_deg": 139.6,
    "semi_major_km": 10.933,
    "semi_minor_km": 8.085
  }
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

## テスト

```bash
make -C test run
```

詳細は[developer-guide.md](docs/developer-guide.md)を参照してください。

---

## 仕様書リファレンス

| 規格            | 内容                        | バージョン     |
| --------------- | --------------------------- | -------------- |
| IS-QZSS-DCR-016 | DC Report Service (MT=43)   | April 03, 2026 |
| IS-QZSS-DCX-003 | DCX Service (MT=44)         | March 28, 2025 |
| EWSS CAMF v1.1  | Common Alert Message Format | Version 1.1    |

---

## ドキュメント

| ドキュメント                              | 内容                                 |
| ----------------------------------------- | ------------------------------------ |
| [API リファレンス](docs/api-reference.md) | 詳細なAPI仕様                        |
| [アーキテクチャ](docs/architecture.md)    | 内部設計とデータフロー               |
| [開発者ガイド](docs/developer-guide.md)   | ビルド方法、テスト、コーディング規約 |

---

## ライセンス

MIT

---

## 謝辞

メッセージ定義は [azarashi](https://github.com/nbtk/azarashi)(MIT)の
`definition/*.py` をもととさせていただきました。

## Acknowledgements

The original project `azarashi` was developed by [NBTK](https://github.com/nbtk) during his time at BitMeister Inc., with support and resources generously provided by the company.

AzaraC is maintained independently by [A-vrice](https://github.com/A-vrice).

## 不具合など

何か不具合、疑問点があれば[Issue](https://github.com/A-vrice/azaraC/issues)，作者メールアドレス[AzaraC@vrice.f5.si]，およびTwitter(現X)のDMまでお願いします。
