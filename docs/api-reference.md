# AzaraC API リファレンス

## 名前空間

すべてのAPIは `azaraC` 名前空間に含まれています。

```cpp
#include <azaraC.h>

// 名前空間の使用
using namespace azaraC;
// または
azaraC::Parser parser;
```

---

## クラスリファレンス

### `azaraC::Parser`

メインのパーサークラス。GNSSモジュールからのバイトストリームを処理し、デコード済みメッセージを出力します。

#### コンストラクタ

```cpp
// デフォルトコンストラクタ (UBX/NMEA自動判別)
Parser();

// カスタムフレーマーを使用する場合
explicit Parser(internal::IFramer& framer);
```

#### メソッド

##### `feed()`

1バイトずつデータを投入し、メッセージが完成したかどうかを返します。

```cpp
bool feed(uint8_t byte, Message& out, uint32_t report_unix = 0);
```

**パラメータ:**
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `byte` | `uint8_t` | GNSSモジュールからの1バイト |
| `out` | `Message&` | 出力メッセージ (戻り値がtrueの場合に有効) |
| `report_unix` | `uint32_t` | UNIX時刻 (省略時: 0 = 未解決) |

**戻り値:** `bool` - 新しいメッセージが完成した場合に `true`

**使用例:**
```cpp
azaraC::Parser parser;
azaraC::Message msg;

void loop() {
    while (Serial1.available()) {
        uint8_t byte = Serial1.read();
        uint32_t now = (uint32_t)time(nullptr); // SNTPから取得
        
        if (parser.feed(byte, msg, now)) {
            // メッセージ受信完了
            processMessage(msg);
        }
    }
}
```

##### `reset()`

パーサーの状態をリセットします。フレーマー、デコーダー、重複除去フィルタが初期化されます。

```cpp
void reset();
```

##### `getNankaiBuffer()`

南海トラフメッセージのページ集約バッファを取得します。

```cpp
const internal::NankaiPageBuffer* getNankaiBuffer(const internal::NankaiPageKey& key) const;
```

---

### `azaraC::Message`

デコード済みメッセージを格納する構造体。

#### 共通フィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `svid` | `uint8_t` | 衛星ID (QZSS: 193-202) |
| `msg_type` | `uint8_t` | メッセージタイプ (43=QZQSM, 44=DCX) |
| `crc24` | `uint32_t` | CRC-24Qチェックサム |
| `valid` | `bool` | メッセージの妥当性フラグ |
| `payload_type` | `MsgPayloadType` | ペイロードタイプ |

#### 安全なアクセサ

```cpp
// MT=43 データへのアクセス
const Mt43Data* getMt43() const;

// MT=44 データへのアクセス
const Mt44Data* getMt44() const;
```

**使用例:**
```cpp
void processMessage(const azaraC::Message& msg) {
    if (msg.msg_type == 43) {
        const azaraC::Mt43Data* mt43 = msg.getMt43();
        if (mt43) {
            uint8_t category = mt43->disaster_category;
            // MT=43 固有の処理
        }
    } else if (msg.msg_type == 44) {
        const azaraC::Mt44Data* mt44 = msg.getMt44();
        if (mt44) {
            auto kind = mt44->service_kind;
            // MT=44 固有の処理
        }
    }
}
```

---

### `azaraC::Mt43Data` (MT=43 QZQSM)

JMA DC Reportメッセージのデータ構造。

#### 共通フィールド

| フィールド | 型 | ビット位置 | 説明 |
|-----------|-----|-----------|------|
| `report_classification` | `uint8_t` | [14..16] | 報告分類 (3bits) |
| `disaster_category` | `uint8_t` | [17..20] | 災害カテゴリ (4bits) |
| `information_type` | `uint8_t` | [41..42] | 情報種別 (2bits) |
| `event_time` | `TimeFields` | [25..40] | イベント日時 |

#### 災害カテゴリ

| カテゴリID | 名称 | データ構造 |
|-----------|------|-----------|
| 1 | 緊急地震速報 (EEW) | `EewData eew` |
| 2 | 震源情報 | `HypocenterData hypo` |
| 3 | 震度情報 | `SeismicData seis` |
| 4 | 南海トラフ地震 | `NankaiData nankai` |
| 5 | 津波警報・注意報 | `TsunamiData tsunami` |
| 6 | 北太平洋津波 | `NwPacTsunamiData nw_pac` |
| 8 | 火山情報 | `VolcanoData vol` |
| 9 | 降灰情報 | `AshFallData ash` |
| 10 | 気象警報・注意報 | `WeatherData wx` |
| 11 | 洪水警報 | `FloodData flood` |
| 12 | 台風情報 | `TyphoonData typh` |
| 14 | 海上警報 | `MarineData marine` |

#### EEWデータ (`EewData`)

