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

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] ready, waiting for $QZQSM..."));
}

void loop() {
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        // (Optional) Pass current UNIX time to resolve absolute timestamps
        // uint32_t now = (uint32_t)time(nullptr);
        uint32_t now = 0;

        if (parser.feed(b, msg, now)) {
            azaraC::toJson(msg, Serial);
            Serial.println();
        }
    }
}
