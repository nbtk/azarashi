
#define ARDUINO 0
#include "../src/internal/Decoder.h"
#include <cstdio>
#include <cstring>
#include <cassert>

using namespace azaraC;
using namespace azaraC::internal;

static void pass(const char* name) { printf("  PASS  %s\n", name); }
static void fail(const char* name, const char* why) {
    printf("  FAIL  %s : %s\n", name, why);
    assert(false);
}

static uint32_t crc24q_ref(const uint8_t* d, int bits) {
    uint32_t crc = 0;
    int bytes = (bits + 7) / 8;
    for (int i = 0; i < bytes; i++) {
        uint8_t b = d[i];
        int bits_to_process = 8;
        if (i == bytes-1 && (bits&7)) {
            b &= 0xFFu << (8-(bits&7));
            bits_to_process = bits & 7;
        }
        crc ^= (uint32_t)b << 16;
        for (int j = 0; j < bits_to_process; j++) {
            crc <<= 1;
            if (crc & 0x1000000) crc ^= 0x1864CFB;
        }
    }
    return crc & 0xFFFFFF;
}

static void setbits(uint8_t* buf, uint16_t s, uint8_t l, uint32_t v) {
    for (int i = l-1; i >= 0; --i) {
        uint16_t pos = s + (l-1-i);
        if ((v >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
        else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
    }
}

void test_tsunami_resolution() {
    uint8_t buf[32] = {};
    // MT43 Preamble: 0x53
    setbits(buf, 0, 8, 0x53);
    // MT: 43
    setbits(buf, 8, 6, 43);
    // Report Time: Month=4, Day=25, Hour=13, Min=0
    setbits(buf, 21, 4, 4);
    setbits(buf, 25, 5, 25);
    setbits(buf, 30, 5, 13);
    setbits(buf, 35, 6, 0);
    // Disaster Category: 2 (Tsunami)
    setbits(buf, 17, 4, 2);
    // Version: 1
    setbits(buf, 214, 6, 1);

    // Tsunami entry 0: Region=1, Height=2, Arrival: NextDay=1, Hour=1, Min=30
    // off = 84 + 0*26 = 84
    setbits(buf, 84, 10, 1);  // Region
    setbits(buf, 94, 4, 2);   // Height
    setbits(buf, 98, 1, 1);   // NextDay
    setbits(buf, 99, 5, 1);   // Hour
    setbits(buf, 104, 6, 30); // Min

    // CRC
    uint32_t crc = crc24q_ref(buf, 226);
    setbits(buf, 226, 24, crc);

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    // now = 2026-04-25 13:00:00 (approx)
    uint32_t now = 1777122000; 
    bool ok = dec.decode(f, msg, now);

    if (!ok) fail("tsunami_res", "decode failed");
    if (msg.tsunami_count != 1) fail("tsunami_res", "count != 1");
    
    // Arrival should be Day 26, 01:30
    TimeFields& arr = msg.tsunamis[0].arrival_time;
    if (arr.day != 26) fail("tsunami_res", "day mismatch");
    if (arr.hour != 1) fail("tsunami_res", "hour mismatch");
    if (arr.minute != 30) fail("tsunami_res", "min mismatch");
    if (arr.unix_time == 0) fail("tsunami_res", "unix_time is 0");

    pass("tsunami_res");
}

int main() {
    printf("=== azaraC tsunami tests ===\n");
    test_tsunami_resolution();
    printf("=== all passed ===\n");
    return 0;
}