```cpp
struct EewData {
    uint8_t  long_period_lower;   // 長周期地震動下限 (3bits)
    uint8_t  long_period_upper;   // 長周期地震動上限 (3bits)
    uint16_t notification[3];     // 防災気象情報通知 (3×9bits)
    uint8_t  notification_count;  // 通知数
    TimeFields quake_time;        // 発震時刻
    uint16_t depth;               // 震源の深さ (×10km)
    uint8_t  magnitude;           // マグニチュード (×0.1)
    uint16_t epicenter;           // 震央地名コード
    uint8_t  intensity_lower;     // 震度下限 (4bits)
    uint8_t  intensity_upper;     // 震度上限 (4bits)
    uint8_t  regions[80];         // 地域別フラグ
    uint8_t  region_count;        // 地域数
};
```

#### 台風データ (`TyphoonData`)

```cpp
struct TyphoonData {
    TimeFields reference_time;  // 基準時刻
    uint8_t    ref_type;        // 参照時刻種別 (1:Analysis 2:Estimate 3:Forecast)
    uint8_t    elapsed;         // 経過時間 (時間)
    uint8_t    number;          // 台風番号
    uint8_t    scale;           // 大きさ (4bits)
    uint8_t    intensity;       // 強さ (4bits)
    LatLon     coords;          // 台風位置
    uint16_t   pressure;        // 中心気圧 (hPa)
    uint8_t    max_wind;        // 最大風速 (m/s)
    uint8_t    max_gust;        // 最大瞬間風速 (m/s)
};
```

---

### `azaraC::Mt44Data` (MT=44 DCX/CAMF)

DCX/CAMFメッセージのデータ構造。

#### 共通フィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `service_kind` | `Mt44ServiceKind` | サービス種別 |
| `is_null_message` | `bool` | Null Messageフラグ |
| `sd` | `Mt44Sd` | 送信元情報 |
| `camf` | `Mt44CamfRaw` | CAMFフィールド (Raw) |
| `onset_time` | `TimeFields` | ハザード発生日時 |
| `ex_kind` | `ExtendedKind` | 拡張メッセージ種別 |
| `mt44_decoded` | `Mt44Decoded` | デコード済み情報 |

#### サービス種別 (`Mt44ServiceKind`)

| 値 | 名称 | 説明 |
|---|------|------|
| `NullMessage` | Null Message | A1=0 |
| `LAlert` | L-Alert | A2=111, A3=1-4 |
| `JAlert` | J-Alert | A2=111, A3=0 |
| `LocalGovernment` | 地方自治体 | A2=111, A3=5-31 |
| `OutsideJapan` | 国外 | A2≠111 |
| `Unknown` | 不明 | 上記以外 |

#### CAMFフィールド (`Mt44CamfRaw`)

| フィールド | 型 | ビット数 | 説明 |
|-----------|-----|---------|------|
| `a1` | `uint8_t` | 2 | メッセージ種別 |
| `a2` | `uint16_t` | 9 | 国/地域コード |
| `a3` | `uint8_t` | 5 | プロバイダID |
| `a4` | `uint8_t` | 7 | ハザード種別 |
| `a5` | `uint8_t` | 2 | 深刻度 |
| `a6` | `uint8_t` | 1 | 週コード |
| `a7` | `uint16_t` | 14 | 発生日時 |
| `a8` | `uint8_t` | 2 | ハザード継続時間 |
| `a9` | `uint8_t` | 1 | ライブラリ選択 |
| `a10` | `uint8_t` | 3 | ライブラリバージョン |
| `a11` | `uint16_t` | 10 | 国際/国内ライブラリコード |
| `a12` | `uint16_t` | 16 | 緯度コード |
| `a13` | `uint32_t` | 17 | 経度コード |
| `a14` | `uint8_t` | 5 | 長半径 |
| `a15` | `uint8_t` | 5 | 短半径 |
| `a16` | `uint8_t` | 6 | 方位角 |
| `a17` | `uint8_t` | 2 | 拡張フィールド種別 |
| `a18` | `uint16_t` | 15 | 拡張データ |

#### A17 拡張フィールド (EWSS CAMF v1.1)

| A17値 | 名称 | 説明 |
|-------|------|------|
| 00 | B1 | Improved Resolution of Main Ellipse |
| 01 | B2 | Hazard Center Position |
| 10 | B3 | Secondary Ellipse Definition |
| 11 | B4 | Quantitative and Detailed Information |

#### デコード済み楕円 (`DecodedEllipse`)

```cpp
struct DecodedEllipse {
    double lat_deg;         // 緯度 (WGS84)
    double lon_deg;         // 経度 (WGS84)
    double semi_major_km;   // 長半径 (km)
    double semi_minor_km;   // 短半径 (km)
    double azimuth_deg;     // 方位角 (度)
    
    // B1 リファインメント値
    double b1_lat_offset_deg;    // 緯度補正オフセット
    double b1_lon_offset_deg;    // 経度補正オフセット
    double b1_major_factor;      // 長半径補間係数
    double b1_minor_factor;      // 短半径補間係数
};
```

---

### `azaraC::TimeFields`

日時情報を格納する構造体。

```cpp
struct TimeFields {
    uint8_t  month;      // 月 (1-12, 0=未解決)
    uint8_t  day;        // 日 (1-31, 0=未解決)
    uint8_t  hour;       // 時 (0-23)
    uint8_t  minute;     // 分 (0-59)
    uint32_t unix_time;  // UNIX時刻 (0=未解決)
};
```

