// azaraC — examples/basic_ubx/basic_ubx.ino
//
// UBX-RXM-SFRBX (binary) → JSON on Serial (USB)
//
// Wiring (ESP32-C3 DevKitM-1):
//   u-blox TX → GPIO20 (Serial1 RX)
//   u-blox RX → GPIO21 (Serial1 TX)
//   GND       → GND
//
// u-blox config required:
//   CFG-MSGOUT-UBX_RXM_SFRBX_UART1 = 1
//   CFG-SIGNAL-QZSS_L1S_ENA        = 1
//   CFG-UART1-BAUDRATE              = 9600

// #define AZARAC_DEDUP_SLOTS 16   // increase if using multiple SVs
#include <azaraC.h>

azaraC::Parser  parser;
azaraC::Message msg;

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] ready, waiting for UBX-RXM-SFRBX..."));
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
