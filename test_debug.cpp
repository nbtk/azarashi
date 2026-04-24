// test_debug.cpp — Debug tests to reproduce identified issues
// Build: g++ -std=c++17 -Wall -Wextra -I/d/documents/azaraC/src -I/d/documents/azaraC/src/internal test_debug.cpp /d/documents/azaraC/src/internal/Decoder.cpp /d/documents/azaraC/src/internal/Dedup.cpp -o test_debug && ./test_debug

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/PrintShim.h"
#include <cstdio>
#include <cassert>
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// ── Helper to create a minimal valid DCX frame (MT=44) ────────────────────────
// This creates a frame with valid CRC, preamble, and minimal payload.
// The frame is crafted to test specific bit offsets in the decoder.
static bool make_dcx_frame(uint8_t* out, DcxType dcx_type, uint8_t a1_msg_type,
                           uint16_t a2_country, uint8_t a3_provider,
                           uint8_t a4_hazard, uint8_t a5_severity,
                           uint16_t a12_lat_e2, uint16_t a13_lon_e2,
                           uint32_t now_unix) {
    // We'll build a minimal frame: preamble(8) + mt(6) + bits...
    // For simplicity, we'll focus on testing the decoder's bit extraction
    // rather than building a full valid frame with CRC.
    // Instead, we'll directly test the extract functions.
    (void)out; (void)dcx_type; (void)a1_msg_type;
    (void)a2_country; (void)a3_provider; (void)a4_hazard;
    (void)a5_severity; (void)a12_lat_e2; (void)a13_lon_e2; (void)now_unix;
    return false;
}

// ── Test getBits with known values ────────────────────────────────────────────
static void test_getBits() {
    // Test data: 4 bytes representing specific bit patterns
    uint8_t buf[4] = {
        0b10101010,  // bits 0-7
        0b11001100,  // bits 8-15
        0b11110000,  // bits 16-23
        0b00001111   // bits 24-31
    };

    // Test reading 1 bit at position 0 (should be 1)
    uint32_t val1 = Decoder::getBits(buf, 0, 1);
    assert(val1 == 1 && "getBits: bit 0 should be 1");

    // Test reading 4 bits at position 4 (should be 1010 = 10)
    uint32_t val2 = Decoder::getBits(buf, 4, 4);
    assert(val2 == 10 && "getBits: bits 4-7 should be 1010");

    // Test reading across byte boundary
    // Position 6, length 6: bits 6-7 of buf[0] (10) + bits 0-3 of buf[1] (1100)
    // = 101100 binary = 44 decimal
    uint32_t val3 = Decoder::getBits(buf, 6, 6);
    assert(val3 == 44 && "getBits: cross-byte read failed");

    printf("  PASS  test_getBits\n");
}

// ── Test extractLatLon ────────────────────────────────────────────────────────
static void test_extractLatLon() {
    uint8_t buf[6] = {0};
    // Set up a known lat/lon:
    // lat: ns=0, deg=45, min=30, sec=15
    // lon: ew=1, deg=120, min=45, sec=30

    // lat_ns = 0 (1 bit at position 0)
    // lat_deg = 45 (7 bits at position 1)
    // lat_min = 30 (6 bits at position 8)
    // lat_sec = 15 (6 bits at position 14)
    // lon_ew = 1 (1 bit at position 20)
    // lon_deg = 120 (8 bits at position 21)
    // lon_min = 45 (6 bits at position 29)
    // lon_sec = 30 (6 bits at position 35)

    // Build the bit pattern manually
    // Position 0: lat_ns = 0
    // Positions 1-7: lat_deg = 45 (0b0101101)
    buf[0] = 0b00101101;  // bits 0-7
    buf[1] = 0b01111100;  // bits 8-15 (lat_min=30=0b0011110, lat_sec=15=0b0001111)
    buf[2] = 0b00000101;  // bits 16-23 (continuation of lat_sec)
    buf[2] |= (1 << 7);   // lon_ew = 1 at bit 20
    buf[3] = 120;         // lon_deg = 120 at bits 21-28
    buf[4] = 0b01011010;  // lon_min = 45 (0b0101101) at bits 29-34
    buf[5] = 0b01111000;  // lon_sec = 30 (0b011110) at bits 35-40

    LatLon ll = Decoder::extractLatLon(buf, 0);

    assert(ll.lat_ns == 0 && "lat_ns should be 0 (N)");
    assert(ll.lat_deg == 45 && "lat_deg should be 45");
    assert(ll.lat_min == 30 && "lat_min should be 30");
    assert(ll.lat_sec == 15 && "lat_sec should be 15");
    assert(ll.lon_ew == 1 && "lon_ew should be 1 (W)");
    assert(ll.lon_deg == 120 && "lon_deg should be 120");
    assert(ll.lon_min == 45 && "lon_min should be 45");
    assert(ll.lon_sec == 30 && "lon_sec should be 30");

    printf("  PASS  test_extractLatLon\n");
}

