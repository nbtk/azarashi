// test/test_json.cpp — JsonSerializer smoke tests
// Build: make -C test run

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/PrintShim.h"
#include "doctest.h"
#include <cstdio>
#include <cstring>
#include <string>

using namespace azaraC;

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

static bool has(const std::string& s, const char* sub) {
    return s.find(sub) != std::string::npos;
}

// ── MT=44 DCX ───────────────────────────────────────────────────────────────
TEST_CASE("JSON Serialization: MT=44 DCX") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::LAlert;
    m.mt44.camf.a1 = 1; m.mt44.camf.a2 = 111;
    m.mt44.camf.a3 = 1; m.mt44.camf.a4 = 1;
    m.mt44.camf.a5 = 3; m.mt44.camf.a8 = 4;
    m.mt44.mt44_decoded.main_ellipse_present = true;
    m.mt44.mt44_decoded.main_ellipse.lat_deg = 35.6;
    m.mt44.mt44_decoded.main_ellipse.lon_deg = 139.6;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"svid\":193"));
    CHECK(has(s,"\"msg_type\":44"));
    CHECK(has(s,"\"a2_country\":111"));
    // Check decoded main ellipse is present
    CHECK(has(s,"\"main_ellipse\":{"));
    CHECK(has(s,"\"lat_deg\":35.600"));
    CHECK(has(s,"\"lon_deg\":139.600"));
}

// ── MT=43 EEW ───────────────────────────────────────────────────────────────

TEST_CASE("JSON Serialization: MT=43 EEW") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 1;
    m.mt43.eew_depth = 60; m.mt43.eew_magnitude = 65; m.mt43.eew_epicenter = 42;
    m.mt43.eew_intensity_lower = 5; m.mt43.eew_intensity_upper = 6;
    m.mt43.eew_region_count = 2;
    m.mt43.eew_regions[0] = 1; m.mt43.eew_regions[1] = 12;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"disaster_category\":1"));
    CHECK(has(s,"\"detail\":{"));
    CHECK(has(s,"\"depth\":60"));
    CHECK(has(s,"\"magnitude\":65"));
    CHECK(has(s,"\"regions\":["));
}

// ── MT=43 Seismic Intensity ──────────────────────────────────────────────────
TEST_CASE("JSON Serialization: MT=43 Seismic Intensity") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 3; // 3 is Seismic Intensity
    m.mt43.seis_count = 2;
    m.mt43.seis_entries[0] = {4, 13};
    m.mt43.seis_entries[1] = {5, 14};

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"disaster_category\":3"));
    CHECK(has(s,"\"entries\":["));
    CHECK(has(s,"\"intensity\":4"));
    CHECK(has(s,"\"prefecture\":13"));
}

// ── MT=44 DCX JSON 出力テスト ───────────────────────────────────────────────

TEST_CASE("JSON Serialization: MT=44 DCX L-Alert") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::LAlert;
    m.mt44.is_null_message = false;
    m.mt44.ex_kind         = ExtendedKind::LAlertOrLocal;
    m.mt44.camf.a1 = 1; m.mt44.camf.a2 = 111; m.mt44.camf.a3 = 1;
    m.mt44.camf.a4 = 10; m.mt44.camf.a5 = 3; m.mt44.camf.a8 = 4;
    m.mt44.camf.a11 = 1;
    m.mt44.ex_lalert_local.ex1 = 1100;
    m.mt44.ex_lalert_local.vn = 1;
    m.mt44.sd.sdmt = 0; m.mt44.sd.sdm = 0x1FF;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":1"));           // LAlert = 1
    CHECK(has(s, "\"dcx_type_label\":\"L_ALERT\""));
    CHECK(has(s, "\"a2_country\":111"));
    CHECK(has(s, "\"a3_provider\":1"));
    CHECK(has(s, "\"ex1_target_area\":1100"));
    CHECK(has(s, "\"sd_sdmt\":0"));
    CHECK(has(s, "\"sd_sdm\":511"));
}

TEST_CASE("JSON Serialization: MT=44 DCX J-Alert") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::JAlert;
    m.mt44.is_null_message = false;
    m.mt44.ex_kind         = ExtendedKind::JAlert;
    m.mt44.camf.a1 = 1; m.mt44.camf.a2 = 111; m.mt44.camf.a3 = 2;
    m.mt44.camf.a4 = 5; m.mt44.camf.a5 = 3;
    m.mt44.ex_jalert.ex8 = 0;    // prefecture code
    m.mt44.ex_jalert.ex9 = 7;    // Hokkaido + Aomori + Iwate (bits 0,1,2 = positions 47,46,45)
    m.mt44.ex_jalert.vn = 1;
    m.mt44.mt44_decoded.jalert_prefecture_mode = true;
    m.mt44.mt44_decoded.prefecture_count = 3;
    m.mt44.mt44_decoded.prefecture_positions[0] = 47;
    m.mt44.mt44_decoded.prefecture_positions[1] = 46;
    m.mt44.mt44_decoded.prefecture_positions[2] = 45;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":2"));           // JAlert = 2
    CHECK(has(s, "\"dcx_type_label\":\"J_ALERT\""));
    CHECK(has(s, "\"a2_country\":111"));
    CHECK(has(s, "\"a3_provider\":2"));
    CHECK(has(s, "\"ex8_area_type\":0"));
    // Check decoded J-Alert target
    CHECK(has(s, "\"jalert_target\":{"));
    CHECK(has(s, "\"prefecture_mode\":1"));
    CHECK(has(s, "\"prefecture_positions\":[47,46,45]"));
}

