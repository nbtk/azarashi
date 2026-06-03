// azaraC — examples/error_handling/error_handling.ino
//
// エラーハンドリングと状態監視の例
// CRCエラー、フレームエラー、重複排除の統計を表示する
//
// Wiring (ESP32-C3 DevKitM-1):
//   GNSS TX → GPIO20 (Serial1 RX)
//   GNSS RX → GPIO21 (Serial1 TX)
//   GND     → GND

#include <azaraC.h>

azaraC::Parser  parser;
azaraC::Message msg;

// 統計カウンタ
struct Statistics {
    uint32_t total_messages = 0;      // 受信メッセージ総数
    uint32_t valid_messages = 0;      // 有効メッセージ数
    uint32_t duplicate_messages = 0;  // 重複メッセージ数
    uint32_t mt43_count = 0;          // MT=43 メッセージ数
    uint32_t mt44_count = 0;          // MT=44 メッセージ数
    uint32_t last_svid = 0;           // 最後に受信したSVID
    uint32_t last_report_time = 0;    // 最後に受信した時刻
};

Statistics stats;

// 統計情報を表示
void printStatistics() {
    Serial.println(F("=== azaraC Statistics ==="));
    Serial.print(F("Total messages:    "));
    Serial.println(stats.total_messages);
    Serial.print(F("Valid messages:    "));
    Serial.println(stats.valid_messages);
    Serial.print(F("Duplicate skipped: "));
    Serial.println(stats.duplicate_messages);
    Serial.print(F("MT=43 (QZQSM):     "));
    Serial.println(stats.mt43_count);
    Serial.print(F("MT=44 (DCX):       "));
    Serial.println(stats.mt44_count);
    Serial.print(F("Last SVID:         "));
    Serial.println(stats.last_svid);
    Serial.print(F("Valid ratio:       "));
    if (stats.total_messages > 0) {
        Serial.print((stats.valid_messages * 100) / stats.total_messages);
        Serial.println(F("%"));
    } else {
        Serial.println(F("N/A"));
    }
    Serial.println(F("========================"));
}

// メッセージの妥当性チェック
bool validateMessage(const azaraC::Message& msg) {
    // 基本的な妥当性チェック
    if (!msg.valid) {
        Serial.println(F("[WARN] Invalid message flag"));
        return false;
    }

    // SVIDの範囲チェック (QZSS: 193-202)
    if (msg.svid < 193 || msg.svid > 202) {
        Serial.print(F("[WARN] Unexpected SVID: "));
        Serial.println(msg.svid);
        // 警告のみで処理は続行
    }

    // msg_typeのチェック
    if (msg.msg_type != 43 && msg.msg_type != 44) {
        Serial.print(F("[ERROR] Unknown msg_type: "));
        Serial.println(msg.msg_type);
        return false;
    }

    return true;
}

// MT=43 メッセージの詳細バリデーション
bool validateMt43(const azaraC::Message& msg) {
    const azaraC::Mt43Data* mt43 = msg.getMt43();
    if (!mt43) {
        Serial.println(F("[ERROR] Failed to get MT43 data"));
        return false;
    }

    // disaster_categoryの範囲チェック
    bool valid_category = false;
    switch (mt43->disaster_category) {
        case 1: case 2: case 3: case 4: case 5: case 6:
        case 8: case 9: case 10: case 11: case 12: case 14:
            valid_category = true;
            break;
        default:
            Serial.print(F("[WARN] Unknown disaster_category: "));
            Serial.println(mt43->disaster_category);
            break;
    }

    // 日付の妥当性チェック
    if (mt43->event_time.month > 12) {
        Serial.print(F("[WARN] Invalid month: "));
        Serial.println(mt43->event_time.month);
    }
    if (mt43->event_time.day > 31) {
        Serial.print(F("[WARN] Invalid day: "));
        Serial.println(mt43->event_time.day);
    }
    if (mt43->event_time.hour > 23) {
        Serial.print(F("[WARN] Invalid hour: "));
        Serial.println(mt43->event_time.hour);
    }
    if (mt43->event_time.minute > 59) {
        Serial.print(F("[WARN] Invalid minute: "));
        Serial.println(mt43->event_time.minute);
    }

    return true;
}

// MT=44 メッセージの詳細バリデーション
bool validateMt44(const azaraC::Message& msg) {
    const azaraC::Mt44Data* mt44 = msg.getMt44();
    if (!mt44) {
        Serial.println(F("[ERROR] Failed to get MT44 data"));
        return false;
    }

    // service_kindのチェック
    switch (mt44->service_kind) {
        case azaraC::Mt44ServiceKind::LAlert:
        case azaraC::Mt44ServiceKind::JAlert:
        case azaraC::Mt44ServiceKind::LocalGovernment:
        case azaraC::Mt44ServiceKind::OutsideJapan:
        case azaraC::Mt44ServiceKind::NullMessage:
            break;
        default:
            Serial.print(F("[WARN] Unknown service_kind"));
            break;
    }

    return true;
}

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] error_handling ready"));
    Serial.println(F("Waiting for QZSS messages..."));
}

void loop() {
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        // バイト受信のデバッグ出力（必要時はコメント解除）
        // Serial.printf("%02X ", b);

        if (parser.feed(b, msg)) {
            stats.total_messages++;
            stats.last_svid = msg.svid;

            // 基本的な妥当性チェック
            if (!validateMessage(msg)) {
                Serial.println(F("[ERROR] Message validation failed"));
                continue;
            }

            stats.valid_messages++;

            // メッセージタイプ別の処理
            if (msg.msg_type == 43) {
                stats.mt43_count++;
                if (!validateMt43(msg)) {
                    Serial.println(F("[WARN] MT43 validation warning"));
                }
            } else if (msg.msg_type == 44) {
                stats.mt44_count++;
                if (!validateMt44(msg)) {
                    Serial.println(F("[WARN] MT44 validation warning"));
                }
            }

            // JSON出力
            azaraC::toJson(msg, Serial);
            Serial.println();

            // 10メッセージごとに統計を表示
            if (stats.total_messages % 10 == 0) {
                printStatistics();
            }
        }
    }

    // 5秒ごとにハートビートを出力（受信がない場合）
    static uint32_t last_heartbeat = 0;
    uint32_t now = millis();
    if (now - last_heartbeat > 5000) {
        last_heartbeat = now;
        if (stats.total_messages == 0) {
            Serial.println(F("[INFO] Waiting for messages..."));
        }
    }
}
