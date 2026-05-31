// test/test_json.cpp — JsonSerializer smoke tests
// JSONシリアライズ出力の検証

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

// ═══════════════════════════════════════════════════════════════════════════════
// MT=44 DCX JSON 出力テスト
// ═══════════════════════════════════════════════════════════════════════════════

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
    CHECK(has(s, "\"dcx_type\":1"));
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
    m.mt44.ex_jalert.ex8 = 0;
    m.mt44.ex_jalert.ex9 = 7;
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
    CHECK(has(s, "\"dcx_type\":2"));
    CHECK(has(s, "\"dcx_type_label\":\"J_ALERT\""));
    CHECK(has(s, "\"a2_country\":111"));
    CHECK(has(s, "\"a3_provider\":2"));
    CHECK(has(s, "\"ex8_area_type\":0"));
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
    m.mt44.ex_lalert_local.ex3 = 91522;
    m.mt44.ex_lalert_local.ex4 = 68950;
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
    CHECK(has(s, "\"dcx_type\":3"));
    CHECK(has(s, "\"dcx_type_label\":\"LOCAL_GOV\""));
    CHECK(has(s, "\"a3_provider\":4"));
    CHECK(has(s, "\"ex1_target_area\":1100"));
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
    CHECK(has(s, "\"dcx_type\":4"));
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
    CHECK(has(s, "\"dcx_type\":0"));
    CHECK(has(s, "\"dcx_type_label\":\"NULL\""));
}

TEST_CASE("JSON Serialization: MT=44 DCX Unknown") {
    Message m{};
    m.msg_type = 44; m.svid = 193; m.crc24 = 0xABCDEF;
    m.payload_type = MsgPayloadType::Mt44;
    m.mt44.service_kind = Mt44ServiceKind::Unknown;
    m.mt44.is_null_message = false;
    m.mt44.ex_kind = ExtendedKind::None;
    m.mt44.camf.a2 = 111; m.mt44.camf.a3 = 5;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"msg_type\":44"));
    CHECK(has(s, "\"dcx_type\":5"));
    CHECK(has(s, "\"dcx_type_label\":\"UNKNOWN\""));
}

TEST_CASE("JSON Serialization: MT=44 DCX main ellipse") {
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
    CHECK(has(s,"\"main_ellipse\":{"));
    CHECK(has(s,"\"lat_deg\":35.600"));
    CHECK(has(s,"\"lon_deg\":139.600"));
}

// ═══════════════════════════════════════════════════════════════════════════════
// MT=43 DCR JSON 出力テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("JSON Serialization: MT=43 EEW") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 1;
    m.mt43.eew.depth = 60; m.mt43.eew.magnitude = 65; m.mt43.eew.epicenter = 42;
    m.mt43.eew.intensity_lower = 5; m.mt43.eew.intensity_upper = 6;
    m.mt43.eew.region_count = 2;
    m.mt43.eew.regions[0] = 1; m.mt43.eew.regions[1] = 12;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"disaster_category\":1"));
    CHECK(has(s,"\"detail\":{"));
    CHECK(has(s,"\"depth\":60"));
    CHECK(has(s,"\"magnitude\":65"));
    CHECK(has(s,"\"regions\":["));
}

TEST_CASE("JSON Serialization: MT=43 Seismic Intensity") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 3;
    m.mt43.seis.count = 2;
    m.mt43.seis.entries[0] = {4, 13};
    m.mt43.seis.entries[1] = {5, 14};

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"disaster_category\":3"));
    CHECK(has(s,"\"entries\":["));
    CHECK(has(s,"\"intensity\":4"));
    CHECK(has(s,"\"prefecture\":13"));
}

TEST_CASE("JSON Serialization: MT=43 Hypocenter") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 2;
    m.mt43.hypo.depth = 40;
    m.mt43.hypo.magnitude = 64;
    m.mt43.hypo.epicenter = 791;
    m.mt43.hypo.notification_count = 1;
    m.mt43.hypo.notification[0] = 201;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":2"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"depth\":40"));
    CHECK(has(s, "\"magnitude\":64"));
    CHECK(has(s, "\"epicenter\":791"));
    CHECK(has(s, "\"notifications\":["));
}

TEST_CASE("JSON Serialization: MT=43 Tsunami") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 5;
    m.mt43.tsunami.warning_code = 3;
    m.mt43.tsunami.count = 2;
    m.mt43.tsunami.entries[0].region_code = 65;
    m.mt43.tsunami.entries[0].height_code = 4;
    m.mt43.tsunami.entries[1].region_code = 66;
    m.mt43.tsunami.entries[1].height_code = 2;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":5"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"warning_code\":3"));
    CHECK(has(s, "\"entries\":["));
    CHECK(has(s, "\"region\":65"));
    CHECK(has(s, "\"height\":4"));
}

