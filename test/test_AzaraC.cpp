// test/test_AzaraC.cpp — Data-driven tests using real NMEA test vectors
// 統合テスト: NMEAフレーマー → デコーダーの一連の流れを検証

#include "test_helpers.h"
#include "doctest.h"
#include <cstring>
#include <string>

using namespace azaraC;

// ── MT=43 DCR Scenarios ──────────────────────────────────────────────────────

TEST_CASE("DCR: EEW (Earthquake Early Warning)") {
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
    CHECK(msg.mt43.eew.magnitude == 72);  // 7.2
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

TEST_CASE("DCR: Tsunami (Updated)") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C8C8001E8F67C31193960464E621193BBC464EF80000000109DB7028*09\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5);
}

TEST_CASE("DCR: Nankai Trough Earthquake") {
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

TEST_CASE("DCR: Flood (Warning Cancelled)") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB90000E0A8F5528600000000000000000000000000000013A699D5C*76\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11);
}

TEST_CASE("DCR: Northwest Pacific Tsunami") {
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

TEST_CASE("DCR: Unknown Magnitude/Depth") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.hypo.depth == 511);
    CHECK(msg.mt43.hypo.magnitude == 127);
}

// ── MT=44 DCX Scenarios ──────────────────────────────────────────────────────

TEST_CASE("DCX: J-Alert (via A3=2, FDMA)") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
}

TEST_CASE("DCX: L-Alert (via A3=1, FMMC)") {
    Message msg{};
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
}

TEST_CASE("DCX: Outside Japan") {
    Message msg{};
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
}

// ── Error Handling ────────────────────────────────────────────────────────────

TEST_CASE("DCR: CRC Mismatch Rejection") {
    Message msg{};
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C000011854432D*34\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

TEST_CASE("DCR: NMEA Checksum Mismatch Rejection") {
    Message msg{};
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

TEST_CASE("DCR: Unknown Disaster Category Rejection") {
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

// ── DCX Null Message ──────────────────────────────────────────────────────────

TEST_CASE("DCX: Null Message") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

// ── Long Period Ground Motion ─────────────────────────────────────────────────

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

// ── Nankai Trough Sequence ────────────────────────────────────────────────────

TEST_CASE("DCR: Nankai Trough - page/total_page tracking") {
    Message msg{};
    // このフレームは page=1, total_page=27 であることを確認する
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4);
    CHECK(msg.mt43.nankai.page == 1);
    CHECK(msg.mt43.nankai.total_page == 27);
    CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
}

TEST_CASE("DCR: Nankai Trough - full sequence") {
    // フレームごとの期待 page 値 (total_page は全て 27)
    // page はビット201から6ビットでデコードされる
    struct NankaiFrame {
        const char* nmea;
        uint8_t expected_page;
    };
    NankaiFrame frames[] = {
        {"$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n",  1},
        {"$QZQSM,58,9AAFA19C918002F1C0D471C0D1F1C0D371C0C7F1C0D071C0CAB4D812D45BCD0*06\r\n", 26},
        {"$QZQSM,58,9AAFA19C918002F1C0CFF4CC5973C0DEF2D7DF72DFCE71C14932D813A64867C*0C\r\n", 25},
        {"$QZQSM,58,53AFA19C918002F1C0C5F1C0C8F3D6C4F1C0D5F2DFCE71C0CC30D81029188EC*0F\r\n", 24},
        {"$QZQSM,58,C6AFA19C918002F1C0D4F1C0C5F1C144F1C0D772C8DE71C0D9AED8108F361A8*7A\r\n", 23},
        {"$QZQSM,58,9AAFA19C918002F2DD4E71C1427443D573595DF25EC9F1C0D52CD81113EFC54*00\r\n", 22},
        {"$QZQSM,58,9AAFA19C918002F1C0CCF1C041725DC572DF4671C0D7734A5FAAD811D504B9C*09\r\n", 21},
        {"$QZQSM,58,53AFA19C918002F1C0D4744041F1C0C471C144F1C14671C0DF28D8127EDCCCC*02\r\n", 20},
        {"$QZQSM,58,C6AFA19C918002F4D5CC71C0DF71C0D1F1C0D371C0C271C145A6D812E9F0C70*03\r\n", 19},
        {"$QZQSM,58,9AAFA19C918002F1C0DCF1C0D373CDDC72D7DF73CD4271C0D5A4D813579A170*78\r\n", 18},
        {"$QZQSM,58,9AAFA19C918002F1C0C672DCD9F2DC5C734CC171C0D5F357CA22D8100D3A898*07\r\n", 17},
        {"$QZQSM,58,53AFA19C918002F1C0D773CCDD73CA4FF2C7D7F441DEF34053A0D8108524298*01\r\n", 16},
        {"$QZQSM,58,C6AFA19C918002F1C040F2D253F45347F35450F2CE5874CE439ED8113990640*7D\r\n", 15},
        {"$QZQSM,58,9AAFA19C918002F2D74D74CE43F35D4872CFCFF1C0D3F1C0D79CD8118D63AC8*07\r\n", 14},
        {"$QZQSM,58,9AAFA19C918002F1C1D4F1C1CAF2CE5874CE43F1C0D77341D99AD81268C2E7C*73\r\n", 13},
        {"$QZQSM,58,53AFA19C918002F1C14471C14571C040F2C6CBF35ADBF1C1C418D812DC94FA0*7F\r\n", 12},
        {"$QZQSM,58,C6AFA19C918002F1C0DCF1C14571C0D773CCDD73CA4FF1C0D596D81357F75D0*74\r\n", 11},
        {"$QZQSM,58,9AAFA19C918002F1C145F1C14371C0D1F1C0C7F1C14571C0CC94D813ED6741C*0C\r\n", 10},
        {"$QZQSM,58,9AAFA19C918002F4C04D72DC5C71C0D471C0D7F3CAD871C0D512D810ADB00F0*78\r\n",  9},
        {"$QZQSM,58,9AAFA19C918002F1C0C271C0D771C1CBF1C1D671C1DE71C1C404D8104D300D8*7F\r\n",  2},
    };

    for (size_t i = 0; i < sizeof(frames)/sizeof(frames[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decodeNmea(frames[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 4);
        CHECK(msg.mt43.nankai.total_page == 27);
        CHECK(msg.mt43.nankai.page == frames[i].expected_page);
        CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
    }
}

TEST_CASE("DCR: Nankai Trough - oversized message rejected") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA19C918002F1C0C271C0410000000000000000000000000036D81121AA2D0*07\r\n";
    bool ok = decodeNmea(nmea, msg);
    CHECK_FALSE(ok);
}

// ── Ash Fall Sequence ─────────────────────────────────────────────────────────

TEST_CASE("DCR: Ash Fall - Sequence") {
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

// ── Weather Multi ─────────────────────────────────────────────────────────────

TEST_CASE("DCR: Weather - Multiple Messages") {
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
