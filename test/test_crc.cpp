// test/test_crc.cpp — CRC-24Q verification
#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

TEST_CASE("CRC-24Q vs reference") {
    // All-zero 226-bit buffer → both impls must agree
    uint8_t buf[29] = {};
    uint32_t a = TestDecoder::calcCRC(buf, 226);
    uint32_t b = crc24qRef(buf, 226);
    CHECK(a == b);

    // Random pattern
    for (auto& v : buf) v = 0xA5;
    a = TestDecoder::calcCRC(buf, 226);
    b = crc24qRef(buf, 226);
    CHECK(a == b);
}

TEST_CASE("getBits extraction") {
    // buf = 0xAB 0xCD = 1010 1011 1100 1101
    uint8_t buf[2] = {0xAB, 0xCD};

    CHECK(TestDecoder::extractBits(buf, 0,  8) == 0xAB);
    CHECK(TestDecoder::extractBits(buf, 8,  8) == 0xCD);
    CHECK(TestDecoder::extractBits(buf, 0,  4) == 0xA);
    CHECK(TestDecoder::extractBits(buf, 4,  4) == 0xB);
    CHECK(TestDecoder::extractBits(buf, 0,  1) == 1);
    CHECK(TestDecoder::extractBits(buf, 7,  1) == 1);
    CHECK(TestDecoder::extractBits(buf, 8,  1) == 1);
    CHECK(TestDecoder::extractBits(buf, 0, 16) == 0xABCD);
}

TEST_CASE("invalid preamble rejected") {
    uint8_t buf[32] = {};
    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    // preamble = 0x00, crc will fail → returns false
    bool ok = dec.decode(f, msg);
    CHECK(ok == false);
}

TEST_CASE("MT=44 field extraction on synthetic frame") {
    // Build a minimal MT=44 frame matching IS-QZSS-DCX-003 bit layout:
    //   preamble[0..7]     = 0x53
    //   msg_type[8..13]    = 44 = 0b101100
    //   SD[14..23]         = SDMT=0, SDM=0
    //   CAMF.A1[24..25]    = 1 (Alert)
    //   CAMF.A2[26..34]    = 0x6F (111 = Japan = 001101111)
    //   CAMF.A3[35..39]    = 2 (FDMA = J-Alert)
    // then append correct CRC-24Q at [226..249]
    uint8_t buf[32] = {};

    setBits(buf, 0,  8, 0x53);  // preamble
    setBits(buf, 8,  6, 44);    // msg_type
    // SD: SDMT=0, SDM=0 (no explicit set needed, buf is zeroed)
    setBits(buf, 24, 2, 1);     // CAMF.A1 = 1 (Alert)
    setBits(buf, 26, 9, 111);   // CAMF.A2 = 111 (Japan)
    setBits(buf, 35, 5, 2);     // CAMF.A3 = 2 (FDMA → J-Alert)

    uint32_t crc = crc24qRef(buf, 226);
    setBits(buf, 226, 24, crc);

    Frame f; f.svid = 193; memcpy(f.bits, buf, 32);
    Decoder dec;
    Message msg{};
    bool ok = dec.decode(f, msg);
    REQUIRE(ok);
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.camf.a1 == 1);
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 2);
}
