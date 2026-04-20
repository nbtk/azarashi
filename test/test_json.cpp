
// test/test_json.cpp — JsonSerializer smoke tests
// Build: make -C test run

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/PrintShim.h"
#include <cstdio>
#include <cstring>
#include <cassert>
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

static void pass(const char* name) { printf("  PASS  %s\n", name); }
static void fail(const char* name, const char* why) {
    printf("  FAIL  %s : %s\n", name, why);
    assert(false);
}
static bool has(const std::string& s, const char* sub) {
    return s.find(sub) != std::string::npos;
}

// ── MT=44 DCX ───────────────────────────────────────────────────────────────
static void test_json_dcx() {
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

    if (!has(s,"\"svid\":193"))       fail("dcx_svid",    s.c_str());
    if (!has(s,"\"msg_type\":44"))    fail("dcx_msg_type",s.c_str());
    if (!has(s,"\"dcx_type\":1"))     fail("dcx_type",    s.c_str());
    if (!has(s,"\"a2_country\":111")) fail("dcx_country", s.c_str());
    if (!has(s,"\"lat_e2\":356"))     fail("dcx_lat",     s.c_str());
    if (!has(s,"\"lon_e2\":1396"))    fail("dcx_lon",     s.c_str());
    pass("json_dcx_keys");
}

// ── MT=43 EEW ───────────────────────────────────────────────────────────────
static void test_json_eew() {
    Message m{};
    m.msg_type = 43; m.disaster_category = 1;
    m.eew_depth = 60; m.eew_magnitude = 65; m.eew_epicenter = 42;
    m.eew_intensity_lower = 5; m.eew_intensity_upper = 6;
    m.eew_region_count = 2;
    m.eew_regions[0] = 1; m.eew_regions[1] = 12;

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    if (!has(s,"\"disaster_category\":1")) fail("eew_cat",     s.c_str());
    if (!has(s,"\"detail\":{"))            fail("eew_detail",  s.c_str());
    if (!has(s,"\"depth\":60"))            fail("eew_depth",   s.c_str());
    if (!has(s,"\"magnitude\":65"))        fail("eew_mag",     s.c_str());
    if (!has(s,"\"regions\":["))           fail("eew_regions", s.c_str());
    pass("json_eew_keys");
}

// ── MT=43 Seismic Intensity ──────────────────────────────────────────────────
static void test_json_seismic() {
    Message m{};
    m.msg_type = 43; m.disaster_category = 5; // 5 is Seismic Intensity
    m.seis_count = 2;
    m.seis_entries[0] = {4, 13};
    m.seis_entries[1] = {5, 14};

    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;

    if (!has(s,"\"disaster_category\":5")) fail("seis_cat",     s.c_str());
    if (!has(s,"\"entries\":["))           fail("seis_entries", s.c_str());
    if (!has(s,"\"intensity\":4"))         fail("seis_int",     s.c_str());
    if (!has(s,"\"prefecture\":13"))       fail("seis_pref",    s.c_str());
    pass("json_seismic_keys");
}

// ── Balanced braces/brackets ─────────────────────────────────────────────────
static void test_balanced(const char* name, const Message& m) {
    StringPrint sp;
    internal::JsonSerializer::serialize(m, sp);
    const auto& s = sp.buf;
    int brace = 0, bracket = 0; bool in_str = false; char prev = 0;
    for (char c : s) {
        if (c == '"' && prev != '\\') in_str = !in_str;
        if (!in_str) {
            if (c=='{') brace++;  if (c=='}') brace--;
            if (c=='[') bracket++;if (c==']') bracket--;
        }
        prev = c;
    }
    if (brace != 0 || bracket != 0) {
        printf("    json=%s\n", s.c_str());
        fail(name, "unbalanced");
    }
    pass(name);
}

// ── main ─────────────────────────────────────────────────────────────────────
int main() {
    printf("=== azaraC JSON tests ===\n");
    test_json_dcx();
    test_json_eew();
    test_json_seismic();

    for (uint8_t dc : {1,2,3,4,5,6,7,8,9,10,11,12}) {
        char name[40]; snprintf(name,sizeof(name),"json_balanced_dc%d",dc);
        Message m{}; m.msg_type = 43; m.disaster_category = dc;
        test_balanced(name, m);
    }
    { Message m{}; m.msg_type = 44; test_balanced("json_balanced_mt44", m); }

    printf("=== all passed ===\n");
    return 0;
}