TEST_CASE("JSON Serialization: MT=44 DCX Local Government") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::LocalGovernment;
    m.mt44.is_null_message = false;
    m.mt44.ex_kind         = ExtendedKind::LAlertOrLocal;
    m.mt44.camf.a1 = 1; m.mt44.camf.a2 = 111; m.mt44.camf.a3 = 4;
    m.mt44.camf.a4 = 10; m.mt44.camf.a5 = 3;
    m.mt44.ex_lalert_local.ex1 = 1100;
    m.mt44.ex_lalert_local.ex2 = 1;
    m.mt44.ex_lalert_local.ex3 = 91522;   // Additional ellipse latitude
    m.mt44.ex_lalert_local.ex4 = 68950;   // Additional ellipse longitude
    m.mt44.ex_lalert_local.ex5 = 10;
    m.mt44.ex_lalert_local.ex6 = 8;
    m.mt44.ex_lalert_local.ex7 = 96;
    m.mt44.ex_lalert_local.vn = 1;
    m.mt44.mt44_decoded.additional_area.present = true;
    m.mt44.mt44_decoded.additional_area.head_to_area = true;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":3"));           // LocalGovernment = 3
    CHECK(has(s, "\"dcx_type_label\":\"LOCAL_GOV\""));
    CHECK(has(s, "\"a3_provider\":4"));
    CHECK(has(s, "\"ex1_target_area\":1100"));
    // Check additional area
    CHECK(has(s, "\"additional_area\":{"));
    CHECK(has(s, "\"head_to_area\":1"));
}

TEST_CASE("JSON Serialization: MT=44 DCX Outside Japan") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::OutsideJapan;
    m.mt44.is_null_message = false;
    m.mt44.ex_kind         = ExtendedKind::OutsideJapan;
    m.mt44.camf.a1 = 1; m.mt44.camf.a2 = 32; m.mt44.camf.a3 = 1;
    m.mt44.ex_outside.vn = 5;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":4"));           // OutsideJapan = 4
    CHECK(has(s, "\"dcx_type_label\":\"OUTSIDE_JAPAN\""));
    CHECK(has(s, "\"a2_country\":32"));
}

TEST_CASE("JSON Serialization: MT=44 DCX Null Message") {
    Message m{};
    m.msg_type        = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type    = MsgPayloadType::Mt44;
    m.mt44.service_kind    = Mt44ServiceKind::NullMessage;
    m.mt44.is_null_message = true;
    m.mt44.ex_kind         = ExtendedKind::None;
    m.mt44.camf.a2 = 111; m.mt44.camf.a3 = 0;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":0"));           // NullMessage = 0
    CHECK(has(s, "\"dcx_type_label\":\"NULL\""));
}

// ── Balanced braces/brackets ─────────────────────────────────────────────────
TEST_CASE("JSON Serialization: Balanced braces/brackets") {
    auto test_balanced = [](const Message& m) {
        StringPrint sp;
        internal::JsonSerializer::serialize(m, sp);
        const auto& s = sp.buf;
        int brace = 0, bracket = 0; bool in_str = false; char prev = 0;
        for (char c : s) {
            if (c == '"' && prev != '\\') in_str = !in_str;
            if (!in_str) {
                if (c=='{') brace++;
                if (c=='}') brace--;
                if (c=='[') bracket++;
                if (c==']') bracket--;
            }
            prev = c;
        }
        CHECK_MESSAGE((brace == 0 && bracket == 0), "json=", s.c_str());
    };

    SUBCASE("Disaster Categories 1-14") {
        for (uint8_t dc : {1,2,3,4,5,6,7,8,9,10,11,12,14}) {
            Message m{}; m.msg_type = 43; m.payload_type = MsgPayloadType::Mt43; m.mt43.disaster_category = dc;
            test_balanced(m);
        }
    }
    SUBCASE("MT=44") {
        Message m{}; m.msg_type = 44; m.payload_type = MsgPayloadType::Mt44;
        test_balanced(m);
    }
}
