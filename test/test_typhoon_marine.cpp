// test/test_typhoon_marine.cpp — 台風・海洋デコード関数の直接検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// テスト用にprotected関数を公開
struct TestDecoderTM : public Decoder {
    static void testDecodeTyphoon(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoderTM t;
        t.decodeTyphoon(bits, out, now_unix);
    }

    static void testDecodeMarine(const uint8_t* bits, Message& out) {
        TestDecoderTM t;
        t.decodeMarine(bits, out);
    }

    static void setBits(uint8_t* buf, uint16_t start, uint8_t len, uint32_t value) {
        if (len == 0) return;
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    }
};

TEST_CASE("decodeTyphoon: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};

    // IS-QZSS-DCR-016 Table 4.1.2-47 のビットレイアウトに基づく
    // reference_time: day=15, hour=12, minute=30 at bit 53
    TestDecoderTM::setBits(bits, 53, 5, 15);       // day
    TestDecoderTM::setBits(bits, 58, 5, 12);       // hour
    TestDecoderTM::setBits(bits, 63, 6, 30);       // minute

    // ref_type: 1 (Analysis) at bit 69
    TestDecoderTM::setBits(bits, 69, 3, 1);

    // elapsed: 24 at bit 80
    TestDecoderTM::setBits(bits, 80, 7, 24);

    // number: 5 at bit 87
    TestDecoderTM::setBits(bits, 87, 7, 5);

    // scale: 3 at bit 94
    TestDecoderTM::setBits(bits, 94, 4, 3);

    // intensity: 2 at bit 98
    TestDecoderTM::setBits(bits, 98, 4, 2);

    // LatLon at bit 102 (41 bits): 北緯25度30分0秒, 東経130度15分0秒
    // lat_ns=0(N), lat_deg=25, lat_min=30, lat_sec=0
    // lon_ew=0(E), lon_deg=130, lon_min=15, lon_sec=0
    TestDecoderTM::setBits(bits, 102, 1, 0);       // lat_ns = 0 (North)
    TestDecoderTM::setBits(bits, 103, 7, 25);      // lat_deg = 25
    TestDecoderTM::setBits(bits, 110, 6, 30);      // lat_min = 30
    TestDecoderTM::setBits(bits, 116, 6, 0);       // lat_sec = 0
    TestDecoderTM::setBits(bits, 122, 1, 0);       // lon_ew = 0 (East)
    TestDecoderTM::setBits(bits, 123, 8, 130);     // lon_deg = 130
    TestDecoderTM::setBits(bits, 131, 6, 15);      // lon_min = 15
    TestDecoderTM::setBits(bits, 137, 6, 0);       // lon_sec = 0

    // Central pressure: 980 hPa at bit 143 (11 bits)
    TestDecoderTM::setBits(bits, 143, 11, 980);

    // Max wind speed: 35 m/s at bit 154 (7 bits)
    TestDecoderTM::setBits(bits, 154, 7, 35);

    // Max gust speed: 50 m/s at bit 161 (7 bits)
    TestDecoderTM::setBits(bits, 161, 7, 50);

    // 2024-01-01 00:00:00 UTC
    TestDecoderTM::testDecodeTyphoon(bits, msg, 1704067200u);

    // 結果を検証
    CHECK(msg.mt43.typh.ref_type == 1);
    CHECK(msg.mt43.typh.elapsed == 24);
    CHECK(msg.mt43.typh.number == 5);
    CHECK(msg.mt43.typh.scale == 3);
    CHECK(msg.mt43.typh.intensity == 2);

    // LatLon 検証
    CHECK(msg.mt43.typh.coords.lat_ns == 0);
    CHECK(msg.mt43.typh.coords.lat_deg == 25);
    CHECK(msg.mt43.typh.coords.lat_min == 30);
    CHECK(msg.mt43.typh.coords.lat_sec == 0);
    CHECK(msg.mt43.typh.coords.lon_ew == 0);
    CHECK(msg.mt43.typh.coords.lon_deg == 130);
    CHECK(msg.mt43.typh.coords.lon_min == 15);
    CHECK(msg.mt43.typh.coords.lon_sec == 0);

    // Pressure / Wind / Gust 検証
    CHECK(msg.mt43.typh.pressure == 980);
    CHECK(msg.mt43.typh.max_wind == 35);
    CHECK(msg.mt43.typh.max_gust == 50);
}

