
// test/test_framer.cpp — Framer verification (UBX/NMEA)
// Build: g++ -std=c++17 -I../src -I../src/internal test_framer.cpp ../src/internal/UbxFramer.cpp ../src/internal/NmeaFramer.cpp -o test_framer && ./test_framer

#define ARDUINO 0
#include "../src/internal/UbxFramer.h"
#include "../src/internal/NmeaFramer.h"
#include "doctest.h"
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>

using namespace azaraC;
using namespace azaraC::internal;


// ── UBX SFRBX Generator ──────────────────────────────────────────────────────
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

// ── NMEA QZQSM Generator ─────────────────────────────────────────────────────
static std::string make_nmea_qzqsm(uint8_t svid, const uint8_t* nav_bits) {
    char buf[256];
    sprintf(buf, "QZQSM,%d,", svid);
    std::string s = "$";
    s += buf;
    for (int i = 0; i < 32; ++i) {
        char hex[3];
        sprintf(hex, "%02X", nav_bits[i]);
        s += hex;
    }
    
    uint8_t xsum = 0;
    for (size_t i = 1; i < s.size(); ++i) {
        xsum ^= (uint8_t)s[i];
    }
    
    char tail[5];
    sprintf(tail, "*%02X\r\n", xsum);
    s += tail;
    return s;
}

// ── UBX Tests ───────────────────────────────────────────────────────────────
TEST_CASE("UBX Framer Basic") {
    uint8_t bits[32] = {0x53, 0xAB}; // dummy data
    auto pkt = make_ubx_sfrbx(193, bits);
    
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
    auto pkt = make_ubx_sfrbx(193, bits);
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
    auto pkt = make_ubx_sfrbx(194, bits);

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

// ── NMEA Tests ──────────────────────────────────────────────────────────────
TEST_CASE("NMEA Framer Basic") {
    uint8_t bits[32];
    for(int i=0; i<32; ++i) bits[i] = i;
    auto pkt = make_nmea_qzqsm(193, bits);

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
    auto pkt = make_nmea_qzqsm(193, bits);
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
    auto pkt = make_nmea_qzqsm(195, bits);

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
    auto pkt = make_nmea_qzqsm(199, bits);
    bool found = false;
    for (char c : pkt) {
        if (framer.feed((uint8_t)c, out)) { found = true; break; }
    }
    CHECK(found);
}
