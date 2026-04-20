
// test/test_crc.cpp — CRC-24Q verification
// Build: g++ -std=c++17 -I../src -I../src/internal test_crc.cpp -o test_crc && ./test_crc

#define ARDUINO 0
#include "../src/internal/Decoder.h"
#include "../src/internal/PrintShim.h"
#include <cstdio>
#include <cstring>
#include <cassert>

using namespace azaraC;
using namespace azaraC::internal;

// ── CRC-24Q reference impl (cross-check) ────────────────────────────────────
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

// Expose private crc24q via subclass
struct TestDecoder : Decoder {
    static uint32_t crc(const uint8_t* d, uint16_t bits) {
        return crc24q(d, bits);
    }
    static uint32_t bits(const uint8_t* b, uint16_t s, uint8_t l) {
        return getBits(b, s, l);
    }
};

// ── helpers ─────────────────────────────────────────────────────────────────
static void pass(const char* name) { printf("  PASS  %s\n", name); }
static void fail(const char* name, const char* why) {
    printf("  FAIL  %s : %s\n", name, why);
    assert(false);
}

// ── test: CRC vs reference ───────────────────────────────────────────────────
static void test_crc_known() {
    // All-zero 226-bit buffer → both impls must agree
    uint8_t buf[29] = {};
    uint32_t a = TestDecoder::crc(buf, 226);
    uint32_t b = crc24q_ref(buf, 226);
    if (a != b) fail("crc_known_zeros", "mismatch vs reference");
    pass("crc_known_zeros");

    // Random pattern
    for (auto& v : buf) v = 0xA5;
    a = TestDecoder::crc(buf, 226);
    b = crc24q_ref(buf, 226);
    if (a != b) fail("crc_known_a5", "mismatch vs reference");
    pass("crc_known_a5");
}

// ── test: getBits ─────────────────────────────────────────────────────────────
static void test_getbits() {
    // buf = 0xAB 0xCD = 1010 1011 1100 1101
    uint8_t buf[2] = {0xAB, 0xCD};

    auto chk = [&](uint16_t s, uint8_t l, uint32_t expected, const char* name) {
        uint32_t got = TestDecoder::bits(buf, s, l);
        if (got != expected) {
            printf("    got=0x%X expected=0x%X\n", got, expected);
            fail(name, "value mismatch");
        }
        pass(name);
    };

    chk(0,  8, 0xAB,  "getBits_byte0");
    chk(8,  8, 0xCD,  "getBits_byte1");
    chk(0,  4, 0xA,   "getBits_nib0");
    chk(4,  4, 0xB,   "getBits_nib1");
    chk(0,  1, 1,     "getBits_msb");
    chk(7,  1, 1,     "getBits_lsb0");
    chk(8,  1, 1,     "getBits_bit8");
    chk(0, 16, 0xABCD,"getBits_word");
}

// ── test: invalid preamble rejected ─────────────────────────────────────────
static void test_bad_preamble() {
    uint8_t buf[32] = {};
    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    // preamble = 0x00, crc will fail → returns false
    bool ok = dec.decode(f, msg);
    if (ok) fail("bad_preamble", "should reject");
    pass("bad_preamble");
}

// ── test: MT=44 field extraction on synthetic frame ──────────────────────────
static void test_mt44_synthetic() {
    // Build a minimal MT=44 frame:
    //   preamble[0..7]  = 0x53
    //   msg_type[8..13] = 44 = 0b101100
    //   dcx_type[14..16]= 1 (L_ALERT) = 0b001
    //   a1[17..20]      = 2 = 0b0010
    //   a2[21..30]      = 111 (Japan) = 0b0001101111
    // then append correct CRC-24Q at [226..249]
    uint8_t buf[32] = {};
    auto setbits = [&](uint16_t s, uint8_t l, uint32_t v) {
        for (int i = l-1; i >= 0; --i) {
            uint16_t pos = s + (l-1-i);
            if ((v >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    };

    setbits(0,  8, 0x53);  // preamble
    setbits(8,  6, 44);    // msg_type
    setbits(14, 3, 1);     // dcx_type = L_ALERT
    setbits(17, 4, 2);     // a1 = 2
    setbits(21,10, 111);   // a2 = Japan

    uint32_t crc = crc24q_ref(buf, 226);
    setbits(226, 24, crc);

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg);
    if (!ok) fail("mt44_synthetic", "decode returned false");
    if (msg.msg_type != 44) fail("mt44_synthetic", "msg_type != 44");
    if (msg.dcx_type != DcxType::L_ALERT) fail("mt44_synthetic", "dcx_type != L_ALERT");
    if (msg.a1_message_type != 2)  fail("mt44_synthetic", "a1 != 2");
    if (msg.a2_country_code != 111) fail("mt44_synthetic", "a2 != 111");
    pass("mt44_synthetic");
}

// ── main ─────────────────────────────────────────────────────────────────────
int main() {
    printf("=== azaraC unit tests ===\n");
    test_crc_known();
    test_getbits();
    test_bad_preamble();
    test_mt44_synthetic();
    printf("=== all passed ===\n");
    return 0;
}
