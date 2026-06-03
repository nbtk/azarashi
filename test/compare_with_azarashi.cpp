// test/compare_with_azarashi.cpp
// azarashiのテストデータを使ってAzaraCの出力を検証する比較テスト
// azarashi v0.16.1 のテストデータと出力を比較

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/JsonSerializer.h"
#include "../src/internal/PrintShim.h"
#include "doctest.h"
#include <cstring>
#include <string>
#include <sstream>
#include <cmath>

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
// azarashi テストデータ比較テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Azarashi Comparison: EEW (緊急地震速報)") {
    // azarashi test_scenario1: EEW
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 1); // EEW
    
    // azarashi出力との比較ポイント
    // - disaster_category: 1 (EEW)
    // - 震度、震源、マグニチュードなどの値が一致するか
    CHECK(msg.mt43.eew.depth > 0);
    CHECK(msg.mt43.eew.magnitude > 0);
}

TEST_CASE("Azarashi Comparison: Seismic Intensity (震度)") {
    const char* nmea = "$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB8000000000000000011E027E5C*76";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 3); // Seismic Intensity
}

TEST_CASE("Azarashi Comparison: Hypocenter (震源)") {
    const char* nmea = "$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 2); // Hypocenter
    
    // azarashi: depth_of_hypocenter, magnitude が出力される
    CHECK(msg.mt43.hypo.depth > 0);
    CHECK(msg.mt43.hypo.magnitude > 0);
}

TEST_CASE("Azarashi Comparison: Tsunami (津波)") {
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 5); // Tsunami
    
    // azarashi: tsunami entries with region, height, arrival time
    CHECK(msg.mt43.tsunami.count > 0);
    CHECK(msg.mt43.tsunami.warning_code > 0);
}

TEST_CASE("Azarashi Comparison: Tsunami Update (津波更新)") {
    const char* nmea = "$QZQSM,58,9AAFA99C8C8001E8F67C31193960464E621193BBC464EF80000000109DB7028*09";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 5); // Tsunami
}

TEST_CASE("Azarashi Comparison: Nankai Trough (南海トラフ)") {
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 4); // Nankai Trough
}

TEST_CASE("Azarashi Comparison: Volcano (火山)") {
    const char* nmea = "$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 8); // Volcano
}

TEST_CASE("Azarashi Comparison: Ash Fall (降灰速報)") {
    const char* nmea = "$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 9); // Ash Fall
}

TEST_CASE("Azarashi Comparison: Weather (気象)") {
    const char* nmea = "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 10); // Weather
}

TEST_CASE("Azarashi Comparison: Flood (洪水)") {
    const char* nmea = "$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 11); // Flood
}

TEST_CASE("Azarashi Comparison: Northwest Pacific Tsunami (北西太平洋津波)") {
    const char* nmea = "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 6); // NW Pacific Tsunami
}

TEST_CASE("Azarashi Comparison: Unknown Magnitude/Depth (不明値)") {
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 2); // Hypocenter
    
    // azarashi: depth_of_hypocenter == '不明', magnitude == '不明'
    // raw値: depth=511, magnitude=127
    CHECK(msg.mt43.hypo.depth == 511);
    CHECK(msg.mt43.hypo.magnitude == 127);
}

TEST_CASE("Azarashi Comparison: Long Period Ground Motion (長周期地震動)") {
    const char* nmea = "$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
    CHECK(msg.mt43.disaster_category == 1); // EEW
    
    // azarashi: long_period_ground_motion_lower_limit == '長周期地震動階級2'
    // long_period_ground_motion_upper_limit == '長周期地震動階級2'
    CHECK(msg.mt43.eew.long_period_lower == 3);
    CHECK(msg.mt43.eew.long_period_upper == 3);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DCX (MT=44) 比較テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Azarashi Comparison: DCX NULL Message") {
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

TEST_CASE("Azarashi Comparison: DCX Outside Japan (Fiji)") {
    // azarashi test_dcx: org_outside_jpn
    // A2 = 71 (Fiji) - NOT 32 (Australia)
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 71); // Fiji (azarashi definition: 71u, "Fiji")
}

