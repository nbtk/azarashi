// test/decoder/test_qzqsm.cpp — MT=43 (QZQSM) デコーダテスト
// 津波、台風、海洋情報のデコードテストを統合

#include "../test_helpers.h"
#include "doctest.h"

using namespace azaraC;

// ═══════════════════════════════════════════════════════════════════════════════
// 津波デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("Tsunami Resolution") {
    uint8_t buf[32] = {};
    // MT43 Preamble: 0x53
    setBits(buf, 0, 8, 0x53);
    // MT: 43
    setBits(buf, 8, 6, 43);
    // Report Time: Month=4, Day=25, Hour=13, Min=0
    setBits(buf, 21, 4, 4);
    setBits(buf, 25, 5, 25);
    setBits(buf, 30, 5, 13);
    setBits(buf, 35, 6, 0);
    // Disaster Category: 5 (Tsunami)
    setBits(buf, 17, 4, 5);
    // Version: 1
    setBits(buf, 214, 6, 1);

    // Tsunami entry 0: Region=1, Height=2, Arrival: NextDay=1, Hour=1, Min=30
    setBits(buf, 84, 10, 1);  // Region
    setBits(buf, 94, 4, 2);   // Height
    setBits(buf, 98, 1, 1);   // NextDay
    setBits(buf, 99, 5, 1);   // Hour
    setBits(buf, 104, 6, 30); // Min

    // CRC
    uint32_t crc = crc24qRef(buf, 226);
    setBits(buf, 226, 24, crc);

    // 2026-04-25 13:00:00 UTC
    constexpr uint32_t NOW_TIMESTAMP = 1777122000;

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);

    REQUIRE(ok);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.tsunami.count == 1);

    // Arrival should be Day 26, 01:30
    TimeFields& arr = msg.mt43.tsunami.entries[0].arrival_time;
    CHECK(arr.day == 26);
    CHECK(arr.hour == 1);
    CHECK(arr.minute == 30);
    CHECK(arr.unix_time != 0);
}

TEST_CASE("NW Pacific Tsunami Resolution - Day Wrap") {
    uint8_t buf[32] = {};
    setBits(buf, 0, 8, 0x53);
    setBits(buf, 8, 6, 43);
    setBits(buf, 21, 4, 5);
    setBits(buf, 25, 5, 31);
    setBits(buf, 30, 5, 23);
    setBits(buf, 35, 6, 50);
    setBits(buf, 17, 4, 6);
    setBits(buf, 214, 6, 1);

    // NW Pac Tsunami entry 0
    setBits(buf, 56, 7, 1);     // Region
    setBits(buf, 63, 1, 1);     // NextDay
    setBits(buf, 64, 5, 0);     // Hour
    setBits(buf, 69, 6, 30);    // Min
    setBits(buf, 75, 9, 2);     // Height

    uint32_t crc = crc24qRef(buf, 226);
    setBits(buf, 226, 24, crc);

    constexpr uint32_t NOW_TIMESTAMP = 1780271400;

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);

    REQUIRE(ok);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.nw_pac.count == 1);

    TimeFields& arr = msg.mt43.nw_pac.entries[0].arrival_time;
    CHECK(arr.day == 1);
    CHECK(arr.hour == 0);
    CHECK(arr.minute == 30);
    CHECK(arr.unix_time != 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 台風デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeTyphoon: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 53, 5, 15);       // day
    setBits(bits, 58, 5, 12);       // hour
    setBits(bits, 63, 6, 30);       // minute
    setBits(bits, 69, 3, 1);        // ref_type
    setBits(bits, 80, 7, 24);       // elapsed
    setBits(bits, 87, 7, 5);        // number
    setBits(bits, 94, 4, 3);        // scale
    setBits(bits, 98, 4, 2);        // intensity

    // LatLon: 北緯25度30分0秒, 東経130度15分0秒
    setBits(bits, 102, 1, 0);       // lat_ns = 0 (North)
    setBits(bits, 103, 7, 25);      // lat_deg = 25
    setBits(bits, 110, 6, 30);      // lat_min = 30
    setBits(bits, 116, 6, 0);       // lat_sec = 0
    setBits(bits, 122, 1, 0);       // lon_ew = 0 (East)
    setBits(bits, 123, 8, 130);     // lon_deg = 130
    setBits(bits, 131, 6, 15);      // lon_min = 15
    setBits(bits, 137, 6, 0);       // lon_sec = 0

    setBits(bits, 143, 11, 980);    // Central pressure
    setBits(bits, 154, 7, 35);      // Max wind speed
    setBits(bits, 161, 7, 50);      // Max gust speed

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

    CHECK(msg.mt43.typh.ref_type == 1);
    CHECK(msg.mt43.typh.elapsed == 24);
    CHECK(msg.mt43.typh.number == 5);
    CHECK(msg.mt43.typh.scale == 3);
    CHECK(msg.mt43.typh.intensity == 2);
    CHECK(msg.mt43.typh.pressure == 980);
    CHECK(msg.mt43.typh.max_wind == 35);
    CHECK(msg.mt43.typh.max_gust == 50);
}

TEST_CASE("decodeTyphoon: 南緯・西経の検証") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 102, 1, 1);       // lat_ns = 1 (South)
    setBits(bits, 103, 7, 10);      // lat_deg = 10
    setBits(bits, 110, 6, 0);       // lat_min = 0
    setBits(bits, 116, 6, 0);       // lat_sec = 0
    setBits(bits, 122, 1, 1);       // lon_ew = 1 (West)
    setBits(bits, 123, 8, 140);     // lon_deg = 140
    setBits(bits, 131, 6, 0);       // lon_min = 0
    setBits(bits, 137, 6, 0);       // lon_sec = 0
    setBits(bits, 143, 11, 950);    // Central pressure
    setBits(bits, 154, 7, 45);      // Max wind speed
    setBits(bits, 161, 7, 60);      // Max gust speed

    TestDecoder::testDecodeTyphoon(bits, msg, 1704067200u);

    CHECK(msg.mt43.typh.coords.lat_ns == 1);
    CHECK(msg.mt43.typh.coords.lat_deg == 10);
    CHECK(msg.mt43.typh.coords.lon_ew == 1);
    CHECK(msg.mt43.typh.coords.lon_deg == 140);
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

    // エントリ1: warning_code=3, region_code=100
    setBits(bits, 53, 5, 3);
    setBits(bits, 58, 14, 100);

    // エントリ2: warning_code=5, region_code=200
    setBits(bits, 72, 5, 5);
    setBits(bits, 77, 14, 200);

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
        setBits(bits, off,      5, i + 1);
        setBits(bits, off + 5, 14, 1000 + i);
    }

    TestDecoder::testDecodeMarine(bits, msg);

    CHECK(msg.mt43.marine.count <= 8);
    if (msg.mt43.marine.count == 8) {
        CHECK(msg.mt43.marine.entries[7].warning_code == 8);
        CHECK(msg.mt43.marine.entries[7].region_code == 1007);
    }
}
