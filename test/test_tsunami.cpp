
#define ARDUINO 0
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstdio>
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;



static uint32_t crc24q_ref(const uint8_t* d, int total_bits) {
    uint32_t crc = 0;
    int bytes = (total_bits + 7) / 8;
    for (int i = 0; i < bytes; i++) {
        uint8_t b = d[i];
        int bits_to_process = 8;
        if (i == bytes-1 && (total_bits&7)) {
            b &= 0xFFu << (8-(total_bits&7));
            bits_to_process = total_bits & 7;
        }
        crc ^= (uint32_t)b << 16;
        for (int j = 0; j < bits_to_process; j++) {
            crc <<= 1;
            if (crc & 0x1000000) crc ^= 0x1864CFB;
        }
    }
    return crc & 0xFFFFFF;
}

static void setbits(uint8_t* buf, size_t buf_size, uint16_t s, uint8_t l, uint32_t v) {
    REQUIRE((size_t)(s + l + 7) / 8 <= buf_size);
    for (int i = l-1; i >= 0; --i) {
        uint16_t pos = s + (l-1-i);
        if ((v >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
        else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
    }
}

TEST_CASE("Tsunami Resolution") {
    uint8_t buf[32] = {};
    // MT43 Preamble: 0x53
    setbits(buf, sizeof(buf), 0, 8, 0x53);
    // MT: 43
    setbits(buf, sizeof(buf), 8, 6, 43);
    // Report Time: Month=4, Day=25, Hour=13, Min=0
    setbits(buf, sizeof(buf), 21, 4, 4);
    setbits(buf, sizeof(buf), 25, 5, 25);
    setbits(buf, sizeof(buf), 30, 5, 13);
    setbits(buf, sizeof(buf), 35, 6, 0);
    // Disaster Category: 5 (Tsunami) — IS-QZSS-DCR-010
    setbits(buf, sizeof(buf), 17, 4, 5);
    // Version: 1
    setbits(buf, sizeof(buf), 214, 6, 1);

    // Tsunami entry 0: Region=1, Height=2, Arrival: NextDay=1, Hour=1, Min=30
    // off = 84 + 0*26 = 84
    setbits(buf, sizeof(buf), 84, 10, 1);  // Region
    setbits(buf, sizeof(buf), 94, 4, 2);   // Height
    setbits(buf, sizeof(buf), 98, 1, 1);   // NextDay
    setbits(buf, sizeof(buf), 99, 5, 1);   // Hour
    setbits(buf, sizeof(buf), 104, 6, 30); // Min

    // CRC
    uint32_t crc = crc24q_ref(buf, 226);
    setbits(buf, sizeof(buf), 226, 24, crc);

    // 2026-04-25 13:00:00 UTC
    // = days_since_1970(2026,4,25) * 86400 + 13 * 3600
    constexpr uint32_t NOW_TIMESTAMP = 1777122000;

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);

    REQUIRE(ok);
    CHECK(msg.tsunami_count == 1);

    // Arrival should be Day 26, 01:30
    TimeFields& arr = msg.tsunamis[0].arrival_time;
    CHECK(arr.day == 26);
    CHECK(arr.hour == 1);
    CHECK(arr.minute == 30);
    CHECK(arr.unix_time != 0);
}

TEST_CASE("NW Pacific Tsunami Resolution - Day Wrap") {
    uint8_t buf[32] = {};
    // MT43 Preamble: 0x53
    setbits(buf, sizeof(buf), 0, 8, 0x53);
    // MT: 43
    setbits(buf, sizeof(buf), 8, 6, 43);
    // Report Time: Month=5, Day=31, Hour=23, Min=50
    setbits(buf, sizeof(buf), 21, 4, 5);
    setbits(buf, sizeof(buf), 25, 5, 31);
    setbits(buf, sizeof(buf), 30, 5, 23);
    setbits(buf, sizeof(buf), 35, 6, 50);
    // Disaster Category: 6 (NW Pacific Tsunami)
    setbits(buf, sizeof(buf), 17, 4, 6);
    // Version: 1
    setbits(buf, sizeof(buf), 214, 6, 1);

    // NW Pac Tsunami entry 0: Region=1, Arrival: NextDay=1, Hour=0, Min=30, Height=2
    // off = 56 + 0*28 = 56
    setbits(buf, sizeof(buf), 56, 7, 1);     // Region
    setbits(buf, sizeof(buf), 63, 1, 1);     // NextDay (arrival_time_raw >> 11)
    setbits(buf, sizeof(buf), 64, 5, 0);     // Hour
    setbits(buf, sizeof(buf), 69, 6, 30);    // Min
    setbits(buf, sizeof(buf), 75, 9, 2);     // Height

    // CRC
    uint32_t crc = crc24q_ref(buf, 226);
    setbits(buf, sizeof(buf), 226, 24, crc);

    // 2026-05-31 23:50:00 UTC
    constexpr uint32_t NOW_TIMESTAMP = 1780271400;

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg, NOW_TIMESTAMP);

    REQUIRE(ok);
    CHECK(msg.nw_pac_count == 1);

    // Arrival should be Day 1 (June 1st), 00:30
    TimeFields& arr = msg.nw_pac_tsunamis[0].arrival_time;
    CHECK(arr.day == 1);
    CHECK(arr.hour == 0);
    CHECK(arr.minute == 30);
    CHECK(arr.unix_time != 0);
}
