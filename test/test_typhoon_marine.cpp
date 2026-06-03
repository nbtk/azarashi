// test/test_typhoon_marine.cpp — 台風・海洋デコード関数の統合テスト
// test_typhoon.cpp と test_typhoon_marine.cpp を統合

#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

// ═══════════════════════════════════════════════════════════════════════════════
// 台風デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeTyphoon: 合成フレームでの基本動作（度分秒）") {
    uint8_t bits[32] = {};
    Message msg{};

    // IS-QZSS-DCR-016 Table 4.1.2-47 のビットレイアウトに基づく
    // reference_time: day=15, hour=12, minute=30 at bit 53
    setBits(bits, 53, 5, 15);       // day
    setBits(bits, 58, 5, 12);       // hour
    setBits(bits, 63, 6, 30);       // minute

    // ref_type: 1 (Analysis) at bit 69
    setBits(bits, 69, 3, 1);

    // elapsed: 24 at bit 80
    setBits(bits, 80, 7, 24);

    // number: 5 at bit 87
    setBits(bits, 87, 7, 5);

    // scale: 3 at bit 94
    setBits(bits, 94, 4, 3);

    // intensity: 2 at bit 98
    setBits(bits, 98, 4, 2);

    // LatLon at bit 102 (41 bits): 北緯25度30分0秒, 東経130度15分0秒
    setBits(bits, 102, 1, 0);       // lat_ns = 0 (North)
    setBits(bits, 103, 7, 25);      // lat_deg = 25
    setBits(bits, 110, 6, 30);      // lat_min = 30
    setBits(bits, 116, 6, 0);       // lat_sec = 0
    setBits(bits, 122, 1, 0);       // lon_ew = 0 (East)
    setBits(bits, 123, 8, 130);     // lon_deg = 130
    setBits(bits, 131, 6, 15);      // lon_min = 15
    setBits(bits, 137, 6, 0);       // lon_sec = 0

    // Central pressure: 980 hPa at bit 143 (11 bits)
    setBits(bits, 143, 11, 980);

    // Max wind speed: 35 m/s at bit 154 (7 bits)
    setBits(bits, 154, 7, 35);

    // Max gust speed: 50 m/s at bit 161 (7 bits)
    setBits(bits, 161, 7, 50);

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

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
    setBits(bits, 102, 1, 1);       // lat_ns = 1 (South)
    setBits(bits, 103, 7, 10);      // lat_deg = 10
    setBits(bits, 110, 6, 0);       // lat_min = 0
    setBits(bits, 116, 6, 0);       // lat_sec = 0
    setBits(bits, 122, 1, 1);       // lon_ew = 1 (West)
    setBits(bits, 123, 8, 140);     // lon_deg = 140
    setBits(bits, 131, 6, 0);       // lon_min = 0
    setBits(bits, 137, 6, 0);       // lon_sec = 0

    // Central pressure: 950 hPa at bit 143
    setBits(bits, 143, 11, 950);

    // Max wind speed: 45 m/s at bit 154
    setBits(bits, 154, 7, 45);

    // Max gust speed: 60 m/s at bit 161
    setBits(bits, 161, 7, 60);

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

    CHECK(msg.mt43.typh.coords.lat_ns == 1);
    CHECK(msg.mt43.typh.coords.lat_deg == 10);
    CHECK(msg.mt43.typh.coords.lat_min == 0);
    CHECK(msg.mt43.typh.coords.lat_sec == 0);
    CHECK(msg.mt43.typh.coords.lon_ew == 1);
    CHECK(msg.mt43.typh.coords.lon_deg == 140);
    CHECK(msg.mt43.typh.coords.lon_min == 0);
    CHECK(msg.mt43.typh.coords.lon_sec == 0);

    CHECK(msg.mt43.typh.pressure == 950);
    CHECK(msg.mt43.typh.max_wind == 45);
    CHECK(msg.mt43.typh.max_gust == 60);
}

TEST_CASE("decodeTyphoon: ゼロ値の検証") {
    uint8_t bits[32] = {};
    Message msg{};

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

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

TEST_CASE("decodeTyphoon: 無効なデータの処理") {
    uint8_t bits[32] = {};
    Message msg{};

    // 最小限の設定
    setBits(bits, 8, 6, 43);        // msg_type
    setBits(bits, 17, 4, 12);       // disaster_category
    setBits(bits, 214, 6, 1);       // version

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

    // Message-level fields: decodeTyphoon does not modify these, so they remain at defaults
    CHECK(msg.msg_type == 0);
    CHECK(msg.valid == false);
    CHECK(msg.payload_type == MsgPayloadType::Empty);

    // Typhoon subfields: all zero since no typhoon data bits are set
    CHECK(msg.mt43.typh.ref_type == 0);
    CHECK(msg.mt43.typh.elapsed == 0);
    CHECK(msg.mt43.typh.number == 0);
    CHECK(msg.mt43.typh.scale == 0);
    CHECK(msg.mt43.typh.intensity == 0);

    // LatLon coordinates: all zero
    CHECK(msg.mt43.typh.coords.lat_ns == 0);
    CHECK(msg.mt43.typh.coords.lat_deg == 0);
    CHECK(msg.mt43.typh.coords.lat_min == 0);
    CHECK(msg.mt43.typh.coords.lat_sec == 0);
    CHECK(msg.mt43.typh.coords.lon_ew == 0);
    CHECK(msg.mt43.typh.coords.lon_deg == 0);
    CHECK(msg.mt43.typh.coords.lon_min == 0);
    CHECK(msg.mt43.typh.coords.lon_sec == 0);

    // Pressure / Wind / Gust: all zero
    CHECK(msg.mt43.typh.pressure == 0);
    CHECK(msg.mt43.typh.max_wind == 0);
    CHECK(msg.mt43.typh.max_gust == 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 海洋デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeMarine: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};

    // 海洋カテゴリのビット配置: warning_code(5) + region_code(14) at bit 53
    // エントリ1: warning_code=3, region_code=100
    setBits(bits, 53, 5, 3);        // warning_code
    setBits(bits, 58, 14, 100);     // region_code

    // エントリ2: warning_code=5, region_code=200
    setBits(bits, 72, 5, 5);        // warning_code
    setBits(bits, 77, 14, 200);     // region_code

    TestDecoder::testDecodeMarine(bits, msg);

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
        setBits(bits, off,      5, i + 1);       // warning_code
        setBits(bits, off + 5, 14, 1000 + i);    // region_code
    }

    TestDecoder::testDecodeMarine(bits, msg);

    CHECK(msg.mt43.marine.count <= 8);
    if (msg.mt43.marine.count == 8) {
        CHECK(msg.mt43.marine.entries[7].warning_code == 8);
        CHECK(msg.mt43.marine.entries[7].region_code == 1007);
    }
}
