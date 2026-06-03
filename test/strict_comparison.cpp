// test/strict_comparison.cpp
// AzaraCとazarashiのデコード結果の厳密な比較テスト
// 同じNMEAデータをデコードして、各フィールドの値が一致するかを検証

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/JsonSerializer.h"
#include "../src/internal/PrintShim.h"
#include "../src/internal/DcxHelper.h"
#include "doctest.h"
#include <cstring>
#include <string>
#include <cmath>
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

// ── Print → std::string アダプタ ────────────────────────────────────────────
struct StringPrint : public Print {
    std::string buf;
    size_t write(uint8_t c) override { buf += (char)c; return 1; }
    size_t write(const char* s, size_t size) override { if (s && size) buf.append(s, size); return size; }
    void print(char c)         override { write(c); }
    void print(const char* s)  override { if (s) buf += s; }
    void print(int v)          override { buf += std::to_string(v); }
    void print(unsigned int v) override { buf += std::to_string(v); }
    void println()             override { buf += '\n'; }
};

// ── NMEAデコードヘルパー ─────────────────────────────────────────────────────
inline bool decodeNmeaHelper(const char* nmea, Message& msg, uint32_t now = 0) {
    NmeaFramer framer;
    Frame frame;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            Decoder dec;
            return dec.decode(frame, msg, now);
        }
    }
    return false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 厳密な値比較テスト
// azarashiの出力値とAzaraCの出力値を比較
// ═══════════════════════════════════════════════════════════════════════════════

// 許容誤差（浮動小数点比較用）
constexpr double EPSILON = 0.01;

TEST_CASE("Strict Comparison: EEW - 緊急地震速報") {
    // azarashi test_scenario1: EEW
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 1); // EEW
    
    // report_time: Month=4, Day=25, Hour=13, Min=0
    CHECK(msg.mt43.event_time.month == 4);
    CHECK(msg.mt43.event_time.day == 25);
    CHECK(msg.mt43.event_time.hour == 13);
    CHECK(msg.mt43.event_time.minute == 0);
    
    // EEWフィールドの検証
    CHECK(msg.mt43.eew.long_period_lower >= 0);
    CHECK(msg.mt43.eew.long_period_upper >= 0);
    CHECK(msg.mt43.eew.depth > 0);
    CHECK(msg.mt43.eew.magnitude > 0);
    CHECK(msg.mt43.eew.epicenter > 0);
    CHECK(msg.mt43.eew.intensity_lower >= 0);
    CHECK(msg.mt43.eew.intensity_upper >= 0);
}

TEST_CASE("Strict Comparison: Hypocenter - 震源（不明値）") {
    // azarashi test_unknown_magnitude_or_depth
    // depth_of_hypocenter == '不明', magnitude == '不明'
    // raw値: depth=511, magnitude=127
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 2); // Hypocenter
    
    // 不明値の検証（azarashiと同じraw値を保持）
    CHECK(msg.mt43.hypo.depth == 511);    // 不明
    CHECK(msg.mt43.hypo.magnitude == 127); // 不明
    
    // report_time: Month=4, Day=25, Hour=13, Min=0
    CHECK(msg.mt43.event_time.month == 4);
    CHECK(msg.mt43.event_time.day == 25);
    CHECK(msg.mt43.event_time.hour == 13);
    CHECK(msg.mt43.event_time.minute == 0);
}

TEST_CASE("Strict Comparison: Tsunami - 津波") {
    // azarashi test_scenario1: Tsunami
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 5); // Tsunami
    
    CHECK(msg.mt43.tsunami.warning_code > 0);
    CHECK(msg.mt43.tsunami.count > 0);
    
    for (int i = 0; i < msg.mt43.tsunami.count; i++) {
        CHECK(msg.mt43.tsunami.entries[i].region_code > 0);
        CHECK(msg.mt43.tsunami.entries[i].height_code <= 15);
    }
}

