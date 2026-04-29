
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
    void print(char c)         override { buf += c; }
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
    m.dcx_type        = DcxType::L_ALERT;
    m.a1_message_type = 2; m.a2_country_code = 111;
    m.a3_provider = 2; m.a4_hazard = 1;
    m.a5_severity = 3; m.a8_duration = 4;
    m.a12_lat_e2 = 356; m.a13_lon_e2 = 1396;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"svid\":193"));
    CHECK(has(s,"\"msg_type\":44"));
    CHECK(has(s,"\"dcx_type\":1"));
    CHECK(has(s,"\"a2_country\":111"));
    CHECK(has(s,"\"lat_e2\":356"));
    CHECK(has(s,"\"lon_e2\":1396"));
}

// ── MT=43 EEW ───────────────────────────────────────────────────────────────
TEST_CASE("JSON Serialization: MT=43 EEW") {
    Message m{};
    m.msg_type = 43; m.disaster_category = 1;
    m.eew_depth = 60; m.eew_magnitude = 65; m.eew_epicenter = 42;
    m.eew_intensity_lower = 5; m.eew_intensity_upper = 6;
    m.eew_region_count = 2;
    m.eew_regions[0] = 1; m.eew_regions[1] = 12;

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
    m.msg_type = 43; m.disaster_category = 5; // 5 is Seismic Intensity
    m.seis_count = 2;
    m.seis_entries[0] = {4, 13};
    m.seis_entries[1] = {5, 14};

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    CHECK(has(s,"\"disaster_category\":5"));
    CHECK(has(s,"\"entries\":["));
    CHECK(has(s,"\"intensity\":4"));
    CHECK(has(s,"\"prefecture\":13"));
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
            Message m{}; m.msg_type = 43; m.disaster_category = dc;
            test_balanced(m);
        }
    }
    SUBCASE("MT=44") {
        Message m{}; m.msg_type = 44;
        test_balanced(m);
    }
}
