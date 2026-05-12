// test/test_latlon.cpp — LatLon変換関数の検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// extractLatLonはprotected staticなので、テスト用に継承して公開
struct TestDecoder2 : Decoder {
    static LatLon testExtractLatLon(const uint8_t* buf, uint16_t start) {
        return extractLatLon(buf, start);
    }
    static uint32_t testGetBits(const uint8_t* buf, uint16_t start, uint8_t len) {
        return getBits(buf, start, len);
    }
};

TEST_CASE("extractLatLon: 基本的な緯度経度抽出") {
    uint8_t buf[32] = {};

    // 緯度: 北緯35度30分45秒 (lat_ns=0, lat_d=35, lat_m=30, lat_s=45)
    // 経度: 東経139度45分30秒 (lon_ew=0, lon_d=139, lon_m=45, lon_s=30)
    // 41ビット: lat_ns(1) + lat_d(7) + lat_m(6) + lat_s(6) + lon_ew(1) + lon_d(8) + lon_m(6) + lon_s(6)

    // ビットをセットする補助関数
    auto setbits = [&](uint16_t start, uint8_t len, uint32_t value) {
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    };

    // 北緯35度 = lat_ns=0, lat_d=35 (0b0100011)
    // 30分 = lat_m=30 (0b011110)
    // 45秒 = lat_s=45 (0b101101)
    setbits(0, 1, 0);        // lat_ns = 0 (北)
    setbits(1, 7, 35);       // lat_d = 35
    setbits(8, 6, 30);       // lat_m = 30
    setbits(14, 6, 45);      // lat_s = 45

    // 東経139度 = lon_ew=0, lon_d=139 (0b10001011)
    // 45分 = lon_m=45 (0b101101)
    // 30秒 = lon_s=30 (0b011110)
    setbits(20, 1, 0);       // lon_ew = 0 (東)
    setbits(21, 8, 139);     // lon_d = 139
    setbits(29, 6, 45);      // lon_m = 45
    setbits(35, 6, 30);      // lon_s = 30

    LatLon ll = TestDecoder2::testExtractLatLon(buf, 0);

    CHECK(ll.lat_ns == 0);
    CHECK(ll.lat_deg == 35);
    CHECK(ll.lat_min == 30);
    CHECK(ll.lat_sec == 45);
    CHECK(ll.lon_ew == 0);
    CHECK(ll.lon_deg == 139);
    CHECK(ll.lon_min == 45);
    CHECK(ll.lon_sec == 30);
}

TEST_CASE("extractLatLon: 南緯と西経") {
    uint8_t buf[32] = {};

    auto setbits = [&](uint16_t start, uint8_t len, uint32_t value) {
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    };

    // 南緯33度 = lat_ns=1, lat_d=33
    // 西経151度 = lon_ew=1, lon_d=151
    setbits(0, 1, 1);        // lat_ns = 1 (南)
    setbits(1, 7, 33);       // lat_d = 33
    setbits(8, 6, 0);        // lat_m = 0
    setbits(14, 6, 0);       // lat_s = 0

    setbits(20, 1, 1);       // lon_ew = 1 (西)
    setbits(21, 8, 151);     // lon_d = 151
    setbits(29, 6, 0);       // lon_m = 0
    setbits(35, 6, 0);       // lon_s = 0

    LatLon ll = TestDecoder2::testExtractLatLon(buf, 0);

    CHECK(ll.lat_ns == 1);
    CHECK(ll.lat_deg == 33);
    CHECK(ll.lon_ew == 1);
    CHECK(ll.lon_deg == 151);
}

TEST_CASE("extractLatLon: 境界値テスト") {
    uint8_t buf[32] = {};

    auto setbits = [&](uint16_t start, uint8_t len, uint32_t value) {
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    };

    // 最大値: 北緯90度、東経180度
    setbits(0, 1, 0);        // lat_ns = 0
    setbits(1, 7, 90);       // lat_d = 90 (最大)
    setbits(8, 6, 59);       // lat_m = 59 (最大)
    setbits(14, 6, 59);      // lat_s = 59 (最大)

    setbits(20, 1, 0);       // lon_ew = 0
    setbits(21, 8, 180);     // lon_d = 180 (最大)
    setbits(29, 6, 59);      // lon_m = 59 (最大)
    setbits(35, 6, 59);      // lon_s = 59 (最大)

    LatLon ll = TestDecoder2::testExtractLatLon(buf, 0);

    CHECK(ll.lat_deg == 90);
    CHECK(ll.lat_min == 59);
    CHECK(ll.lat_sec == 59);
    CHECK(ll.lon_deg == 180);
    CHECK(ll.lon_min == 59);
    CHECK(ll.lon_sec == 59);
}
