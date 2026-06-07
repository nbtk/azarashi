// azaraC — examples/basic_nmea/basic_nmea.ino
//
// NMEA $QZQSM (9600 baud) → JSON on Serial (USB)
//
// Wiring (ESP32-C3 DevKitM-1):
//   GNSS TX → GPIO20 (Serial1 RX)
//   GNSS RX → GPIO21 (Serial1 TX)  [optional, for config]
//   GND     → GND
//
// Tested with: u-blox M10 / ZED-F9P (L1S enabled), Furuno GT-87

#include <azaraC.h>

azaraC::Parser  parser;
azaraC::Message msg;

// GNSSから取得した最新のUNIX時刻をキャッシュする変数
// (TinyGPS++ などを併用して $GPRMC や $GPZDA から取得・更新する想定)
uint32_t cached_gnss_unix_time = 0;

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] ready, waiting for $QZQSM..."));
}

void loop() {
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        // TinyGPS++ 等で NMEA をパースして時刻が更新されたら、
        // cached_gnss_unix_time = ... と更新する想定。

        // 第3引数 now_unix に最新の時刻を渡すことで、DCR/DCX電文の「年」を正確に算出できます。
        // 未同期時 (now_unix = 0) の場合、年は解決されませんが、
        // 電文の生データ (月・日・時・分) は正しく取得・出力されます。
        if (parser.feed(b, msg, cached_gnss_unix_time)) {
            azaraC::toJson(msg, Serial);
            Serial.println();
        }
    }
}
