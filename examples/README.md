# azaraC Examples

このディレクトリには、azaraCライブラリの使用例が含まれています。

## 目次

- [基本的な使用例](#基本的な使用例)
- [高度な使用例](#高度な使用例)
- [Example一覧](#example一覧)

---

## 基本的な使用例

### basic_nmea - NMEA $QZQSM 入力

NMEAフォーマットの$QZQSMメッセージを受信し、JSONに変換して出力します。

**対応ハードウェア**: u-blox M10, ZED-F9P, Furuno GT-87 など

```bash
# Arduino IDE で examples/basic_nmea/basic_nmea.ino を開いて書き込み
```

**配線 (ESP32-C3 DevKitM-1)**:
| GNSS | ESP32-C3 |
|------|----------|
| TX | GPIO20 |
| RX | GPIO21 |
| GND | GND |

---

### basic_ubx - UBX-RXM-SFRBX 入力

u-bloxバイナリフォーマットのUBX-RXM-SFRBXメッセージを受信します。

**必要なu-blox設定**:

```
CFG-MSGOUT-UBX_RXM_SFRBX_UART1 = 1
CFG-SIGNAL-QZSS_L1S_ENA        = 1
CFG-UART1-BAUDRATE              = 9600
```

```bash
# Arduino IDE で examples/basic_ubx/basic_ubx.ino を開いて書き込み
```

---

### with_sntp - SNTP時刻解決付き

Wi-FiとSNTPを使用してUNIX時刻を取得し、DCR/DCXメッセージの年を正確に解決します。

**機能**:

- Wi-Fi接続
- SNTP時刻同期
- EEW (disaster_category=1) フィルタリング
- DCXメッセージのサービス種別表示

**必要な設定**:

```cpp
#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASS "YOUR_PASS"
```

---

## 高度な使用例

### filter_by_category - カテゴリ別フィルタリング

MT=43メッセージを災害カテゴリ別にフィルタリングして出力します。

**対応カテゴリ**:

| カテゴリID | 内容               | デフォルト |
| ---------- | ------------------ | ---------- |
| 1          | 緊急地震速報 (EEW) | ON         |
| 2          | 震源情報           | ON         |
| 3          | 震度情報           | ON         |
| 4          | 南海トラフ地震     | ON         |
| 5          | 津波警報・注意報   | ON         |
| 6          | 北太平洋津波       | OFF        |
| 8          | 火山情報           | ON         |
| 9          | 降灰情報           | ON         |
| 10         | 気象警報・注意報   | OFF        |
| 11         | 洪水警報           | ON         |
| 12         | 台風情報           | ON         |
| 14         | 海上警報           | OFF        |

**フィルタ設定の変更**:

```cpp
// examples/filter_by_category/filter_by_category.ino の CategoryFilter を編集
CategoryFilter filter;
filter.eew = true;        // 緊急地震速報を出力
filter.weather = false;    // 気象警報を出力しない
```

---

### error_handling - エラーハンドリングと統計

メッセージの妥当性チェックと受信統計を表示します。

**機能**:

- メッセージ妥当性チェック (`msg.valid`)
- SVID範囲チェック (QZSS: 193-202)
- `disaster_category` 範囲チェック (MT=43)
- `service_kind` チェック (MT=44)
- 日付・時刻の妥当性チェック
- 受信統計の定期表示
- ハートビート出力（受信がない場合）

**バリデーション関数**:

```cpp
// 基本的な妥当性チェック
bool validateMessage(const azaraC::Message& msg) {
    if (!msg.valid) {
        Serial.println(F("[WARN] Invalid message flag"));
        return false;
    }
    // SVIDの範囲チェック (QZSS: 193-202)
    if (msg.svid < 193 || msg.svid > 202) {
        Serial.print(F("[WARN] Unexpected SVID: "));
        Serial.println(msg.svid);
    }
    return true;
}

// MT=43 メッセージの詳細バリデーション
bool validateMt43(const azaraC::Message& msg) {
    const azaraC::Mt43Data* mt43 = msg.getMt43();
    if (!mt43) return false;
    // disaster_categoryの範囲チェック
    // 日付の妥当性チェック
    // ...
}

// MT=44 メッセージの詳細バリデーション
bool validateMt44(const azaraC::Message& msg) {
    const azaraC::Mt44Data* mt44 = msg.getMt44();
    if (!mt44) return false;
    // service_kindのチェック
    // ...
}
```

**出力例**:

```
=== azaraC Statistics ===
Total messages:    50
Valid messages:    48
Duplicate skipped: 2
MT=43 (QZQSM):     30
MT=44 (DCX):       18
Last SVID:         193
Valid ratio:       96%
========================

[INFO] Heartbeat - Total: 50 Valid: 48
```

---

### wifi_client - Wi-Fiクライアント出力

JSONメッセージをTCPサーバーに送信します。

**用途**:

- MQTTブローカーへの転送
- HTTPエンドポイントへの送信
- リモートログサーバーへの転送

**必要な設定**:

```cpp
#define WIFI_SSID   "YOUR_SSID"
#define WIFI_PASS   "YOUR_PASS"
#define SERVER_HOST "192.168.1.100"
#define SERVER_PORT 1883
```

**カスタムPrintクラス例**:

```cpp
class WifiPrint : public Print {
public:
    WiFiClient& client;
    WifiPrint(WiFiClient& c) : client(c) {}
    size_t write(uint8_t c) override { return client.write(c); }
    size_t write(const uint8_t* buf, size_t len) override { return client.write(buf, len); }
};
```

---

## Example一覧

| Example            | 入力          | 出力                   | 特徴               |
| ------------------ | ------------- | ---------------------- | ------------------ |
| basic_nmea         | NMEA $QZQSM   | Serial JSON            | 最もシンプル       |
| basic_ubx          | UBX-RXM-SFRBX | Serial JSON            | u-bloxバイナリ     |
| with_sntp          | NMEA $QZQSM   | Serial JSON + フィルタ | SNTP時刻解決       |
| filter_by_category | NMEA/UBX      | Serial JSON            | カテゴリフィルタ   |
| error_handling     | NMEA/UBX      | Serial JSON + 統計     | エラーハンドリング |
| wifi_client        | NMEA/UBX      | Serial + TCP           | ネットワーク出力   |

---

## 共通の配線図

### ESP32-C3 DevKitM-1

```
GNSS Module          ESP32-C3 DevKitM-1
+--------+          +------------------+
| TX  ---+--------→ | GPIO20 (Serial1 RX)
| RX  ---+--------← | GPIO21 (Serial1 TX)
| GND ---+--------→ | GND
| VCC ---+--------→ | 3.3V
+--------+          +------------------+
```

### ピン配置のカスタマイズ

```cpp
// デフォルト (GPIO20, GPIO21)
Serial1.begin(9600, SERIAL_8N1, 20, 21);

// カスタムピン (例: GPIO10, GPIO11)
Serial1.begin(9600, SERIAL_8N1, 10, 11);
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
