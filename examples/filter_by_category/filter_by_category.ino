// azaraC — examples/filter_by_category/filter_by_category.ino
//
// MT=43 防災カテゴリ別フィルタリングの例
// 特定の災害カテゴリのみをSerialに出力する
//
// 対応カテゴリ:
//   1  = 緊急地震速報 (EEW)
//   2  = 震源情報 (Hypocenter)
//   3  = 震度情報 (Seismic Intensity)
//   4  = 南海トラフ地震 (Nankai Trough)
//   5  = 津波警報・注意報 (Tsunami)
//   6  = 北太平洋津波 (NW Pacific Tsunami)
//   8  = 火山情報 (Volcano)
//   9  = 降灰情報 (Ash Fall)
//   10 = 気象警報・注意報 (Weather)
//   11 = 洪水警報 (Flood)
//   12 = 台風情報 (Typhoon)
//   14 = 海上警報 (Marine)
//
// Wiring (ESP32-C3 DevKitM-1):
//   GNSS TX → GPIO20 (Serial1 RX)
//   GNSS RX → GPIO21 (Serial1 TX)
//   GND     → GND

#include <azaraC.h>

azaraC::Parser  parser;
azaraC::Message msg;

// 出力したい災害カテゴリを設定（true = 出力する）
struct CategoryFilter {
    bool eew          = true;   // 1: 緊急地震速報
    bool hypocenter   = true;   // 2: 震源情報
    bool seismic      = true;   // 3: 震度情報
    bool nankai       = true;   // 4: 南海トラフ
    bool tsunami      = true;   // 5: 津波
    bool nw_pac_tsu   = false;  // 6: 北太平洋津波
    bool volcano      = true;   // 8: 火山
    bool ash_fall     = true;   // 9: 降灰
    bool weather      = false;  // 10: 気象
    bool flood        = true;   // 11: 洪水
    bool typhoon      = true;   // 12: 台風
    bool marine       = false;  // 14: 海上
};

CategoryFilter filter;

// 災害カテゴリのラベル（日本語）
const char* getCategoryLabel(uint8_t category) {
    switch (category) {
        case 1:  return "緊急地震速報";
        case 2:  return "震源情報";
        case 3:  return "震度情報";
        case 4:  return "南海トラフ";
        case 5:  return "津波";
        case 6:  return "北太平洋津波";
        case 8:  return "火山";
        case 9:  return "降灰";
        case 10: return "気象";
        case 11: return "洪水";
        case 12: return "台風";
        case 14: return "海上";
        default: return "不明";
    }
}

// フィルタリング判定
bool shouldOutput(uint8_t category) {
    switch (category) {
        case 1:  return filter.eew;
        case 2:  return filter.hypocenter;
        case 3:  return filter.seismic;
        case 4:  return filter.nankai;
        case 5:  return filter.tsunami;
        case 6:  return filter.nw_pac_tsu;
        case 8:  return filter.volcano;
        case 9:  return filter.ash_fall;
        case 10: return filter.weather;
        case 11: return filter.flood;
        case 12: return filter.typhoon;
        case 14: return filter.marine;
        default: return true; // 未知のカテゴリは常に出力
    }
}

// MT=43 カテゴリ別の詳細出力
void printMt43Details(const azaraC::Message& msg) {
    const azaraC::Mt43Data* mt43 = msg.getMt43();
    if (!mt43) return;

    switch (mt43->disaster_category) {
        case 1: { // EEW
            Serial.print(F("  震源: "));
            Serial.print(mt43->eew.epicenter);
            Serial.print(F(" マグニチュード: "));
            Serial.print(mt43->eew.magnitude / 10);
            Serial.print(F("."));
            Serial.print(mt43->eew.magnitude % 10);
            Serial.print(F(" 深さ: "));
            Serial.print(mt43->eew.depth);
            Serial.println(F("km"));
            break;
        }
        case 2: { // Hypocenter
            Serial.print(F("  震源: "));
            Serial.print(mt43->hypo.epicenter);
            Serial.print(F(" マグニチュード: "));
            Serial.print(mt43->hypo.magnitude / 10);
            Serial.print(F("."));
            Serial.print(mt43->hypo.magnitude % 10);
            break;
        }
        case 3: { // Seismic Intensity
            Serial.print(F("  観測地点数: "));
            Serial.println(mt43->seis.count);
            break;
        }
        case 5: { // Tsunami
            Serial.print(F("  警報コード: "));
            Serial.print(mt43->tsunami.warning_code);
            Serial.print(F(" 海域数: "));
            Serial.println(mt43->tsunami.count);
            break;
        }
        case 12: { // Typhoon
            Serial.print(F("  台風番号: "));
            Serial.print(mt43->typh.number);
            Serial.print(F(" 中心気圧: "));
            Serial.print(mt43->typh.pressure);
            Serial.print(F("hPa 最大風速: "));
            Serial.print(mt43->typh.max_wind);
            Serial.println(F("m/s"));
            break;
        }
        default:
            break;
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial1.begin(9600, SERIAL_8N1, /*rx=*/20, /*tx=*/21);
    Serial.println(F("[azaraC] filter_by_category ready"));
    Serial.println(F("出力カテゴリ:"));
    Serial.println(F("  [ON]  EEW, 震源, 震度, 南海トラフ, 津波, 火山, 降灰, 洪水, 台風"));
    Serial.println(F("  [OFF] 北太平洋津波, 気象, 海上"));
}

void loop() {
    while (Serial1.available()) {
        uint8_t b = static_cast<uint8_t>(Serial1.read());

        if (parser.feed(b, msg)) {
            if (msg.msg_type == 43) {
                const azaraC::Mt43Data* mt43 = msg.getMt43();
                if (mt43 && shouldOutput(mt43->disaster_category)) {
                    Serial.print(F("[MT43:"));
                    Serial.print(getCategoryLabel(mt43->disaster_category));
                    Serial.print(F("] SVID="));
                    Serial.print(msg.svid);
                    printMt43Details(msg);
                }
            } else if (msg.msg_type == 44) {
                // DCX メッセージは常に出力
                Serial.print(F("[MT44] SVID="));
                Serial.println(msg.svid);
                azaraC::toJson(msg, Serial);
                Serial.println();
            }
        }
    }
}
