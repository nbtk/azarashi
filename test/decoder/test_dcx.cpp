// test/decoder/test_dcx.cpp — MT=44 (DCX) デコーダテスト
// DcxHelper のデコード関数テストを統合

#include "../test_helpers.h"
#include "../src/internal/DcxHelper.h"
#include "doctest.h"
#include <cmath>

using namespace azaraC;

// ── decodeLatitude16 ────────────────────────────────────────────────────────

TEST_CASE("decodeLatitude16: code=0 → -90.0") {
    CHECK(std::abs(decodeLatitude16(0) - (-90.0)) < 0.001);
}

TEST_CASE("decodeLatitude16: code=65535 → +90.0") {
    CHECK(std::abs(decodeLatitude16(65535) - 90.0) < 0.001);
}

TEST_CASE("decodeLatitude16: code=32768 → ~0.0") {
    double lat = decodeLatitude16(32768);
    CHECK(std::abs(lat) < 0.01);
}

TEST_CASE("decodeLatitude16: Tokyo area (~35.688°N)") {
    double lat = decodeLatitude16(45761);
    CHECK(lat >= 35.6);
    CHECK(lat <= 35.8);
}

// ── decodeLongitude17 ───────────────────────────────────────────────────────

TEST_CASE("decodeLongitude17: code=0 → -180.0") {
    CHECK(std::abs(decodeLongitude17(0) - (-180.0)) < 0.001);
}

TEST_CASE("decodeLongitude17: code=131071 → +180.0") {
    CHECK(std::abs(decodeLongitude17(131071) - 180.0) < 0.001);
}

TEST_CASE("decodeLongitude17: code=65536 → ~0.0") {
    double lon = decodeLongitude17(65536);
    CHECK(std::abs(lon) < 0.01);
}

TEST_CASE("decodeLongitude17: Tokyo area (~139.691°E)") {
    double lon = decodeLongitude17(116395);
    CHECK(lon >= 139.6);
    CHECK(lon <= 139.8);
}

// ── decodeLatitude17 ────────────────────────────────────────────────────────

TEST_CASE("decodeLatitude17: code=0 → -90.0") {
    CHECK(std::abs(decodeLatitude17(0) - (-90.0)) < 0.001);
}

TEST_CASE("decodeLatitude17: code=131071 → +90.0") {
    CHECK(std::abs(decodeLatitude17(131071) - 90.0) < 0.001);
}

TEST_CASE("decodeLatitude17: code=65536 → ~0.0") {
    double lat = decodeLatitude17(65536);
    CHECK(std::abs(lat) < 0.01);
}

// ── decodeLongitude17_45_225 ────────────────────────────────────────────────

TEST_CASE("decodeLongitude17_45_225: code=0 → 45.0") {
    CHECK(std::abs(decodeLongitude17_45_225(0) - 45.0) < 0.001);
}

TEST_CASE("decodeLongitude17_45_225: code=131071 → 225.0") {
    CHECK(std::abs(decodeLongitude17_45_225(131071) - 225.0) < 0.001);
}

TEST_CASE("decodeLongitude17_45_225: Tokyo area (~139.689°E)") {
    double lon = decodeLongitude17_45_225(68950);
    CHECK(lon >= 139.6);
    CHECK(lon <= 139.8);
}

// ── decodeRadiusCode ────────────────────────────────────────────────────────

TEST_CASE("decodeRadiusCode: code=0 → 0.216 km") {
    CHECK(std::abs(decodeRadiusCode(0) - 0.216) < 0.001);
}

TEST_CASE("decodeRadiusCode: code=13 → 10.933 km") {
    CHECK(std::abs(decodeRadiusCode(13) - 10.933) < 0.001);
}

TEST_CASE("decodeRadiusCode: code=31 → 2500.0 km") {
    CHECK(std::abs(decodeRadiusCode(31) - 2500.0) < 0.001);
}

TEST_CASE("decodeRadiusCode: code=32 (invalid) → 0.0") {
    CHECK(decodeRadiusCode(32) == 0.0);
}

