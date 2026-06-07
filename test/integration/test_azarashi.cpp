// test/integration/test_azarashi.cpp — Data-driven tests using real NMEA test vectors
// test_AzaraC.cpp and test_coverage.cpp integrated

#include "../test_helpers.h"
#include "doctest.h"
#include <cstring>
#include <string>

using namespace azaraC;

// ── MT=43 DCR Scenarios ──────────────────────────────────────────────────────

TEST_CASE("DCR: EEW") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 1);
    CHECK(msg.mt43.eew.long_period_lower == 0);
    CHECK(msg.mt43.eew.long_period_upper == 0);
    CHECK(msg.mt43.eew.notification_count == 1);
    CHECK(msg.mt43.eew.notification[0] == 201);
    CHECK(msg.mt43.eew.quake_time.day == 7);
    CHECK(msg.mt43.eew.quake_time.hour == 4);
    CHECK(msg.mt43.eew.quake_time.minute == 0);
    CHECK(msg.mt43.eew.depth == 10);
    CHECK(msg.mt43.eew.magnitude == 72);
    CHECK(msg.mt43.eew.epicenter == 791);
    CHECK(msg.mt43.eew.intensity_lower == 8);
    CHECK(msg.mt43.eew.intensity_upper == 11);
    CHECK(msg.mt43.eew.region_count == 17);
    CHECK(msg.mt43.eew.regions[0] == 37);
    CHECK(msg.mt43.eew.regions[1] == 38);
    CHECK(msg.mt43.eew.regions[2] == 39);
}

TEST_CASE("DCR: Seismic Intensity") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB8000000000000000011E027E5C*76\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 3);
}

TEST_CASE("DCR: Hypocenter") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 2);
}

TEST_CASE("DCR: Tsunami") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5);
}

TEST_CASE("DCR: Tsunami Updated") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C8C8001E8F67C31193960464E621193BBC464EF80000000109DB7028*09\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5);
}

TEST_CASE("DCR: Nankai Trough") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4);
}

TEST_CASE("DCR: Volcano") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 8);
}

TEST_CASE("DCR: Ash Fall") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 9);
}

TEST_CASE("DCR: Weather") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 10);
}

TEST_CASE("DCR: Flood") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11);
}

TEST_CASE("DCR: Flood Warning Cancelled") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB90000E0A8F5528600000000000000000000000000000013A699D5C*76\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11);
}

TEST_CASE("DCR: NW Pacific Tsunami") {
    SUBCASE("Pattern 1") {
        Message msg{};
        const char* nmea = "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C\r\n";
        REQUIRE(decodeNmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6);
    }
    SUBCASE("Pattern 2") {
        Message msg{};
        const char* nmea = "$QZQSM,56,9AAD3609E080023AE008D3D1008E449009D457009E3E5011F00000138B3E720*09\r\n";
        REQUIRE(decodeNmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6);
    }
}

TEST_CASE("DCR: Unknown Magnitude Depth") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.hypo.depth == 511);
    CHECK(msg.mt43.hypo.magnitude == 127);
}

// ── MT=44 DCX Scenarios ──────────────────────────────────────────────────────

TEST_CASE("DCX: J-Alert") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
}

TEST_CASE("DCX: L-Alert") {
    Message msg{};
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
}

TEST_CASE("DCX: Outside Japan - Fiji Tsunami") {
    Message msg{};
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 71);   // Fiji
    CHECK(msg.mt44.camf.a3 == 0);    // Undefined Provider
    CHECK(msg.mt44.camf.a4 == 44);   // GEO/Tsunami
    CHECK(msg.mt44.camf.a5 == 3);    // Extreme severity
    CHECK(msg.mt44.ex_outside.vn == 16); // version 16
}

TEST_CASE("DCX: Null Message") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

TEST_CASE("DCR: Long Period Ground Motion") {
    Message msg{};
    const char* nmea = "$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 1);
    CHECK(msg.mt43.eew.long_period_lower == 3);
    CHECK(msg.mt43.eew.long_period_upper == 3);
}

TEST_CASE("DCR: Nankai page tracking") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4);
    CHECK(msg.mt43.nankai.page == 1);
    CHECK(msg.mt43.nankai.total_page == 27);
    CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
}

TEST_CASE("DCR: Nankai oversized rejected") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA19C918002F1C0C271C0410000000000000000000000000036D81121AA2D0*07\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
}

TEST_CASE("DCR: Ash Fall Sequence") {
    struct TestCase {
        const char* nmea;
    };
    TestCase cases[] = {
        {"$QZQSM,58,C6AFC99CAA0001CAA43EE541F0782A1220813091811183E0F000001329B16E0*7F\r\n"},
        {"$QZQSM,58,C6AFC99CAA0001CAA43EE8C2441046123023307C1E19848820000013E2F3E6C*00\r\n"},
        {"$QZQSM,58,9AAFC99CAA0001CAA43EECC24604860F83C430910421848C080000106286874*00\r\n"},
        {"$QZQSM,58,53AFC99CAA0001CAA43EF4C1F078A61220853091813183E0F0000010CE8C39C*77\r\n"},
        {"$QZQSM,58,C6AFC99CAA0001CAA43EF8C24410C61230200000000000000000001148565F4*0A\r\n"},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decodeNmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 9);
    }
}

TEST_CASE("DCR: Weather Multiple") {
    struct TestCase {
        const char* nmea;
        uint8_t expected_dc;
    };
    TestCase cases[] = {
        {"$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73\r\n", 10},
        {"$QZQSM,58,9AAFD19CB180011222E0B93880B95F90B986A0B9ADB0B9D4C0000013D276B60*0D\r\n", 10},
        {"$QZQSM,58,53AFD19CB18001B9FBD0BA22E00000000000000000000000000000107AA71EC*76\r\n", 10},
        {"$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E\r\n", 11},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decodeNmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == cases[i].expected_dc);
    }
}

