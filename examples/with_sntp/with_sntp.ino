// azaraC — examples/with_sntp/with_sntp.ino
//
// Wi-Fi + SNTP で UNIX 時刻を取得し、DCR/DCX の発生時刻を解決する例
// disaster_category == 1 (EEW) のみ Serial に警告ログを出力するフィルタ付き

// #define AZARAC_DEDUP_SLOTS 16
#include <azaraC.h>
#include <WiFi.h>
#include <time.h>

// ── 設定 (必要に応じて書き換えてください) ──────────────────────────────────
// [重要] Wi-Fi 設定を自分の環境に合わせて書き換えてください
#ifndef WIFI_SSID
  #warning "Please ensure WIFI_SSID and WIFI_PASS are set correctly in with_sntp.ino"
  #define WIFI_SSID "YOUR_SSID" // <-- Change this
  #define WIFI_PASS "YOUR_PASS" // <-- Change this
#endif


// ── グローバル ───────────────────────────────────────────────────────────────
azaraC::Parser  parser;
azaraC::Message msg;

// ── setup ───────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    // Wi-Fi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print(F("[wifi] connecting"));
    while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print('.'); }
    Serial.println(F(" OK"));

    // SNTP (pool.ntp.org, JST+9)
    configTime(9 * 3600, 0, "pool.ntp.org", "time.cloudflare.com");
    Serial.print(F("[sntp] syncing"));
    struct tm ti{};
    while (!getLocalTime(&ti, 5000)) { Serial.print('.'); delay(1000); }
    Serial.println(F(" OK"));

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] ready"));
}

// ── loop ────────────────────────────────────────────────────────────────────
void loop() {
    while (Serial1.available()) {
        uint32_t now = static_cast<uint32_t>(time(nullptr));

        if (parser.feed(static_cast<uint8_t>(Serial1.read()), msg, now)) {
            // ── EEW のみ警告出力（他は通常 JSON）──────────────────────────
            if (msg.msg_type == 43 && msg.disaster_category == 1) {
                Serial.print(F("[EEW] epicenter="));
                Serial.print(msg.eew_epicenter);
                Serial.print(F(" mag="));
                Serial.print(msg.eew_magnitude / 10);
                Serial.print('.');
                Serial.print(msg.eew_magnitude % 10);
                Serial.print(F(" depth="));
                Serial.print(msg.eew_depth);
                Serial.println(F("km"));
            }

            // 全メッセージを JSON で Serial 出力
            azaraC::toJson(msg, Serial);
            Serial.println();
        }
    }
}