TEST_CASE("decodeRadiusCode: code=255 (invalid) → 0.0") {
    CHECK(decodeRadiusCode(255) == 0.0);
}

// ── decodeAzimuth6 ──────────────────────────────────────────────────────────

TEST_CASE("decodeAzimuth6: code=0 → -90.0") {
    CHECK(std::abs(decodeAzimuth6(0) - (-90.0)) < 0.001);
}

TEST_CASE("decodeAzimuth6: code=63 → ~87.2") {
    double az = decodeAzimuth6(63);
    CHECK(az >= 87.0);
    CHECK(az <= 87.5);
}

TEST_CASE("decodeAzimuth6: code=32 → ~0.0") {
    double az = decodeAzimuth6(32);
    CHECK(std::abs(az) < 3.0);
}

// ── decodeAzimuth7 ──────────────────────────────────────────────────────────

TEST_CASE("decodeAzimuth7: code=0 → -90.0") {
    CHECK(std::abs(decodeAzimuth7(0) - (-90.0)) < 0.001);
}

TEST_CASE("decodeAzimuth7: code=127 → ~88.6") {
    double az = decodeAzimuth7(127);
    CHECK(az >= 88.0);
    CHECK(az <= 89.0);
}

TEST_CASE("decodeAzimuth7: code=64 → ~0.0") {
    double az = decodeAzimuth7(64);
    CHECK(std::abs(az) < 2.0);
}

// ── decodeCityCodeList ──────────────────────────────────────────────────────

TEST_CASE("decodeCityCodeList: 1コード") {
    uint64_t ex9 = (uint64_t)1100;
    uint16_t codes[4] = {};
    uint8_t count = decodeCityCodeList(ex9, codes);
    CHECK(count == 1);
    CHECK(codes[0] == 1100);
}

TEST_CASE("decodeCityCodeList: 4コード") {
    uint64_t ex9 = (uint64_t)1100 | ((uint64_t)2200 << 16) | ((uint64_t)3300 << 32) | ((uint64_t)4400 << 48);
    uint16_t codes[4] = {};
    uint8_t count = decodeCityCodeList(ex9, codes);
    CHECK(count == 4);
    CHECK(codes[0] == 1100);
    CHECK(codes[1] == 2200);
    CHECK(codes[2] == 3300);
    CHECK(codes[3] == 4400);
}

TEST_CASE("decodeCityCodeList: 空（ゼロ）") {
    uint64_t ex9 = 0;
    uint16_t codes[4] = {};
    uint8_t count = decodeCityCodeList(ex9, codes);
    CHECK(count == 0);
}

// ── B1 Refinement Tests ───────────────────────────────────────────────────

TEST_CASE("B1: all zeros") {
    B1Refinement b1 = decodeB1Refinement(0x0000);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C1=7") {
    B1Refinement b1 = decodeB1Refinement(0x7000);
    CHECK(b1.c1 == 7);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C2=7") {
    B1Refinement b1 = decodeB1Refinement(0x0E00);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 7);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C3=7") {
    B1Refinement b1 = decodeB1Refinement(0x01C0);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 7);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C4=7") {
    B1Refinement b1 = decodeB1Refinement(0x0038);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 7);
}

TEST_CASE("B1: b1RefinedLatitudeOffset: C1=0 → 0.0") {
    CHECK(std::abs(b1RefinedLatitudeOffset(0) - 0.0) < 0.0001);
}

TEST_CASE("B1: b1RefinedLatitudeOffset: C1=7 → ~0.0024°") {
    double offset = b1RefinedLatitudeOffset(7);
    CHECK(offset > 0.002);
    CHECK(offset < 0.003);
}

TEST_CASE("B1: b1InterpolationFactor: C3=0 → 0.0") {
    CHECK(std::abs(b1InterpolationFactor(0) - 0.0) < 0.001);
}

TEST_CASE("B1: b1InterpolationFactor: C3=7 → 0.875") {
    CHECK(std::abs(b1InterpolationFactor(7) - 0.875) < 0.001);
}

// ── B2 Hazard Center Tests ────────────────────────────────────────────────

