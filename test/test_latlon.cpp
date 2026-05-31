// test/test_latlon.cpp — LatLon変換関数の検証
#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

TEST_CASE("extractLatLon: 基本的な緯度経度抽出") {
    uint8_t buf[32] = {};

    // 緯度: 北緯35度30分45秒 (lat_ns=0, lat_d=35, lat_m=30, lat_s=45)
    // 経度: 東経139度45分30秒 (lon_ew=0, lon_d=139, lon_m=45, lon_s=30)
    // 41ビット: lat_ns(1) + lat_d(7) + lat_m(6) + lat_s(6) + lon_ew(1) + lon_d(8) + lon_m(6) + lon_s(6)

    setBits(buf, 0, 1, 0);        // lat_ns = 0 (北)
    setBits(buf, 1, 7, 35);       // lat_d = 35
    setBits(buf, 8, 6, 30);       // lat_m = 30
    setBits(buf, 14, 6, 45);      // lat_s = 45

    setBits(buf, 20, 1, 0);       // lon_ew = 0 (東)
    setBits(buf, 21, 8, 139);     // lon_d = 139
    setBits(buf, 29, 6, 45);      // lon_m = 45
    setBits(buf, 35, 6, 30);      // lon_s = 30

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

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

    setBits(buf, 0, 1, 1);        // lat_ns = 1 (南)
    setBits(buf, 1, 7, 33);       // lat_d = 33
    setBits(buf, 8, 6, 0);        // lat_m = 0
    setBits(buf, 14, 6, 0);       // lat_s = 0

    setBits(buf, 20, 1, 1);       // lon_ew = 1 (西)
    setBits(buf, 21, 8, 151);     // lon_d = 151
    setBits(buf, 29, 6, 0);       // lon_m = 0
    setBits(buf, 35, 6, 0);       // lon_s = 0

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

    CHECK(ll.lat_ns == 1);
    CHECK(ll.lat_deg == 33);
    CHECK(ll.lon_ew == 1);
    CHECK(ll.lon_deg == 151);
}

TEST_CASE("extractLatLon: 境界値テスト") {
    uint8_t buf[32] = {};

    // 最大値: 北緯90度、東経180度
    setBits(buf, 0, 1, 0);        // lat_ns = 0
    setBits(buf, 1, 7, 90);       // lat_d = 90 (最大)
    setBits(buf, 8, 6, 59);       // lat_m = 59 (最大)
    setBits(buf, 14, 6, 59);      // lat_s = 59 (最大)

    setBits(buf, 20, 1, 0);       // lon_ew = 0
    setBits(buf, 21, 8, 180);     // lon_d = 180 (最大)
    setBits(buf, 29, 6, 59);      // lon_m = 59 (最大)
    setBits(buf, 35, 6, 59);      // lon_s = 59 (最大)

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

    CHECK(ll.lat_deg == 90);
    CHECK(ll.lat_min == 59);
    CHECK(ll.lat_sec == 59);
    CHECK(ll.lon_deg == 180);
    CHECK(ll.lon_min == 59);
    CHECK(ll.lon_sec == 59);
}