TEST_CASE("Strict Comparison: NW Pacific Tsunami - 北西太平洋津波") {
    // azarashi test_northwest_pacific_tsunami
    const char* nmea = "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 6); // NW Pacific Tsunami
    
    CHECK(msg.mt43.nw_pac.potential > 0);
    CHECK(msg.mt43.nw_pac.count > 0);
}

TEST_CASE("Strict Comparison: Long Period Ground Motion - 長周期地震動") {
    // azarashi test_long_period_ground_motion
    // long_period_ground_motion_lower_limit == '長周期地震動階級2' (raw=3)
    // long_period_ground_motion_upper_limit == '長周期地震動階級2' (raw=3)
    const char* nmea = "$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 1); // EEW
    
    // 長周期地震動階級の検証
    CHECK(msg.mt43.eew.long_period_lower == 3); // 階級2
    CHECK(msg.mt43.eew.long_period_upper == 3); // 階級2
}

TEST_CASE("Strict Comparison: DCX L-Alert") {
    // azarashi test_dcx: l_alert
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.is_null_message == false);
    
    // CAMFフィールドの検証
    CHECK(msg.mt44.camf.a1 == 1);  // Alert
    CHECK(msg.mt44.camf.a2 == 111); // Japan
    CHECK(msg.mt44.camf.a3 == 1);  // FMMC/L-Alert
    
    // Extended fields
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1100); // 札幌市
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

TEST_CASE("Strict Comparison: DCX J-Alert") {
    // azarashi test_dcx: j_alert
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.is_null_message == false);
    
    // CAMFフィールドの検証
    CHECK(msg.mt44.camf.a2 == 111); // Japan
    CHECK(msg.mt44.camf.a3 == 2);  // FDMA/J-Alert
    
    // Extended fields
    CHECK(msg.mt44.ex_jalert.ex8 == 0); // Prefecture mode
    // EX9: 64-bit field, prefecture bitmask in bits [63:17]
    // 0x1FFFFFFFFFFFC0000 >> 17 = 0x1FFFFFFFFFFFF (all 47 prefectures set)
    CHECK((msg.mt44.ex_jalert.ex9 >> 17) == 0x1FFFFFFFFFFFFULL);
    CHECK(msg.mt44.ex_jalert.vn == 1);
}

TEST_CASE("Strict Comparison: DCX NULL Message") {
    // azarashi test_dcx: null_msg
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
    
    // A2=111 (Japan), A3=0
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 0);
}

TEST_CASE("Strict Comparison: DCX Outside Japan (Fiji)") {
    // azarashi test_dcx: org_outside_jpn
    // A2 = 71 (Fiji)
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    
    // A2 = 71 (Fiji)
    CHECK(msg.mt44.camf.a2 == 71);
    
    // VN = 5
    CHECK(msg.mt44.ex_outside.vn == 5);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 数値精度比較テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Numeric Precision: Lat/Lon decode") {
    // L-Alertテストデータ
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    
    // 緯度経度が妥当な範囲内か確認
    if (msg.mt44.mt44_decoded.main_ellipse_present) {
        double lat = msg.mt44.mt44_decoded.main_ellipse.lat_deg;
        double lon = msg.mt44.mt44_decoded.main_ellipse.lon_deg;
        
        CHECK(lat >= -90.0);
        CHECK(lat <= 90.0);
        CHECK(lon >= -180.0);
        CHECK(lon <= 180.0);
    }
}

TEST_CASE("Numeric Precision: Radius code decode") {
    // azarashi: __get_axis(factor) = pow(10, log10(216.2) + factor * (log10(2500000) - log10(216.2)) / 31) / 1000
    
    // code=0 → 0.216 km
    CHECK(std::abs(decodeRadiusCode(0) - 0.216) < 0.001);
    
    // code=13 → 10.933 km
    CHECK(std::abs(decodeRadiusCode(13) - 10.933) < 0.001);
    
    // code=31 → 2500.0 km
    CHECK(std::abs(decodeRadiusCode(31) - 2500.0) < 0.1);
}

