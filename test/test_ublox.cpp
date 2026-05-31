// test/test_ublox.cpp — UBX SFRBX format tests
// UBXフォーマットのデコードテスト

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/UbxFramer.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include "../src/definition/ublox_qzss_svid_prn_map.h"
#include "doctest.h"
#include <cstring>
#include <string>
#include <vector>

using namespace azaraC;
using namespace azaraC::internal;
using namespace azaraC::def;

// Helper: Feed raw bytes through UBX framer
static bool decodeUbx(const uint8_t* data, size_t len, Frame& out) {
    UbxFramer framer;
    for (size_t i = 0; i < len; ++i) {
        if (framer.feed(data[i], out)) return true;
    }
    return false;
}

// Helper: Build UBX SFRBX packet with correct checksum
static std::vector<uint8_t> makeUbxSfrbx(uint8_t svId, const uint8_t* nav_bits) {
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
    auto pkt = makeUbxSfrbx(2, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 2);
    CHECK(ubx_frame.bits[0] == 0x53);
}

TEST_CASE("UBX: SFRBX round-trip with NMEA") {
    uint8_t nav_bits[32] = {};
    nav_bits[0] = 0x53;
    nav_bits[1] = 0x2F;

    auto pkt = makeUbxSfrbx(56, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 56);
}

TEST_CASE("UBX: SFRBX with different svid") {
    uint8_t nav_bits[32] = {0x9A, 0xCD};
    auto pkt = makeUbxSfrbx(57, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 57);
}

TEST_CASE("UBX: SFRBX svid=61") {
    uint8_t nav_bits[32] = {0xC6, 0xEF};
    auto pkt = makeUbxSfrbx(61, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 61);
}

TEST_CASE("UBX: SFRBX svid=55") {
    uint8_t nav_bits[32] = {0x53, 0x00};
    auto pkt = makeUbxSfrbx(55, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 55);
}

TEST_CASE("UBX: Checksum error rejection") {
    uint8_t nav_bits[32] = {0x53, 0xAB};
    auto pkt = makeUbxSfrbx(2, nav_bits);

    // Corrupt the checksum
    pkt[pkt.size() - 1] ^= 0xFF;

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    CHECK_FALSE(ok);
}

TEST_CASE("UBX: Garbage recovery") {
    uint8_t nav_bits[32] = {0x9A};
    auto pkt = makeUbxSfrbx(3, nav_bits);

    Frame ubx_frame;
    bool ok = decodeUbx(pkt.data(), pkt.size(), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 3);
}

// ── UBX Round-Trip Tests ──────────────────────────────────────────────────────

TEST_CASE("UBX: Round-trip svId=2 PRN=184") {
    const uint8_t ubx_data[] = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00, 0x05, 0x02, 0x01, 0x00, 0x09, 0x40, 0x02, 0x00,
        0xC5, 0xF1, 0xAD, 0x9A, 0x04, 0x05, 0x80, 0x11, 0x54, 0x8D, 0xA0, 0x60, 0x3F, 0x82,
        0xD2, 0x11, 0x0F, 0xAA, 0x7D, 0x50, 0x28, 0x0C, 0x43, 0xC9, 0x10, 0x00, 0x50, 0x7D,
        0x31, 0x79, 0xF0, 0x28, 0x73, 0x18, 0x10, 0xB2, 0x62, 0x2F
    };

    Frame ubx_frame;
    bool ok = decodeUbx(ubx_data, sizeof(ubx_data), ubx_frame);
    REQUIRE(ok);

    CHECK(ubx_frame.svid == 0x02);

    auto prn = ublox_qzss_svid_prn_map_lookup(ubx_frame.svid);
    REQUIRE(prn.has_value());
    CHECK(prn.value() == "184");
}

