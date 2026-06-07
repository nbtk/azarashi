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

// UBX-NAV-PVT メッセージ等から取得した最新のUNIX時刻をキャッシュする変数
uint32_t cached_gnss_unix_time = 0;

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] ready, waiting for UBX-RXM-SFRBX..."));
}

void loop() {
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        // UBX-NAV-PVT 等を別途パースして時刻が更新されたら、
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
