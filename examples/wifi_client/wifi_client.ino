// azaraC — examples/wifi_client/wifi_client.ino
//
// Wi-FiクライアントとしてJSONメッセージをTCPサーバーに送信する例
// MQTTブローカーやHTTPエンドポイントにメッセージを転送する用途に適する
//
// 必要な設定:
//   - WIFI_SSID: Wi-Fiネットワーク名
//   - WIFI_PASS: Wi-Fiパスワード
//   - SERVER_HOST: 送信先サーバーアドレス
//   - SERVER_PORT: 送信先ポート番号
//
// Wiring (ESP32-C3 DevKitM-1):
//   GNSS TX → GPIO20 (Serial1 RX)
//   GNSS RX → GPIO21 (Serial1 TX)
//   GND     → GND

#include <azaraC.h>
#include <WiFi.h>

// ===== 設定 =====
#ifndef WIFI_SSID
  #define WIFI_SSID "YOUR_SSID"
#endif
#ifndef WIFI_PASS
  #define WIFI_PASS "YOUR_PASS"
#endif
#ifndef SERVER_HOST
  #define SERVER_HOST "192.168.1.100"
#endif
#ifndef SERVER_PORT
  #define SERVER_PORT 1883
#endif
// ================

azaraC::Parser  parser;
azaraC::Message msg;
WiFiClient wifiClient;

// 再接続管理
uint32_t lastReconnectAttempt = 0;
const uint32_t RECONNECT_INTERVAL = 5000;

// Wi-Fi接続
void connectWiFi() {
    Serial.print(F("[wifi] connecting to "));
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10) {
        delay(500);
        Serial.print(F("."));
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(F(" OK"));
        Serial.print(F("[wifi] IP: "));
        Serial.println(WiFi.localIP());
    } else {
        Serial.println(F(" FAILED"));
    }
}

// TCPサーバー接続
bool connectServer() {
    if (wifiClient.connected()) {
        return true;
    }

    Serial.print(F("[tcp] connecting to "));
    Serial.print(SERVER_HOST);
    Serial.print(F(":"));
    Serial.println(SERVER_PORT);

    if (wifiClient.connect(SERVER_HOST, SERVER_PORT)) {
        Serial.println(F("[tcp] connected"));
        return true;
    } else {
        Serial.println(F("[tcp] connection failed"));
        return false;
    }
}

// JSONをWiFiClientに送信
bool sendJson(const azaraC::Message& msg) {
    if (!wifiClient.connected()) {
        return false;
    }

    // カスタムPrintクラス: WiFiClientに出力
    class WifiPrint : public Print {
    public:
        WiFiClient& client;
        WifiPrint(WiFiClient& c) : client(c) {}
        size_t write(uint8_t c) override { return client.write(c); }
        size_t write(const uint8_t* buf, size_t len) override { return client.write(buf, len); }
    };

    WifiPrint wifiPrint(wifiClient);
    azaraC::toJson(msg, wifiPrint);
    wifiPrint.println();

    return true;
}

// ステータスLED制御（ESP32-C3 DevKitM-1内蔵LED）
void setStatusLED(bool on) {
    // ESP32-C3 DevKitM-1: GPIO8 (active low)
    static bool initialized = false;
    if (!initialized) {
        pinMode(8, OUTPUT);
        initialized = true;
    }
    digitalWrite(8, on ? LOW : HIGH);
}

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println(F("[azaraC] wifi_client ready"));

    // Wi-Fi接続
    connectWiFi();

    // GNSSシリアル開始
    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
}

void loop() {
    // Wi-Fi接続確認
    if (WiFi.status() != WL_CONNECTED) {
        setStatusLED(false);
        uint32_t now = millis();
        if (now - lastReconnectAttempt > RECONNECT_INTERVAL) {
            lastReconnectAttempt = now;
            connectWiFi();
        }
    } else {
        setStatusLED(true);
    }

    // TCP接続確認
    if (WiFi.status() == WL_CONNECTED) {
        connectServer();
    }

    // メッセージ受信処理
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        if (parser.feed(b, msg)) {
            // Serialにも出力
            azaraC::toJson(msg, Serial);
            Serial.println();

            // WiFi経由で送信
            if (sendJson(msg)) {
                Serial.println(F("[tcp] sent"));
            } else {
                Serial.println(F("[tcp] send failed (not connected)"));
            }
        }
    }
}
