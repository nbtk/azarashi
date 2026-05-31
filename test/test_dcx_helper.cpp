// test/test_dcx_helper.cpp — DcxHelper decode function unit tests
// DCXヘルパー関数の単体テスト（decodePrefectureBitmask は test_decoder.cpp に移動）

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