TEST_CASE("UBX: Round-trip svId=3 PRN=185") {
    const uint8_t ubx_data[] = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00, 0x05, 0x03, 0x01, 0x00, 0x09, 0x41, 0x02, 0x00,
        0xA1, 0xE5, 0xAD, 0xC6, 0x12, 0x02, 0x80, 0x36, 0x68, 0x00, 0x00, 0x01, 0x10, 0x50,
        0x34, 0x44, 0xD4, 0xEE, 0x00, 0x34, 0x00, 0x00, 0x00, 0x3C, 0x11, 0x00, 0x00, 0x00,
        0x14, 0x9C, 0x5F, 0x60, 0x26, 0xCB, 0xC0, 0xF2, 0xEF, 0x1A
    };

    Frame ubx_frame;
    bool ok = decodeUbx(ubx_data, sizeof(ubx_data), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 0x03);

    auto prn = ublox_qzss_svid_prn_map_lookup(ubx_frame.svid);
    REQUIRE(prn.has_value());
    CHECK(prn.value() == "185");
}

TEST_CASE("UBX: Round-trip svId=7 PRN=189") {
    const uint8_t ubx_data[] = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00, 0x05, 0x07, 0x01, 0x00, 0x09, 0x45, 0x02, 0x00,
        0xA1, 0xE5, 0xAD, 0xC6, 0x12, 0x02, 0x80, 0x36, 0x68, 0x00, 0x00, 0x01, 0x10, 0x50,
        0x34, 0x44, 0xD4, 0xEE, 0x00, 0x34, 0x00, 0x00, 0x00, 0x3C, 0x11, 0x00, 0x00, 0x00,
        0x14, 0x9C, 0x5F, 0x60, 0x26, 0xCB, 0xC0, 0xF2, 0xF7, 0x62
    };

    Frame ubx_frame;
    bool ok = decodeUbx(ubx_data, sizeof(ubx_data), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 0x07);

    auto prn = ublox_qzss_svid_prn_map_lookup(ubx_frame.svid);
    REQUIRE(prn.has_value());
    CHECK(prn.value() == "189");
}

TEST_CASE("UBX: Round-trip svId=1 (suspended, no PRN mapping)") {
    const uint8_t ubx_data[] = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00, 0x05, 0x01, 0x01, 0x00, 0x09, 0x45, 0x02, 0x00,
        0xA1, 0xE5, 0xAD, 0xC6, 0x12, 0x02, 0x80, 0x36, 0x68, 0x00, 0x00, 0x01, 0x10, 0x50,
        0x34, 0x44, 0xD4, 0xEE, 0x00, 0x34, 0x00, 0x00, 0x00, 0x3C, 0x11, 0x00, 0x00, 0x00,
        0x14, 0x9C, 0x5F, 0x60, 0x26, 0xCB, 0xC0, 0xF2, 0xF1, 0x60
    };

    Frame ubx_frame;
    bool ok = decodeUbx(ubx_data, sizeof(ubx_data), ubx_frame);
    REQUIRE(ok);
    CHECK(ubx_frame.svid == 0x01);

    auto prn = ublox_qzss_svid_prn_map_lookup(ubx_frame.svid);
    CHECK_FALSE(prn.has_value());
}

// ── UBX Error Handling Tests ──────────────────────────────────────────────────

TEST_CASE("UBX: Corrupted UBX payload rejected") {
    const uint8_t ubx_data[] = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00, 0x05, 0x02, 0x01, 0x00, 0x09, 0x40, 0x02, 0x00,
        0xC5, 0xF1, 0xAD, 0x9A, 0x04, 0x05, 0x80, 0x11, 0x54, 0x8D, 0xA0, 0x60, 0x3F, 0x82,
        0xD2, 0x11, 0x0F, 0xAA, 0x7D, 0x50, 0x28, 0x0C, 0x43, 0xC9, 0x10, 0x00, 0x50, 0x7D,
        0x31, 0x79, 0xF0, 0x28, 0x73, 0x18, 0x10, 0xB2, 0x62, 0x20  // Corrupted last byte
    };

    Frame ubx_frame;
    bool ok = decodeUbx(ubx_data, sizeof(ubx_data), ubx_frame);
    CHECK_FALSE(ok);
}