// ── Error Handling ────────────────────────────────────────────────────────────

TEST_CASE("Error: CRC Mismatch") {
    Message msg{};
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C000011854432D*34\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

TEST_CASE("Error: NMEA Checksum Mismatch") {
    Message msg{};
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

TEST_CASE("Error: Unknown Disaster Category") {
    Message msg{};
    internal::Frame frame;
    frame.svid = 55;
    frame.source = internal::FrameSource::NMEA;

    memset(frame.bits, 0, 32);
    setBits(frame.bits, 0, 8, 0x53);
    setBits(frame.bits, 8, 6, 43);
    setBits(frame.bits, 17, 4, 7);
    setBits(frame.bits, 214, 6, 1);

    uint32_t crc = crc24qRef(frame.bits, 226);
    setBits(frame.bits, 226, 24, crc);

    internal::Decoder dec;
    bool ok = dec.decode(frame, msg, 0);
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

// ── Edge Cases ───────────────────────────────────────────────────────────────

TEST_CASE("Edge: Invalid MT=42") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 42);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Invalid MT=45") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 45);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Version 0 rejected") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 0);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Version 2 rejected") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 2);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Invalid preamble 0x00") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x00);
    setBits(bits, 8, 6, 43);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Valid preamble 0x53") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Valid preamble 0x9A") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x9A);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: Valid preamble 0xC6") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0xC6);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge: NMEA 63 char accepted") {
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\r\n";
    const char* payload_start = nmea + 10;
    size_t payload_len = 0;
    while (payload_start[payload_len] != '*') payload_len++;
    CHECK(payload_len == 63);

    Message msg{};
    bool ok = decodeNmea(nmea, msg);
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
}

TEST_CASE("Edge: Tsunami invalid arrival time") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 5);
    setBits(bits, 214, 6, 1);

    setBits(bits, 21, 4, 4);
    setBits(bits, 25, 5, 25);
    setBits(bits, 30, 5, 13);
    setBits(bits, 35, 6, 0);

    setBits(bits, 80, 4, 3);

    setBits(bits, 84, 10, 1);
    setBits(bits, 94, 4, 2);
    setBits(bits, 98, 12, (0u << 11) | (31u << 6) | 63u);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    TestDecoder::testDecodeTsunami(bits, msg, 1777122000u);

    CHECK(msg.mt43.tsunami.count >= 1);
    if (msg.mt43.tsunami.count >= 1) {
        CHECK(msg.mt43.tsunami.entries[0].arrival_time.hour == 0);
        CHECK(msg.mt43.tsunami.entries[0].arrival_time.minute == 0);
        CHECK(msg.mt43.tsunami.entries[0].arrival_time.unix_time == 0);
    }
}

TEST_CASE("Edge: Leap year Feb 29") {
    uint32_t now = 1709164800u;
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    setBits(bits, 21, 4, 2);
    setBits(bits, 25, 5, 29);
    setBits(bits, 30, 5, 0);
    setBits(bits, 35, 6, 0);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, now));
    CHECK(msg.mt43.event_time.day == 29);
}

TEST_CASE("Edge: Year end transition") {
    uint32_t now = 1735686000u;
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    setBits(bits, 21, 4, 12);
    setBits(bits, 25, 5, 31);
    setBits(bits, 30, 5, 23);
    setBits(bits, 35, 6, 0);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, now));
    CHECK(msg.mt43.event_time.day == 31);
}

TEST_CASE("Edge: Depth 501+") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 2);
    setBits(bits, 214, 6, 1);
    setBits(bits, 96, 9, 501);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo.depth == 501);
}

TEST_CASE("Edge: Depth 511 unknown") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 2);
    setBits(bits, 214, 6, 1);
    setBits(bits, 96, 9, 511);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo.depth == 511);
}

TEST_CASE("Edge: Magnitude 126") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 2);
    setBits(bits, 214, 6, 1);
    setBits(bits, 105, 7, 126);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo.magnitude == 126);
}

TEST_CASE("Edge: Magnitude 127 unknown") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 2);
    setBits(bits, 214, 6, 1);
    setBits(bits, 105, 7, 127);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo.magnitude == 127);
}

TEST_CASE("Error: Invalid CRC") {
    uint8_t bits[32] = {};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 14, 3, 1);
    setBits(bits, 17, 4, 1);
    setBits(bits, 41, 2, 0);
    setBits(bits, 214, 6, 1);
    setBits(bits, 226, 24, 0xEADBEE);

    Frame frame{};
    memcpy(frame.bits, bits, 32);
    frame.svid = 193;
    Decoder dec;
    Message msg{};
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Error: Invalid NMEA checksum") {
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*00";
    Message msg{};
    CHECK_FALSE(decodeNmea(nmea, msg));
}

TEST_CASE("Error: Invalid MT=99") {
    uint8_t bits[32] = {};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 99);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    Frame frame{};
    memcpy(frame.bits, bits, 32);
    frame.svid = 193;
    Decoder dec;
    Message msg{};
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Error: Invalid preamble 0xFF") {
    uint8_t bits[32] = {};
    setBits(bits, 0, 8, 0xFF);
    setBits(bits, 8, 6, 43);
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    Frame frame{};
    memcpy(frame.bits, bits, 32);
    frame.svid = 193;
    Decoder dec;
    Message msg{};
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Error: Short NMEA payload") {
    const char* nmea = "$QZQSM,58,9AAF899C*7F";
    NmeaFramer framer;
    Frame frame;
    bool decoded = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            decoded = true;
            break;
        }
    }
    CHECK_FALSE(decoded);
}