---

### `azaraC::LatLon`

緯度経度情報を格納する構造体。

```cpp
struct LatLon {
    uint8_t  lat_ns;    // 北緯/南緯 (0=N, 1=S)
    uint8_t  lat_deg;   // 緯度度 (0-89)
    uint8_t  lat_min;   // 緯度分 (0-59)
    uint8_t  lat_sec;   // 緯度秒 (0-59)
    uint8_t  lon_ew;    // 東経/西経 (0=E, 1=W)
    uint16_t lon_deg;   // 経度度 (0-179)
    uint8_t  lon_min;   // 経度分 (0-59)
    uint8_t  lon_sec;   // 経度秒 (0-59)
};
```

---

## グローバル関数

### `toJson()`

MessageをJSON形式で出力します。

```cpp
void toJson(const Message& msg, Print& out);
```

**パラメータ:**
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `msg` | `const Message&` | シリアライズするメッセージ |
| `out` | `Print&` | 出力先 (Serial, WiFiClient等) |

**使用例:**
```cpp
// Serialに出力
azaraC::toJson(msg, Serial);
Serial.println();

// WiFiClientに出力
WiFiClient client;
if (client.connect(server, port)) {
    azaraC::toJson(msg, client);
    client.println();
}
```

---

## コンパイル時設定

ライブラリのインクルード前に定義できるマクロです。

| マクロ | デフォルト | 説明 |
|-------|-----------|------|
| `AZARAC_DEDUP_SLOTS` | 8 | 重複除去リングバッファのスロット数 |
| `AZARAC_LANG_JA` | 1 | 日本語ラベルを有効化 |
| `AZARAC_LANG_EN` | 0 | 英語ラベルを有効化 |

```cpp
// カスタム設定例
#define AZARAC_DEDUP_SLOTS 32
#define AZARAC_LANG_JA 1
#define AZARAC_LANG_EN 1
#include <azaraC.h>
```

---

## 内部インターフェース

### `azaraC::internal::IFramer`

カスタムフレーマーを実装するためのインターフェース。

```cpp
class IFramer {
public:
    virtual bool feed(uint8_t byte, Frame& out) = 0;
    virtual void reset() = 0;
    virtual ~IFramer() = default;
};
```

**実装例:**
```cpp
class MyFramer : public azaraC::internal::IFramer {
public:
    bool feed(uint8_t byte, azaraC::internal::Frame& out) override {
        // フレーミング処理
        // フレーム完成時: return true
        return false;
    }
    
    void reset() override {
        // 状態リセット
    }
};
```

---

## エラーコード

### MT=44 パース結果コード

| コード | 名称 | 説明 |
|-------|------|------|
| 001 | `INVALID_PAB` | 不正なPAB |
| 002 | `INVALID_MT` | 不正なMT |
| 003 | `INVALID_SD` | 不正なSD |
| 004 | `INVALID_CAMF` | 不正なCAMF |
| 005 | `INVALID_EX` | 不正な拡張フィールド |
| 006 | `INVALID_CRC` | CRC不一致 |
| 007 | `INVALID_LENGTH` | 不正な長さ |
| 100 | `SUCCESS` | 成功 |
| 101-109 | `WARN_*` | 警告 (処理は継続) |

---

## 使用パターン

### 基本的な使用パターン

```cpp
#include <azaraC.h>

azaraC::Parser parser;
azaraC::Message msg;

void setup() {
    Serial.begin(115200);
    Serial1.begin(9600, SERIAL_8N1, 20, 21);
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

### エラーハンドリング付きパターン

```cpp
void processMessage(const azaraC::Message& msg) {
    // 基本的な妥当性チェック
    if (!msg.valid) {
        Serial.println(F("[WARN] Invalid message"));
        return;
    }
    
    // SVID範囲チェック
    if (msg.svid < 193 || msg.svid > 202) {
        Serial.print(F("[WARN] Unexpected SVID: "));
        Serial.println(msg.svid);
    }
    
    // メッセージタイプ別処理
    if (msg.msg_type == 43) {
        const azaraC::Mt43Data* mt43 = msg.getMt43();
        if (mt43 && mt43->disaster_category == 1) {
            // EEW処理
            handleEEW(*mt43);
        }
    }
}
```

### SNTP時刻解決付きパターン

```cpp
#include <WiFi.h>
#include <azaraC.h>

const char* ssid = "YOUR_SSID";
const char* pass = "YOUR_PASS";

azaraC::Parser parser;
azaraC::Message msg;

void setup() {
    Serial.begin(115200);
    Serial1.begin(9600, SERIAL_8N1, 20, 21);
    
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) delay(500);
    
    configTime(9 * 3600, 0, "ntp.nict.jp"); // JST
}

void loop() {
    uint32_t now = (uint32_t)time(nullptr);
    
    while (Serial1.available()) {
        if (parser.feed(Serial1.read(), msg, now)) {
            azaraC::toJson(msg, Serial);
            Serial.println();
        }
    }
}
```

---

## 関連ドキュメント

- [アーキテクチャドキュメント](architecture.md)
- [開発者ガイド](developer-guide.md)