TEST_CASE("decodeTyphoon: 南緯・西経の検証") {
    uint8_t bits[32] = {};
    Message msg{};

    // LatLon at bit 102 (41 bits): 南緯10度0分0秒, 西経140度0分0秒
    // lat_ns=1(S), lat_deg=10, lat_min=0, lat_sec=0
    // lon_ew=1(W), lon_deg=140, lon_min=0, lon_sec=0
    TestDecoderTM::setBits(bits, 102, 1, 1);       // lat_ns = 1 (South)
    TestDecoderTM::setBits(bits, 103, 7, 10);      // lat_deg = 10
    TestDecoderTM::setBits(bits, 110, 6, 0);       // lat_min = 0
    TestDecoderTM::setBits(bits, 116, 6, 0);       // lat_sec = 0
    TestDecoderTM::setBits(bits, 122, 1, 1);       // lon_ew = 1 (West)
    TestDecoderTM::setBits(bits, 123, 8, 140);     // lon_deg = 140
    TestDecoderTM::setBits(bits, 131, 6, 0);       // lon_min = 0
    TestDecoderTM::setBits(bits, 137, 6, 0);       // lon_sec = 0

    // Central pressure: 950 hPa at bit 143
    TestDecoderTM::setBits(bits, 143, 11, 950);

    // Max wind speed: 45 m/s at bit 154
    TestDecoderTM::setBits(bits, 154, 7, 45);

    // Max gust speed: 60 m/s at bit 161
    TestDecoderTM::setBits(bits, 161, 7, 60);

    TestDecoderTM::testDecodeTyphoon(bits, msg, 1704067200u);

    // LatLon 検証
    CHECK(msg.mt43.typh.coords.lat_ns == 1);
    CHECK(msg.mt43.typh.coords.lat_deg == 10);
    CHECK(msg.mt43.typh.coords.lat_min == 0);
    CHECK(msg.mt43.typh.coords.lat_sec == 0);
    CHECK(msg.mt43.typh.coords.lon_ew == 1);
    CHECK(msg.mt43.typh.coords.lon_deg == 140);
    CHECK(msg.mt43.typh.coords.lon_min == 0);
    CHECK(msg.mt43.typh.coords.lon_sec == 0);

    // Pressure / Wind / Gust 検証
    CHECK(msg.mt43.typh.pressure == 950);
    CHECK(msg.mt43.typh.max_wind == 45);
    CHECK(msg.mt43.typh.max_gust == 60);
}

TEST_CASE("decodeTyphoon: ゼロ値の検証") {
    uint8_t bits[32] = {};
    Message msg{};

    // すべてのフィールドをゼロで設定
    // LatLon = 0 (lat_ns=0, lat_deg=0, lat_min=0, lat_sec=0, lon_ew=0, lon_deg=0, lon_min=0, lon_sec=0)
    // pressure = 0, max_wind = 0, max_gust = 0

    TestDecoderTM::testDecodeTyphoon(bits, msg, 1704067200u);

    // すべてゼロであることを検証
    CHECK(msg.mt43.typh.coords.lat_ns == 0);
    CHECK(msg.mt43.typh.coords.lat_deg == 0);
    CHECK(msg.mt43.typh.coords.lat_min == 0);
    CHECK(msg.mt43.typh.coords.lat_sec == 0);
    CHECK(msg.mt43.typh.coords.lon_ew == 0);
    CHECK(msg.mt43.typh.coords.lon_deg == 0);
    CHECK(msg.mt43.typh.coords.lon_min == 0);
    CHECK(msg.mt43.typh.coords.lon_sec == 0);
    CHECK(msg.mt43.typh.pressure == 0);
    CHECK(msg.mt43.typh.max_wind == 0);
    CHECK(msg.mt43.typh.max_gust == 0);
}

TEST_CASE("decodeMarine: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};

    // 海洋カテゴリのビット配置: warning_code(5) + region_code(14) at bit 53
    // エントリ1: warning_code=3, region_code=100
    TestDecoderTM::setBits(bits, 53, 5, 3);        // warning_code
    TestDecoderTM::setBits(bits, 58, 14, 100);     // region_code

    // エントリ2: warning_code=5, region_code=200
    TestDecoderTM::setBits(bits, 72, 5, 5);        // warning_code
    TestDecoderTM::setBits(bits, 77, 14, 200);     // region_code

    TestDecoderTM::testDecodeMarine(bits, msg);

    CHECK(msg.mt43.marine.count == 2);
    if (msg.mt43.marine.count >= 2) {
        CHECK(msg.mt43.marine.entries[0].warning_code == 3);
        CHECK(msg.mt43.marine.entries[0].region_code == 100);
        CHECK(msg.mt43.marine.entries[1].warning_code == 5);
        CHECK(msg.mt43.marine.entries[1].region_code == 200);
    }
}

TEST_CASE("decodeMarine: 最大エントリ数の検証") {
    uint8_t bits[32] = {};
    Message msg{};

    // 8エントリを設定
    for (int i = 0; i < 8; i++) {
        uint16_t off = 53 + i * 19;
        TestDecoderTM::setBits(bits, off,      5, i+1);  // warning_code
        TestDecoderTM::setBits(bits, off +  5, 14, 1000 + i); // region_code
    }

    TestDecoderTM::testDecodeMarine(bits, msg);

    // marine.countは最大8になるはず
    CHECK(msg.mt43.marine.count <= 8);
    if (msg.mt43.marine.count == 8) {
        CHECK(msg.mt43.marine.entries[7].warning_code == 8);
        CHECK(msg.mt43.marine.entries[7].region_code == 1007);
    }
}
