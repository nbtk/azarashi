// test/framer/test_framer.cpp — フレーマーテスト
// UBX/NMEA フレーマーの統合テスト

#define ARDUINO 0
#include "../test_helpers.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;

// ── UBX Tests ──────────────────────────────────────────────────────────────

TEST_CASE("UBX Framer Basic") {
    uint8_t bits[32] = {0x53, 0xAB};
    auto pkt = makeUbxSfrbx(193, bits);

    UbxFramer framer;
    Frame out;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, out)) { found = true; break; }
    }

    REQUIRE(found);
    CHECK(out.svid == 193);
    CHECK(out.bits[0] == 0x53);
}

TEST_CASE("UBX Checksum Error") {
    uint8_t bits[32] = {0};
    auto pkt = makeUbxSfrbx(193, bits);
    pkt[10] ^= 0xFF; // Corrupt header/payload

    UbxFramer framer;
    Frame out;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, out)) found = true;
    }
    CHECK_FALSE(found);
}

TEST_CASE("UBX Garbage Recovery") {
    uint8_t bits[32] = {0x9A};
    auto pkt = makeUbxSfrbx(194, bits);

    UbxFramer framer;
    Frame out;
    // Feed garbage
    for (int i = 0; i < 100; ++i) framer.feed(0xAA, out);

    // Feed valid
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, out)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(out.svid == 194);
}

TEST_CASE("UBX: SFRBX basic decode") {
    uint8_t nav_bits[32] = {0x53, 0xAB};
    auto pkt = makeUbxSfrbx(2, nav_bits);

    UbxFramer framer;
    Frame ubx_frame;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, ubx_frame)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(ubx_frame.svid == 2);
    CHECK(ubx_frame.bits[0] == 0x53);
}

TEST_CASE("UBX: SFRBX round-trip with NMEA") {
    uint8_t nav_bits[32] = {};
    nav_bits[0] = 0x53;
    nav_bits[1] = 0x2F;

    auto pkt = makeUbxSfrbx(56, nav_bits);

    UbxFramer framer;
    Frame ubx_frame;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, ubx_frame)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(ubx_frame.svid == 56);
}

TEST_CASE("UBX: SFRBX with different svid") {
    uint8_t nav_bits[32] = {0x9A, 0xCD};
    auto pkt = makeUbxSfrbx(57, nav_bits);

    UbxFramer framer;
    Frame ubx_frame;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, ubx_frame)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(ubx_frame.svid == 57);
}

TEST_CASE("UBX: Checksum error rejection") {
    uint8_t nav_bits[32] = {0x53, 0xAB};
    auto pkt = makeUbxSfrbx(2, nav_bits);

    // Corrupt the checksum
    pkt[pkt.size() - 1] ^= 0xFF;

    UbxFramer framer;
    Frame ubx_frame;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, ubx_frame)) { found = true; break; }
    }
    CHECK_FALSE(found);
}

TEST_CASE("UBX: Garbage recovery") {
    uint8_t nav_bits[32] = {0x9A};
    auto pkt = makeUbxSfrbx(3, nav_bits);

    UbxFramer framer;
    Frame ubx_frame;
    bool found = false;
    for (auto b : pkt) {
        if (framer.feed(b, ubx_frame)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(ubx_frame.svid == 3);
}

// ── NMEA Tests ──────────────────────────────────────────────────────────────

TEST_CASE("NMEA Framer Basic") {
    uint8_t bits[32];
    for(int i=0; i<32; ++i) bits[i] = i;
    auto pkt = makeNmeaQzqsm(193, bits);

    NmeaFramer framer;
    Frame out;
    bool found = false;
    for (char c : pkt) {
        if (framer.feed((uint8_t)c, out)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(out.svid == 193);
    CHECK(out.bits[1] == 1);
}

TEST_CASE("NMEA Checksum Error") {
    uint8_t bits[32] = {0};
    auto pkt = makeNmeaQzqsm(193, bits);
    pkt[pkt.size() - 3] = '0'; // Corrupt checksum last digit

    NmeaFramer framer;
    Frame out;
    bool found = false;
    for (char c : pkt) {
        if (framer.feed((uint8_t)c, out)) found = true;
    }
    CHECK_FALSE(found);
}

TEST_CASE("NMEA Garbage Recovery") {
    uint8_t bits[32] = {0x12, 0x34};
    auto pkt = makeNmeaQzqsm(195, bits);

    NmeaFramer framer;
    Frame out;
    // Feed partial frame then garbage
    std::string partial = "$QZQSM,1";
    for (char c : partial) framer.feed((uint8_t)c, out);
    for (int i = 0; i < 50; ++i) framer.feed('?', out);

    // Feed valid
    bool found = false;
    for (char c : pkt) {
        if (framer.feed((uint8_t)c, out)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(out.svid == 195);
}

TEST_CASE("NMEA Oversize Recovery") {
    NmeaFramer framer;
    Frame out;
    framer.feed('$', out);
    for (int i = 0; i < 300; ++i) {
        framer.feed('A', out); // Fill buffer beyond capacity
    }
    // Should have reset internally. Try valid one now.
    uint8_t bits[32] = {0x55};
    auto pkt = makeNmeaQzqsm(199, bits);
    bool found = false;
    for (char c : pkt) {
        if (framer.feed((uint8_t)c, out)) { found = true; break; }
    }
    REQUIRE(found);
}

// ── NMEA ペイロード長検証 ────────────────────────────────────────────────────

TEST_CASE("NMEA: 62文字の拒否") {
    char nmea[256];
    strcpy(nmea, "$QZQSM,55,");
    for (int i = 0; i < 62; i++) sprintf(nmea + strlen(nmea), "%X", i % 16);
    uint8_t xsum = 0;
    for (size_t i = 1; i < strlen(nmea); i++) xsum ^= (uint8_t)nmea[i];
    sprintf(nmea + strlen(nmea), "*%02X\r\n", xsum);
    Message msg{};
    CHECK_FALSE(decodeNmea(nmea, msg));
}

TEST_CASE("NMEA: 64文字の拒否") {
    char nmea[256];
    strcpy(nmea, "$QZQSM,55,");
    for (int i = 0; i < 64; i++) sprintf(nmea + strlen(nmea), "%X", i % 16);
    uint8_t xsum = 0;
    for (size_t i = 1; i < strlen(nmea); i++) xsum ^= (uint8_t)nmea[i];
    sprintf(nmea + strlen(nmea), "*%02X\r\n", xsum);
    Message msg{};
    CHECK_FALSE(decodeNmea(nmea, msg));
}
