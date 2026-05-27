// test/test_dcx_helper.cpp — DcxHelper decode function unit tests
// Tests all DCX helper functions from DcxHelper.cpp

#define ARDUINO 0
#include "../src/internal/DcxHelper.h"
#include "doctest.h"
#include <cmath>

using namespace azaraC;
using namespace azaraC::internal;

// ── decodeLatitude16 ────────────────────────────────────────────────────────
// Latitude = -90 + (180 / 65535) * code

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
    // code = (lat + 90) * 65535 / 180 = (35.688 + 90) * 65535 / 180 ≈ 45761
    double lat = decodeLatitude16(45761);
    CHECK(lat >= 35.6);
    CHECK(lat <= 35.8);
}

// ── decodeLongitude17 ───────────────────────────────────────────────────────
// Longitude = -180 + (360 / 131071) * code

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
    // code = (lon + 180) * 131071 / 360 = (139.691 + 180) * 131071 / 360 ≈ 116395
    double lon = decodeLongitude17(116395);
    CHECK(lon >= 139.6);
    CHECK(lon <= 139.8);
}

// ── decodeLatitude17 ────────────────────────────────────────────────────────
// Latitude = -90 + (180 / 131071) * code

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
// Longitude = 45 + (180 / 131071) * code

TEST_CASE("decodeLongitude17_45_225: code=0 → 45.0") {
    CHECK(std::abs(decodeLongitude17_45_225(0) - 45.0) < 0.001);
}

TEST_CASE("decodeLongitude17_45_225: code=131071 → 225.0") {
    CHECK(std::abs(decodeLongitude17_45_225(131071) - 225.0) < 0.001);
}

TEST_CASE("decodeLongitude17_45_225: Tokyo area (~139.689°E)") {
    // code = (lon - 45) * 131071 / 180 = (139.689 - 45) * 131071 / 180 ≈ 68950
    double lon = decodeLongitude17_45_225(68950);
    CHECK(lon >= 139.6);
    CHECK(lon <= 139.8);
}

// ── decodeRadiusCode ────────────────────────────────────────────────────────
// IS-QZSS-DCX-003 Table 4.2-17

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
// Azimuth = -90 + (180 / 64) * code

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

TEST_CASE("decodeAzimuth6: code=48 → ~45.0 (Tokyo area)") {
    // code = (azimuth + 90) * 64 / 180 = (45 + 90) * 64 / 180 ≈ 48
    double az = decodeAzimuth6(48);
    CHECK(az >= 43.0);
    CHECK(az <= 47.0);
}

// ── decodeAzimuth7 ──────────────────────────────────────────────────────────
// Azimuth = -90 + (180 / 128) * code

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

TEST_CASE("decodeAzimuth7: code=96 → ~45.0 (Tokyo area)") {
    // code = (azimuth + 90) * 128 / 180 = (45 + 90) * 128 / 180 = 96
    double az = decodeAzimuth7(96);
    CHECK(az >= 44.0);
    CHECK(az <= 46.0);
}

// ── decodePrefectureBitmask ─────────────────────────────────────────────────
// EX9 64-bit field: [47-bit prefecture][17-bit reserved]
// Prefecture bits in ex9[63:17], bit 0 (LSB) = Hokkaido (JIS 1)

TEST_CASE("decodePrefectureBitmask: 北海道・青森・岩手（仕様書例）") {
    // IS-QZSS-DCX-003 §4.2.4.2.2 の例: 0b111 → Hokkaido, Aomori, Iwate
    uint64_t ex9 = (uint64_t)7 << 17;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 3);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[1] == 2);   // 青森県
    CHECK(positions[2] == 3);   // 岩手県
}

TEST_CASE("decodePrefectureBitmask: 沖縄のみ（MSB）") {
    uint64_t ex9 = (uint64_t)1 << 63;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 47);  // 沖縄県
}

TEST_CASE("decodePrefectureBitmask: 全都道府県（全ビット=1）") {
    uint64_t ex9 = ((1ULL << 47) - 1) << 17;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 47);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[46] == 47); // 沖縄県
}

TEST_CASE("decodePrefectureBitmask: 空（ゼロ）") {
    uint64_t ex9 = 0;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}

TEST_CASE("decodePrefectureBitmask: reservedビットは無視される") {
    uint64_t ex9 = (uint64_t)0xFFFF;  // bits [16:0] = all 1s
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}

TEST_CASE("decodePrefectureBitmask: ビット17だけ設定（北海道）") {
    uint64_t ex9 = (uint64_t)1 << 17;
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 1);  // 北海道
}

TEST_CASE("decodePrefectureBitmask: 東京（JIS 13）") {
    // Tokyo = JIS code 13 = bit 12 of 47-bit integer
    uint64_t ex9 = (uint64_t)1 << (12 + 17);
    uint8_t positions[47] = {};
    uint8_t count = decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 13);  // 東京都
}

// ── decodeCityCodeList ──────────────────────────────────────────────────────
// EX9 64-bit field: four 16-bit city/town/village codes

TEST_CASE("decodeCityCodeList: 1コード") {
    uint64_t ex9 = (uint64_t)1100;  // 札幌市
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
    // Code 1 = 0 (skip), Code 2 = 500, Code 3 = 0 (skip), Code 4 = 600
    uint64_t ex9 = ((uint64_t)500 << 16) | ((uint64_t)600 << 48);
    uint16_t codes[4] = {};
    uint8_t count = decodeCityCodeList(ex9, codes);

    CHECK(count == 2);
    CHECK(codes[0] == 500);
    CHECK(codes[1] == 600);
}