TEST_CASE("JSON Serialization: MT=43 Nankai Trough") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 4;
    m.mt43.nankai.info_code = 1;
    m.mt43.nankai.page = 2;
    m.mt43.nankai.total_page = 3;
    m.mt43.nankai.text[0] = 'T';
    m.mt43.nankai.text[1] = 'e';
    m.mt43.nankai.text[2] = 's';
    m.mt43.nankai.text[3] = 't';

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":4"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"info_code\":1"));
    CHECK(has(s, "\"page\":2"));
    CHECK(has(s, "\"total_page\":3"));
}

TEST_CASE("JSON Serialization: MT=43 NW Pacific Tsunami") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 6;
    m.mt43.nw_pac.potential = 2;
    m.mt43.nw_pac.count = 1;
    m.mt43.nw_pac.entries[0].region_code = 1;
    m.mt43.nw_pac.entries[0].height_code = 3;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":6"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"potential\":2"));
    CHECK(has(s, "\"entries\":["));
}

TEST_CASE("JSON Serialization: MT=43 Volcano") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 8;
    m.mt43.vol.warning_code = 52;
    m.mt43.vol.volcano_name = 503;
    m.mt43.vol.ambiguity = 0;
    m.mt43.vol.lg_count = 1;
    m.mt43.vol.local_govs[0] = 4600000;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":8"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"warning_code\":52"));
    CHECK(has(s, "\"volcano_name\":503"));
    CHECK(has(s, "\"local_govs\":["));
}

TEST_CASE("JSON Serialization: MT=43 Ash Fall") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 9;
    m.mt43.ash.warning_type = 1;
    m.mt43.ash.volcano_name = 503;
    m.mt43.ash.count = 2;
    m.mt43.ash.entries_time[0] = 3;
    m.mt43.ash.entries_code[0] = 2;
    m.mt43.ash.entries_lg[0] = 1100000;
    m.mt43.ash.entries_time[1] = 6;
    m.mt43.ash.entries_code[1] = 5;
    m.mt43.ash.entries_lg[1] = 1200000;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":9"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"warning_type\":1"));
    CHECK(has(s, "\"volcano_name\":503"));
    CHECK(has(s, "\"entries\":["));
}

TEST_CASE("JSON Serialization: MT=43 Weather") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 10;
    m.mt43.wx.warning_state = 1;
    m.mt43.wx.count = 3;
    m.mt43.wx.entries[0].sub_category = 2;
    m.mt43.wx.entries[0].region_code = 11000;
    m.mt43.wx.entries[1].sub_category = 3;
    m.mt43.wx.entries[1].region_code = 12000;
    m.mt43.wx.entries[2].sub_category = 7;
    m.mt43.wx.entries[2].region_code = 13000;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":10"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"warning_state\":1"));
    CHECK(has(s, "\"entries\":["));
    CHECK(has(s, "\"sub_category\":2"));
    CHECK(has(s, "\"region\":11000"));
}

TEST_CASE("JSON Serialization: MT=43 Flood") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 11;
    m.mt43.flood.count = 2;
    m.mt43.flood.entries[0].warning_level = 3;
    m.mt43.flood.entries[0].region_code = 1234567ULL;
    m.mt43.flood.entries[1].warning_level = 4;
    m.mt43.flood.entries[1].region_code = 890ULL;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":11"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"entries\":["));
    CHECK(has(s, "\"warning_level\":3"));
}

TEST_CASE("JSON Serialization: MT=43 Typhoon") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 12;
    m.mt43.typh.number = 21;
    m.mt43.typh.scale = 3;
    m.mt43.typh.intensity = 2;
    m.mt43.typh.pressure = 980;
    m.mt43.typh.max_wind = 35;
    m.mt43.typh.max_gust = 50;
    m.mt43.typh.coords.lat_ns = 0;
    m.mt43.typh.coords.lat_deg = 25;
    m.mt43.typh.coords.lon_ew = 0;
    m.mt43.typh.coords.lon_deg = 130;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":12"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"number\":21"));
    CHECK(has(s, "\"scale\":3"));
    CHECK(has(s, "\"intensity\":2"));
    CHECK(has(s, "\"pressure\":980"));
    CHECK(has(s, "\"max_wind\":35"));
    CHECK(has(s, "\"max_gust\":50"));
}

TEST_CASE("JSON Serialization: MT=43 Marine") {
    Message m{};
    m.msg_type = 43;
    m.payload_type = MsgPayloadType::Mt43;
    m.mt43.disaster_category = 14;
    m.mt43.marine.count = 2;
    m.mt43.marine.entries[0].warning_code = 19;
    m.mt43.marine.entries[0].region_code = 100;
    m.mt43.marine.entries[1].warning_code = 20;
    m.mt43.marine.entries[1].region_code = 200;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s, "\"disaster_category\":14"));
    CHECK(has(s, "\"detail\":{"));
    CHECK(has(s, "\"entries\":["));
    CHECK(has(s, "\"warning_code\":19"));
    CHECK(has(s, "\"region\":100"));
}

// ═══════════════════════════════════════════════════════════════════════════════
// JSON 構造検証
// ═══════════════════════════════════════════════════════════════════════════════

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