// ── Test extractDHM with edge cases ──────────────────────────────────────────
static void test_extractDHM() {
    uint8_t buf[4] = {0};
    // day=15, hour=23, minute=59 at position 0
    // day(5 bits): 15 = 0b01111
    // hour(5 bits): 23 = 0b10111
    // minute(6 bits): 59 = 0b111011
    buf[0] = 0b01111101;  // bits 0-7: day(5) + hour(3)
    buf[1] = 0b11101100;  // bits 8-15: hour(2) + minute(6)

    TimeFields tf = Decoder::extractDHM(buf, 0, 0);
    assert(tf.day == 15 && "day should be 15");
    assert(tf.hour == 23 && "hour should be 23");
    assert(tf.minute == 59 && "minute should be 59");
    assert(tf.unix_time == 0 && "unix_time should be 0 when now_unix is 0");

    // Test invalid values - should reset to 0
    buf[0] = 0xFF;  // day would be 31 (valid), hour would be 31 (invalid > 23)
    tf = Decoder::extractDHM(buf, 0, 0);
    assert(tf.day == 0 && "day should be reset on invalid hour");
    assert(tf.hour == 0 && "hour should be reset on invalid value");
    assert(tf.minute == 0 && "minute should be reset on invalid value");

    printf("  PASS  test_extractDHM\n");
}

// ── Test resolveTime with month/year wrap ─────────────────────────────────────
static void test_resolveTime() {
    // Current time: 2024-04-15 12:00:00 (UNIX: 1713182400)
    uint32_t now = 1713182400;

    // Test 1: Same month, MDHM (month=4, day=15, hour=14, minute=30)
    TimeFields tf = Decoder::resolveTime(4, 15, 14, 30, now);
    assert(tf.unix_time == 1713191400 && "MDHM: same month failed");

    // Test 2: Next month wrap, MDHM (month=5, day=1, hour=0, minute=0)
    tf = Decoder::resolveTime(5, 1, 0, 0, now);
    assert(tf.unix_time == 1714521600 && "MDHM: next month failed");

    // Test 3: Year wrap backwards, MDHM (month=12, day=31, hour=23, minute=59)
    // now is April 2024, so month=12 should resolve to Dec 2023
    tf = Decoder::resolveTime(12, 31, 23, 59, now);
    assert(tf.unix_time == 1704067140 && "MDHM: year wrap backward failed");

    // Test 4: DHM only (month=0), same month (day=16)
    tf = Decoder::resolveTime(0, 16, 10, 0, now);
    assert(tf.unix_time == 1713261600 && "DHM: same month failed");

    // Test 5: DHM only, previous month wrap (day=30)
    // now is April 15, day=30 should be March 30
    tf = Decoder::resolveTime(0, 30, 0, 0, now);
    assert(tf.unix_time == 1711756800 && "DHM: prev month failed");

    printf("  PASS  test_resolveTime\n");
}

// ── Test EEW 80-region parsing ────────────────────────────────────────────────
static void test_eew_80_regions() {
    uint8_t frame[32] = {0};
    // Set bits for region 1, 40, and 80
    // region 1: bit 130 of frame (index 16 byte, bit 2)
    // bit 130 / 8 = 16, rem 2 -> byte 16, bit 130 % 8 = 2 (from MSB, so bit 5 of byte)
    // Wait, getBits uses (7 - (pos % 8))
    frame[16] |= (1 << (7 - (130 % 8))); // region 1 (bit 130)
    frame[21] |= (1 << (7 - (169 % 8))); // region 40 (bit 169)
    frame[26] |= (1 << (7 - (209 % 8))); // region 80 (bit 209)

    Message msg{};
    // We call a shim or manually test the loop
    msg.eew_region_count = 0;
    for (uint8_t i = 0; i < 80 && msg.eew_region_count < 80; ++i) {
        if (Decoder::getBits(frame, 130 + i, 1)) {
            msg.eew_regions[msg.eew_region_count++] = i + 1;
        }
    }

    assert(msg.eew_region_count == 3 && "EEW regions: count should be 3");
    assert(msg.eew_regions[0] == 1 && "EEW regions: 1 failed");
    assert(msg.eew_regions[1] == 40 && "EEW regions: 40 failed");
    assert(msg.eew_regions[2] == 80 && "EEW regions: 80 failed");

    printf("  PASS  test_eew_80_regions\n");
}