TEST_CASE("B2: C5=0, C6=0 → delta=-10.0") {
    B2HazardCenter b2 = decodeB2HazardCenter(0, 0);
    CHECK(std::abs(b2.delta_lat_deg - (-10.0)) < 0.001);
    CHECK(std::abs(b2.delta_lon_deg - (-10.0)) < 0.001);
}

TEST_CASE("B2: C5=127, C6=127 → delta=+10.0") {
    B2HazardCenter b2 = decodeB2HazardCenter(127, 127);
    CHECK(std::abs(b2.delta_lat_deg - 10.0) < 0.001);
    CHECK(std::abs(b2.delta_lon_deg - 10.0) < 0.001);
}

// ── B3 Secondary Ellipse Tests ─────────────────────────────────────────────

TEST_CASE("B3: C7=0 → shift=0.0") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(0, 0, 0, 0, 100.0);
    CHECK(std::abs(b3.shift_km - 0.0) < 0.001);
}

TEST_CASE("B3: C7=3 → shift=300.0 km") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(3, 0, 0, 0, 100.0);
    CHECK(std::abs(b3.shift_km - 300.0) < 0.001);
}

TEST_CASE("B3: C8=0 → factor=0.25") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(0, 0, 0, 0, 100.0);
    CHECK(std::abs(b3.homothetic_factor - 0.25) < 0.001);
}

TEST_CASE("B3: C8=7 → factor=2.0") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(0, 7, 0, 0, 100.0);
    CHECK(std::abs(b3.homothetic_factor - 2.0) < 0.001);
}

TEST_CASE("B3: C9=0 → bearing=0.0") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(0, 0, 0, 0, 100.0);
    CHECK(std::abs(b3.bearing_deg - 0.0) < 0.001);
}

TEST_CASE("B3: C9=31 → bearing=348.75") {
    B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(0, 0, 31, 0, 100.0);
    CHECK(std::abs(b3.bearing_deg - 348.75) < 0.001);
}

// ── B4 Detailed Info Tests ────────────────────────────────────────────────

TEST_CASE("B4: Earthquake (A4=36): D1-D4 all 1s") {
    B4DetailedInfo b4 = decodeB4DetailedInfo(0xFFFF, 36);
    CHECK(b4.d1 == 15);
    CHECK(b4.d2 == 7);
    CHECK(b4.d3 == 15);
    CHECK(b4.d4 == 15);
}

TEST_CASE("B4: Tsunami (A4=43): D5=7") {
    B4DetailedInfo b4 = decodeB4DetailedInfo(0x7000, 43);
    CHECK(b4.d5 == 7);
}

TEST_CASE("B4: Hurricane (A4=80): D7=7, D8=15, D9=7") {
    B4DetailedInfo b4 = decodeB4DetailedInfo(0x7FE0, 80);
    CHECK(b4.d7 == 7);
    CHECK(b4.d8 == 15);
    CHECK(b4.d9 == 7);
}

TEST_CASE("B4: Typhoon (A4=82): D36=7, D8=15, D9=7") {
    B4DetailedInfo b4 = decodeB4DetailedInfo(0x7FE0, 82);
    CHECK(b4.d36 == 7);
    CHECK(b4.d8 == 15);
    CHECK(b4.d9 == 7);
}

// ── MT=44 統合テスト ───────────────────────────────────────────────────────

TEST_CASE("MT=44 field extraction on synthetic frame") {
    uint8_t buf[32] = {};

    setBits(buf, 0,  8, 0x53);  // preamble
    setBits(buf, 8,  6, 44);    // msg_type
    setBits(buf, 24, 2, 1);     // CAMF.A1 = 1 (Alert)
    setBits(buf, 26, 9, 111);   // CAMF.A2 = 111 (Japan)
    setBits(buf, 35, 5, 2);     // CAMF.A3 = 2 (FDMA → J-Alert)

    uint32_t crc = crc24qRef(buf, 226);
    setBits(buf, 226, 24, crc);

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg);
    REQUIRE(ok);
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.camf.a1 == 1);
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 2);
}
