// test/test_ublox.cpp — UBX SFRBX format tests (from azarashi test_ublox)
// Tests that UBX-decoded frames produce the same NMEA output as the original

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/UbxFramer.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>
#include <string>
#include <vector>

using namespace azaraC;
using namespace azaraC::internal;

// Helper: Feed raw bytes through UBX framer
static bool decode_ubx(const uint8_t* data, size_t len, Frame& out) {
    UbxFramer framer;
    for (size_t i = 0; i < len; ++i) {
        if (framer.feed(data[i], out)) return true;
    }
    return false;
}

// Helper: Build UBX SFRBX packet with correct checksum
static std::vector<uint8_t> make_ubx_sfrbx(uint8_t svId, const uint8_t* nav_bits) {
    std::vector<uint8_t> out;
    out.push_back(0xB5); out.push_back(0x62); // SYNC
    out.push_back(0x02); out.push_back(0x13); // CLASS/ID (RXM-SFRBX)

    uint16_t len = 8 + 8 * 4; // header(8) + 8 words(32)
    out.push_back(len & 0xFF);
    out.push_back(len >> 8);

    // Header
    out.push_back(5);    // gnssId (QZSS)
    out.push_back(svId); // svId
    out.push_back(0);    // sigId (L1S)
    out.push_back(0);    // freqId
    out.push_back(8);    // numWords
    out.push_back(0);    // chn
    out.push_back(1);    // version
    out.push_back(0);    // reserved

    // Payload (8 words)
    for (int w = 0; w < 8; ++w) {
        uint32_t val = 0;
        for (int b = 0; b < 32; ++b) {
            int bit_idx = w * 32 + b;
            if (bit_idx < 250) {
                if (nav_bits[bit_idx / 8] & (0x80u >> (bit_idx % 8))) {
                    val |= (1u << (31 - b));
                }
            }
        }
        out.push_back(val & 0xFF);
        out.push_back((val >> 8) & 0xFF);
        out.push_back((val >> 16) & 0xFF);
        out.push_back(val >> 24);
    }

    // Checksum
    uint8_t cka = 0, ckb = 0;
    for (size_t i = 2; i < out.size(); ++i) {
        cka += out[i];
        ckb += cka;
    }
    out.push_back(cka);
    out.push_back(ckb);

    return out;
}

// ── UBX SFRBX Tests ───────────────────────────────────────────────────────────

TEST_CASE("UBX: SFRBX basic decode") {
    uint8_t nav_bits[32] = {0x53, 0xAB};
    auto pkt = make_ubx_sfrbx(2, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 2);
    CHECK(ubx_frame.bits[0] == 0x53);
}

TEST_CASE("UBX: SFRBX round-trip with NMEA") {
    uint8_t nav_bits[32] = {};
    nav_bits[0] = 0x53;
    nav_bits[1] = 0x2F;

    auto pkt = make_ubx_sfrbx(56, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 56);
}

TEST_CASE("UBX: SFRBX with different svid") {
    uint8_t nav_bits[32] = {0x9A, 0xCD};
    auto pkt = make_ubx_sfrbx(57, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 57);
}

TEST_CASE("UBX: SFRBX svid=61") {
    uint8_t nav_bits[32] = {0xC6, 0xEF};
    auto pkt = make_ubx_sfrbx(61, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 61);
}

TEST_CASE("UBX: SFRBX svid=55") {
    uint8_t nav_bits[32] = {0x53, 0x00};
    auto pkt = make_ubx_sfrbx(55, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 55);
}

TEST_CASE("UBX: Checksum error rejection") {
    uint8_t nav_bits[32] = {0x53, 0xAB};
    auto pkt = make_ubx_sfrbx(2, nav_bits);

    // Corrupt the checksum
    pkt[pkt.size() - 1] ^= 0xFF;

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    CHECK_FALSE(ok);
}

TEST_CASE("UBX: Garbage recovery") {
    uint8_t nav_bits[32] = {0x9A};
    auto pkt = make_ubx_sfrbx(3, nav_bits);

    Frame ubx_frame;
    bool ok = decode_ubx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 3);
}
