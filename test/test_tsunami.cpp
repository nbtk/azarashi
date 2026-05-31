// test/test_tsunami.cpp — 津波時間解決テスト
#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

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
    // Disaster Category: 5 (Tsunami) — IS-QZSS-DCR-016
    setBits(buf, 17, 4, 5);
    // Version: 1
    setBits(buf, 214, 6, 1);

    // Tsunami entry 0: Region=1, Height=2, Arrival: NextDay=1, Hour=1, Min=30
    // off = 84 + 0*26 = 84
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
    // MT43 Preamble: 0x53
    setBits(buf, 0, 8, 0x53);
    // MT: 43
    setBits(buf, 8, 6, 43);
    // Report Time: Month=5, Day=31, Hour=23, Min=50
    setBits(buf, 21, 4, 5);
    setBits(buf, 25, 5, 31);
    setBits(buf, 30, 5, 23);
    setBits(buf, 35, 6, 50);
    // Disaster Category: 6 (NW Pacific Tsunami)
    setBits(buf, 17, 4, 6);
    // Version: 1
    setBits(buf, 214, 6, 1);

    // NW Pac Tsunami entry 0: Region=1, Arrival: NextDay=1, Hour=0, Min=30, Height=2
    // off = 56 + 0*28 = 56
    setBits(buf, 56, 7, 1);     // Region
    setBits(buf, 63, 1, 1);     // NextDay (arrival_time_raw >> 11)
    setBits(buf, 64, 5, 0);     // Hour
    setBits(buf, 69, 6, 30);    // Min
    setBits(buf, 75, 9, 2);     // Height

    // CRC
    uint32_t crc = crc24qRef(buf, 226);
    setBits(buf, 226, 24, crc);

    // 2026-05-31 23:50:00 UTC
    constexpr uint32_t NOW_TIMESTAMP = 1780271400;

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);

    REQUIRE(ok);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.nw_pac.count == 1);

    // Arrival should be Day 1 (June 1st), 00:30
    TimeFields& arr = msg.mt43.nw_pac.entries[0].arrival_time;
    CHECK(arr.day == 1);
    CHECK(arr.hour == 0);
    CHECK(arr.minute == 30);
    CHECK(arr.unix_time != 0);
}