TEST_CASE("Azarashi Comparison: DCX L-Alert") {
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
}

TEST_CASE("Azarashi Comparison: DCX J-Alert") {
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
}

// ═══════════════════════════════════════════════════════════════════════════════
// カバー率測定テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Coverage: All MT=43 Disaster Categories") {
    // azarashiテストデータでカバーされる災害カテゴリ
    // 1: EEW, 2: Hypocenter, 3: Seismic Intensity, 4: Nankai Trough
    // 5: Tsunami, 6: NW Pacific Tsunami, 8: Volcano, 9: Ash Fall
    // 10: Weather, 11: Flood
    
    // 各カテゴリの代表NMEAデータ
    struct TestCase {
        const char* name;
        const char* nmea;
        uint8_t expected_dc;
    };
    
    TestCase cases[] = {
        {"EEW", "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F", 1},
        {"Hypocenter", "$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A", 2},
        {"Seismic", "$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB8000000000000000011E027E5C*76", 3},
        {"Nankai", "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02", 4},
        {"Tsunami", "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F", 5},
        {"NW Pac Tsunami", "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C", 6},
        {"Volcano", "$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70", 8},
        {"Ash Fall", "$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71", 9},
        {"Weather", "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73", 10},
        {"Flood", "$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E", 11},
    };
    
    int covered = 0;
    for (const auto& tc : cases) {
        Message msg{};
        bool ok = decodeNmeaHelper(tc.nmea, msg);
        if (ok && msg.valid && msg.mt43.disaster_category == tc.expected_dc) {
            covered++;
        }
    }
    
    // 10/10 カバーされていることを確認
    CHECK(covered == 10);
}

TEST_CASE("Coverage: All MT=44 Service Kinds") {
    // azarashiテストデータでカバーされるDCX種別
    // NULL, Outside Japan, L-Alert, J-Alert
    
    struct TestCase {
        const char* name;
        const char* nmea;
        Mt44ServiceKind expected_kind;
    };
    
    TestCase cases[] = {
        {"NULL", "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E", Mt44ServiceKind::NullMessage},
        {"Outside Japan", "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C", Mt44ServiceKind::OutsideJapan},
        {"L-Alert", "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04", Mt44ServiceKind::LAlert},
        {"J-Alert", "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00", Mt44ServiceKind::JAlert},
    };
    
    int covered = 0;
    for (const auto& tc : cases) {
        Message msg{};
        bool ok = decodeNmeaHelper(tc.nmea, msg);
        if (ok && msg.valid && msg.mt44.service_kind == tc.expected_kind) {
            covered++;
        }
    }
    
    // 4/4 カバーされていることを確認
    CHECK(covered == 4);
}

// ═══════════════════════════════════════════════════════════════════════════════
// JSON出力比較テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("JSON Output: EEW structure validation") {
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    REQUIRE(ok);
    
    StringPrint sp;
    JsonSerializer::serialize(msg, sp);
    const auto& json = sp.buf;
    
    // 必須フィールドの存在確認
    CHECK(json.find("\"msg_type\":43") != std::string::npos);
    CHECK(json.find("\"disaster_category\":1") != std::string::npos);
    CHECK(json.find("\"detail\"") != std::string::npos);
}

TEST_CASE("JSON Output: DCX L-Alert structure validation") {
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
    Message msg{};
    bool ok = decodeNmeaHelper(nmea, msg);
    REQUIRE(ok);
    
    StringPrint sp;
    JsonSerializer::serialize(msg, sp);
    const auto& json = sp.buf;
    
    // 必須フィールドの存在確認
    CHECK(json.find("\"msg_type\":44") != std::string::npos);
    CHECK(json.find("\"dcx_type\":1") != std::string::npos);
    CHECK(json.find("\"dcx_type_label\":\"L_ALERT\"") != std::string::npos);
}
