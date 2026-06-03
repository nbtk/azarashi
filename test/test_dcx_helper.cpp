// test/test_dcx_helper.cpp — DcxHelper decode function unit tests

#include "test_helpers.h"
#include "../src/internal/DcxHelper.h"
#include "doctest.h"
#include <cmath>

using namespace azaraC;
using namespace azaraC::internal;

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

TEST_CASE("decodeRadiusCode: code=10 → 4.421 km") {
    CHECK(std::abs(decodeRadiusCode(10) - 4.421) < 0.001);
}

TEST_CASE("decodeRadiusCode: code=20 → 90.407 km") {
    CHECK(std::abs(decodeRadiusCode(20) - 90.407) < 0.001);
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

TEST_CASE("decodeAzimuth6: code=48 → ~45.0") {
    double az = decodeAzimuth6(48);
    CHECK(az >= 43.0);
    CHECK(az <= 47.0);
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

TEST_CASE("decodeAzimuth7: code=96 → ~45.0") {
    double az = decodeAzimuth7(96);
    CHECK(az >= 44.0);
    CHECK(az <= 46.0);
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

TEST_CASE("decodeCityCodeList: スキップあり") {
    uint64_t ex9 = ((uint64_t)500 << 16) | ((uint64_t)600 << 48);
    uint16_t codes[4] = {};
    uint8_t count = decodeCityCodeList(ex9, codes);
    CHECK(count == 2);
    CHECK(codes[0] == 500);
    CHECK(codes[1] == 600);
}

// ── B1 Refinement Tests ───────────────────────────────────────────────────
// A18 bit layout: bit[14]=MSB (spec bit 131), bit[0]=LSB (spec bit 145)
// C1 = (a18 >> 12) & 0x07  → spec[131:133]
// C2 = (a18 >> 9)  & 0x07  → spec[134:136]
// C3 = (a18 >> 6)  & 0x07  → spec[137:139]
// C4 = (a18 >> 3)  & 0x07  → spec[140:142]

TEST_CASE("B1: all zeros") {
    B1Refinement b1 = decodeB1Refinement(0x0000);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C1=7") {
    // C1 = (a18 >> 12) & 0x07 = 7 → a18 bits 14:12 = 0b111
    // a18 = 0b0111_0000_0000_0000 = 0x7000
    B1Refinement b1 = decodeB1Refinement(0x7000);
    CHECK(b1.c1 == 7);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C2=7") {
    // C2 = (a18 >> 9) & 0x07 = 7 → a18 bits 11:9 = 0b111
    // a18 = 0b0000_1110_0000_0000 = 0x0E00
    B1Refinement b1 = decodeB1Refinement(0x0E00);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 7);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C3=7") {
    // C3 = (a18 >> 6) & 0x07 = 7 → a18 bits 8:6 = 0b111
    // a18 = 0b0000_0001_1100_0000 = 0x01C0
    B1Refinement b1 = decodeB1Refinement(0x01C0);
    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 7);
    CHECK(b1.c4 == 0);
}

TEST_CASE("B1: C4=7") {
    // C4 = (a18 >> 3) & 0x07 = 7 → a18 bits 5:3 = 0b111
    // a18 = 0b0000_0000_0011_1000 = 0x0038
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

TEST_CASE("B1: b1RefinedLongitudeOffset: C2=0 → 0.0") {
    CHECK(std::abs(b1RefinedLongitudeOffset(0) - 0.0) < 0.0001);
}

TEST_CASE("B1: b1RefinedLongitudeOffset: C2=7 → ~0.0024°") {
    double offset = b1RefinedLongitudeOffset(7);
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

TEST_CASE("B2: C5=32 → delta=-5.0") {
    // C5=32: -10 + (20/128) * 32 = -10 + 5 = -5
    B2HazardCenter b2 = decodeB2HazardCenter(32, 0);
    CHECK(std::abs(b2.delta_lat_deg - (-5.0)) < 0.001);
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
// A18 bit layout: bit[14]=MSB (spec bit 131), bit[0]=LSB (spec bit 145)
// D1[131:134] → shift=11, mask=0x0F
// D2[135:137] → shift=8,  mask=0x07
// D3[138:141] → shift=4,  mask=0x0F
// D4[142:145] → shift=0,  mask=0x0F

TEST_CASE("B4: Earthquake (A4=36): D1-D4 all 1s") {
    B4DetailedInfo b4 = decodeB4DetailedInfo(0xFFFF, 36);
    CHECK(b4.d1 == 15);
    CHECK(b4.d2 == 7);
    CHECK(b4.d3 == 15);
    CHECK(b4.d4 == 15);
}

TEST_CASE("B4: Tsunami (A4=43): D5=7") {
    // D5[131:133] → a18[14:12] = 0b111 → a18 = 0x7000
    B4DetailedInfo b4 = decodeB4DetailedInfo(0x7000, 43);
    CHECK(b4.d5 == 7);
}

TEST_CASE("B4: Hurricane (A4=80): D7=7, D8=15, D9=7") {
    // D7[131:133] → a18[14:12] = 0b111
    // D8[134:137] → a18[10:7]  = 0b1111
    // D9[138:140] → a18[7:5]   = 0b111
    // a18 = 0b0111_1111_1110_0000 = 0x7FE0
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