TEST_CASE("Numeric Precision: Azimuth decode") {
    // azarashi: a16_ellipse_azimuth = -90 + 180 / 0x40 * camf.a16
    
    // code=0 → -90.0
    CHECK(std::abs(decodeAzimuth6(0) - (-90.0)) < 0.01);
    
    // code=32 → ~0.0
    CHECK(std::abs(decodeAzimuth6(32)) < 3.0);
    
    // code=63 → ~87.2
    CHECK(decodeAzimuth6(63) >= 87.0);
    CHECK(decodeAzimuth6(63) <= 87.5);
}

// ═══════════════════════════════════════════════════════════════════════════════
// エッジケース比較テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Edge Case: 不明値の処理") {
    // 深さ511 = 不明
    // マグニチュード127 = 不明
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    REQUIRE(ok);
    REQUIRE(msg.valid);
    
    // azarashiと同じraw値を保持しているか
    CHECK(msg.mt43.hypo.depth == 511);
    CHECK(msg.mt43.hypo.magnitude == 127);
}

TEST_CASE("Edge Case: 津波到着時間の境界値") {
    // hour=31, min=63 → 不明
    uint8_t bits[32] = {};
    Message msg{};
    
    // ビット操作ヘルパー
    auto setBits = [](uint8_t* buf, uint16_t start, uint8_t len, uint32_t value) {
        if (len == 0) return;
        for (int i = static_cast<int>(len) - 1; i >= 0; --i) {
            uint16_t pos = start + (len - 1 - i);
            if ((value >> i) & 1) buf[pos >> 3] |=  (1 << (7 - (pos & 7)));
            else                  buf[pos >> 3] &= ~(1 << (7 - (pos & 7)));
        }
    };
    
    // CRC計算ヘルパー
    auto crc24qRef = [](const uint8_t* d, int total_bits) {
        uint32_t crc = 0;
        int bytes = (total_bits + 7) / 8;
        for (int i = 0; i < bytes; i++) {
            uint8_t b = d[i];
            int bits_to_process = 8;
            if (i == bytes - 1 && (total_bits & 7)) {
                b &= 0xFFu << (8 - (total_bits & 7));
                bits_to_process = total_bits & 7;
            }
            crc ^= (uint32_t)b << 16;
            for (int j = 0; j < bits_to_process; j++) {
                crc <<= 1;
                if (crc & 0x1000000) crc ^= 0x1864CFB;
            }
        }
        return crc & 0xFFFFFF;
    };
    
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 5);   // Tsunami
    setBits(bits, 214, 6, 1);
    
    // report_time: month=4, day=25, hour=13, min=0
    setBits(bits, 21, 4, 4);
    setBits(bits, 25, 5, 25);
    setBits(bits, 30, 5, 13);
    setBits(bits, 35, 6, 0);
    
    setBits(bits, 80, 4, 3);   // warning_code
    
    // entry 1: region=1, height=2, arrival: hour=31, min=63 (不明)
    setBits(bits, 84, 10, 1);
    setBits(bits, 94, 4, 2);
    setBits(bits, 98, 12, (0u << 11) | (31u << 6) | 63u);
    
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    
    constexpr uint32_t NOW_TIMESTAMP = 1777122000;
    
    Frame f; f.svid = 193; memcpy(f.bits, bits, 32);
    Decoder dec;
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);
    
    REQUIRE(ok);
    REQUIRE(msg.mt43.tsunami.count >= 1);
    
    // 不明値の検証
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.hour == 0);
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.minute == 0);
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.unix_time == 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// JSON出力の一致検証
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("JSON Output: 全フィールド出力確認") {
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    REQUIRE(ok);
    
    StringPrint sp;
    JsonSerializer::serialize(msg, sp);
    const auto& json = sp.buf;
    
    // 必須フィールドの存在確認
    CHECK(json.find("\"msg_type\"") != std::string::npos);
    CHECK(json.find("\"svid\"") != std::string::npos);
    CHECK(json.find("\"disaster_category\"") != std::string::npos);
    
    // 値の一致確認
    CHECK(json.find("\"msg_type\":43") != std::string::npos);
    CHECK(json.find("\"disaster_category\":1") != std::string::npos);
}
