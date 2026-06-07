// test/framer/test_ublox_azarashi.cpp
// UBX SFRBX の azarashi 比較テスト
// azarashi v0.16.1 のデコード結果と照合

#define ARDUINO 0
#include "../test_helpers.h"
#include "doctest.h"
#include <cstring>
#include <vector>

using namespace azaraC;

// ═══════════════════════════════════════════════════════════════════════════════
// UBX SFRBX 5パターン — test_ublox (azarashi)
// azarashi でデコードした結果: NMEA ラウンドトリップ + フィールド検証
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("UBX: SFRBX sv56 pattern1 - Marine (round-trip with NMEA)") {
    // azarashi ublox_sv56_p1: svid=2, Marine, Regular, 8 regions
    // UBXヘッダー: gnssId=5(QZSS), svId=2, sigId=0, freqId=0, numWords=8, chn=0, version=1
    std::vector<uint8_t> ubx_data = {
        0xB5, 0x62, 0x02, 0x13, 0x2C, 0x00,
        0x05, 0x02, 0x01, 0x00, 0x09, 0x40, 0x02, 0x00,
        0xC5, 0xF1, 0xAD, 0x9A, 0x04, 0x05, 0x80, 0x11,
        0x54, 0x8D, 0xA0, 0x60, 0x3F, 0x82, 0xD2, 0x11,
        0x0F, 0xAA, 0x7D, 0x50, 0x28, 0x0C, 0x43, 0xC9,
        0x10, 0x00, 0x50, 0x7D, 0x31, 0x79, 0xF0, 0x28,
        0x73, 0x18, 0x10, 0xB2, 0x62, 0x2F
    };

    UbxFramer framer;
    Frame frame;
    bool found = false;
    for (auto b : ubx_data) {
        if (framer.feed(b, frame)) { found = true; break; }
    }
    REQUIRE(found);
    CHECK(frame.svid == 2);  // UBXヘッダーのsvIdフィールド

    // NMEA に変換してデコード
    std::string nmea = makeNmeaQzqsm(frame.svid, frame.bits);
    Message msg{};
    REQUIRE(decodeNmea(nmea.c_str(), msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 14); // Marine
}

TEST_CASE("UBX: SFRBX sv56 pattern2 - Hypocenter (round-trip with NMEA)") {
    // azarashi ublox_sv56_p2: Hypocenter, Priority
    // NMEA: $QZQSM,56,53AD14761A80035C0000EC33142F484952011B200000000000000012C6B0598*7C
    const char* nmea = "$QZQSM,56,53AD14761A80035C0000EC33142F484952011B200000000000000012C6B0598*7C";
    Message msg{};
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 2); // Hypocenter
}

TEST_CASE("UBX: SFRBX sv57 - Typhoon (round-trip with NMEA)") {
    // azarashi ublox_sv57: Typhoon, Regular
    // NMEA: $QZQSM,57,C6ADE5A13680021201000068443450103400EED43C00000000000011605F9C0*0E
    const char* nmea = "$QZQSM,57,C6ADE5A13680021201000068443450103400EED43C00000000000011605F9C0*0E";
    Message msg{};
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 12); // Typhoon
}

TEST_CASE("UBX: SFRBX sv61 - Typhoon (round-trip with NMEA)") {
    // azarashi ublox_sv61: Typhoon, Regular (same content, different svid)
    const char* nmea = "$QZQSM,61,C6ADE5A13680021201000068443450103400EED43C00000000000011605F9C0*0B";
    Message msg{};
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 12); // Typhoon
}

TEST_CASE("UBX: SFRBX sv55 - Typhoon (round-trip with NMEA)") {
    // azarashi ublox_sv55: Typhoon, Regular (svid:1 -> PRN183)
    const char* nmea = "$QZQSM,55,C6ADE5A13680021201000068443450103400EED43C00000000000011605F9C0*0C";
    Message msg{};
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 12); // Typhoon
}