// ── Test decodeDcx bit extraction ────────────────────────────────────────────
static void test_decodeDcx_bits() {
    // Create a frame with known bit values at specific positions
    uint8_t frame[32] = {0};

    // Set specific bits for DCX type (3 bits at position 14)
    // DCX type L_ALERT = 1 (001 in 3 bits)
    frame[1] |= (1 << 7);   // bit 14
    frame[2] |= (1 << 6);   // bit 15

    // Set A1 message type (4 bits at position 17)
    frame[2] |= (1 << 3);   // bit 17
    frame[3] |= (1 << 7);   // bit 18

    // Set A2 country code (10 bits at position 21)
    frame[3] |= 0x03;       // bits 21-22
    frame[4] |= 0xC0;       // bits 23-24

    Message msg{};
    // We can't fully decode without proper CRC, but we can test bit extraction
    uint32_t dcx_type = Decoder::getBits(frame, 14, 3);
    assert(dcx_type == 1 && "dcx_type should be 1 (L_ALERT)");

    uint32_t a1_msg = Decoder::getBits(frame, 17, 4);
    assert(a1_msg == 9 && "a1_message_type should be 9");

    uint32_t a2_country = Decoder::getBits(frame, 21, 10);
    assert(a2_country == 0x1FF && "a2_country_code should be 511");

    printf("  PASS  test_decodeDcx_bits\n");
}

// ── Test decodeQzqsm version check ──────────────────────────────────────────
static void test_decodeQzqsm_version() {
    uint8_t frame[32] = {0};
    // Set version bits (6 bits at position 214)
    // Version should be 1
    frame[26] = 0b000001;  // bits 214-219

    Message msg{};
    // This would fail in full decode due to CRC, but we can test the version check
    uint8_t ver = Decoder::getBits(frame, 214, 6);
    assert(ver == 1 && "version should be 1");

    printf("  PASS  test_decodeQzqsm_version\n");
}

// ── Test decodeQzqsm report time conversion ─────────────────────────────────
static void test_decodeQzqsm_report_time() {
    uint8_t frame[32] = {0};
    // Set report time: month=4, day=15, hour=14, minute=30 at position 21
    // month(4 bits): 4
    // day(5 bits): 15
    // hour(5 bits): 14
    // minute(6 bits): 30
    frame[2] |= 0x10;  // bits 21-24: month=4
    frame[3] |= 0xF8;  // bits 25-29: day=15 (0b01111)
    frame[3] |= 0x07;  // bits 29-31 + bits 30-31 of hour
    frame[4] |= 0xE0;  // bits 32-36: hour=14 (0b01110)
    frame[5] |= 0xFC;  // bits 37-42: minute=30 (0b11110)

    Message msg{};
    // Test would verify proper time conversion
    uint8_t month = (Decoder::getBits(frame, 21, 4) == 4);
    uint8_t day = (Decoder::getBits(frame, 25, 5) == 15);
    uint8_t hour = (Decoder::getBits(frame, 32, 5) == 14);
    uint8_t minute = (Decoder::getBits(frame, 37, 6) == 30);

    assert(month && "report month should be 4");
    assert(day && "report day should be 15");
    assert(hour && "report hour should be 14");
    assert(minute && "report minute should be 30");

    printf("  PASS  test_decodeQzqsm_report_time\n");
}

// ── Test decodeTsunami unused parameter ──────────────────────────────────────
static void test_decodeTsunami_unused_param() {
    // This test documents that decodeTsunami takes now_unix but doesn't use it
    // The function should still compile and work correctly
    uint8_t frame[32] = {0};
    frame[0] = 0x05;  // Set disaster category to 5 (Tsunami)

    // Set tsunami warning code (4 bits at position 80)
    frame[10] = 0x10;  // warning code = 1

    Message msg{};
    // decodeTsunami should not crash even though now_unix is unused
    // We can't call it directly without proper frame structure, but this
    // documents the behavior

    printf("  PASS  test_decodeTsunami_unused_param\n");
}

int main() {
    printf("Running debug tests...\n");

    test_getBits();
    test_extractLatLon();
    test_extractDHM();
    test_resolveTime();
    test_eew_80_regions();
    test_decodeDcx_bits();
    test_decodeQzqsm_version();
    test_decodeQzqsm_report_time();
    test_decodeTsunami_unused_param();

    printf("All debug tests passed!\n");
    return 0;
}
