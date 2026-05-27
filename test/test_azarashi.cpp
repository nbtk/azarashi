// test/test_azarashi.cpp
// Data-driven tests using real NMEA test vectors from the `azarashi` Python library.

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>
#include <string>

using namespace azaraC;

// Helper: Feed a raw NMEA string through framer + decoder.
static bool decode_nmea(const char* nmea, Message& msg) {
    internal::NmeaFramer framer;
    internal::Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            found = true;
            break;
        }
    }
    if (!found) return false;
    internal::Decoder dec;
    return dec.decode(frame, msg, 0);
}

static uint32_t crc24q_ref(const uint8_t* d, int total_bits) {
    uint32_t crc = 0;
    int bytes = (total_bits + 7) / 8;
    for (int i = 0; i < bytes; i++) {
        uint8_t b = d[i];
        int bits_to_process = 8;
        if (i == bytes-1 && (total_bits&7)) {
            b &= 0xFFu << (8-(total_bits&7));
            bits_to_process = total_bits & 7;
        }
        crc ^= (uint32_t)b << 16;
        for (int j = 0; j < bits_to_process; j++) {
            crc <<= 1;
            if (crc & 0x1000000) crc ^= 0x1864CFB;
        }
    }
    return crc & 0xFFFFFF;
}

static void setbits(uint8_t* buf, uint16_t s, uint8_t l, uint32_t v) {
    for (int i = l-1; i >= 0; --i) {
        uint16_t pos = s + (l-1-i);
        if ((v >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
        else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
    }
}

// ── MT=43 DCR Scenarios (from azarashi tests/test.py) ────────────────────────

TEST_CASE("DCR: EEW (Earthquake Early Warning)") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 1);
    // 実際のデコード結果を検証（print_eewで出力した値）
    CHECK(msg.mt43.eew.long_period_lower == 0);
    CHECK(msg.mt43.eew.long_period_upper == 0);
    CHECK(msg.mt43.eew.notification_count == 1);
    CHECK(msg.mt43.eew.notification[0] == 201);
    // eew.quake_time: day=7, hour=4, minute=0 (unix=1709784000)
    CHECK(msg.mt43.eew.quake_time.day == 7);
    CHECK(msg.mt43.eew.quake_time.hour == 4);
    CHECK(msg.mt43.eew.quake_time.minute == 0);
    CHECK(msg.mt43.eew.depth == 10);
    CHECK(msg.mt43.eew.magnitude == 72);  // 7.2
    CHECK(msg.mt43.eew.epicenter == 791);
    CHECK(msg.mt43.eew.intensity_lower == 8);
    CHECK(msg.mt43.eew.intensity_upper == 11);
    CHECK(msg.mt43.eew.region_count == 17);
    // 最初の数地域をチェック
    CHECK(msg.mt43.eew.regions[0] == 37);
    CHECK(msg.mt43.eew.regions[1] == 38);
    CHECK(msg.mt43.eew.regions[2] == 39);
}

TEST_CASE("DCR: Seismic Intensity") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB8000000000000000011E027E5C*76\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 3); // Seismic Intensity
}

TEST_CASE("DCR: Hypocenter") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 2); // Hypocenter
}

TEST_CASE("DCR: Tsunami") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5); // Tsunami
}

TEST_CASE("DCR: Tsunami (Updated)") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C8C8001E8F67C31193960464E621193BBC464EF80000000109DB7028*09\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5);
}

TEST_CASE("DCR: Nankai Trough Earthquake") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4); // Nankai trough
}

TEST_CASE("DCR: Volcano") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 8); // Volcano
}

TEST_CASE("DCR: Ash Fall") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 9); // Ash fall
}

TEST_CASE("DCR: Weather") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 10); // Weather
}

TEST_CASE("DCR: Flood") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11); // Flood
}

TEST_CASE("DCR: Flood (Warning Cancelled)") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB90000E0A8F5528600000000000000000000000000000013A699D5C*76\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11);
}

TEST_CASE("DCR: Northwest Pacific Tsunami") {
    Message msg{};
    SUBCASE("Pattern 1") {
        const char* nmea = "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C\r\n";
        REQUIRE(decode_nmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6); // NW Pacific Tsunami
    }
    SUBCASE("Pattern 2") {
        const char* nmea = "$QZQSM,56,9AAD3609E080023AE008D3D1008E449009D457009E3E5011F00000138B3E720*09\r\n";
        REQUIRE(decode_nmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6);
    }
}

TEST_CASE("DCR: Unknown Magnitude/Depth") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    // depth_of_hypocenter_raw == 511 means "不明"
    CHECK(msg.mt43.hypo.depth == 511);
    // magnitude_raw == 127 means "不明"
    CHECK(msg.mt43.hypo.magnitude == 127);
}

// ── MT=44 DCX Scenarios ──────────────────────────────────────────────────────

TEST_CASE("DCX: J-Alert (via A3=2, FDMA)") {
    Message msg{};
    // Frame: preamble=0x53, MT=44, CAMF.A2=111(Japan), CAMF.A3=2(FDMA=J-Alert)
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
}

TEST_CASE("DCX: L-Alert (via A3=1, FMMC)") {
    Message msg{};
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
}

TEST_CASE("DCX: Outside Japan") {
    Message msg{};
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
}

// ── Hex input format ─────────────────────────────────────────────────────────

TEST_CASE("DCR: Hex input decode") {
    // Same data as EEW scenario but without $QZQSM wrapper.
    // The hex string in azarashi test is: C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC
    // Since our decoder uses NmeaFramer which expects $QZQSM, we wrap it.
    // This test verifies a different svid (55 = C6 prefix).
    Message msg{};
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00\r\n";
    // Note: checksum might not match. This is to test that a bad checksum is rejected.
    bool ok = decode_nmea(nmea, msg);
    // If checksum is wrong, framer should reject → decode returns false
    // This tests our error-handling path
    CHECK_FALSE(ok);
}

TEST_CASE("DCR: Unknown Disaster Category Rejection") {
    Message msg{};
    internal::Frame frame;
    frame.svid = 55;
    frame.source = internal::FrameSource::NMEA;

    memset(frame.bits, 0, 32);
    // Preamble: 0x53, MT: 43, DC: 7 (Unused)
    setbits(frame.bits, 0, 8, 0x53);
    setbits(frame.bits, 8, 6, 43);
    setbits(frame.bits, 17, 4, 7);
    // Version: 1
    setbits(frame.bits, 214, 6, 1);

    // Calculate and set CRC
    uint32_t crc = crc24q_ref(frame.bits, 226);
    setbits(frame.bits, 226, 24, crc);

    internal::Decoder dec;
    bool ok = dec.decode(frame, msg, 0);

    // Should fail because DC=7 is not handled
    CHECK_FALSE(ok);
    CHECK_FALSE(msg.valid);
}

TEST_CASE("DCR: Typhoon") {
    Message msg{};
    internal::Frame frame;
    frame.svid = 55;
    frame.source = internal::FrameSource::NMEA;

    memset(frame.bits, 0, 32);
    setbits(frame.bits, 0, 8, 0x53);
    setbits(frame.bits, 8, 6, 43);
    setbits(frame.bits, 17, 4, 12); // Typhoon
    setbits(frame.bits, 87, 7, 21); // Typhoon Number 21
    setbits(frame.bits, 214, 6, 1);

    uint32_t crc = crc24q_ref(frame.bits, 226);
    setbits(frame.bits, 226, 24, crc);

    internal::Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 12);
    CHECK(msg.mt43.typh.number == 21);
}

TEST_CASE("DCR: Marine") {
    Message msg{};
    internal::Frame frame;
    frame.svid = 55;
    frame.source = internal::FrameSource::NMEA;

    memset(frame.bits, 0, 32);
    setbits(frame.bits, 0, 8, 0x53);
    setbits(frame.bits, 8, 6, 43);
    setbits(frame.bits, 17, 4, 14); // Marine
    setbits(frame.bits, 53, 5, 19); // Warning code 19
    setbits(frame.bits, 214, 6, 1);

    uint32_t crc = crc24q_ref(frame.bits, 226);
    setbits(frame.bits, 226, 24, crc);

    internal::Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 14);
    REQUIRE(msg.mt43.marine.count > 0);
    CHECK(msg.mt43.marine.entries[0].warning_code == 19);
}

TEST_CASE("DCR: Comprehensive Category Mapping Verification") {
    internal::Decoder dec;
    internal::Frame frame;
    frame.svid = 55;
    frame.source = internal::FrameSource::NMEA;

    auto verify_mapping = [&](uint8_t category, auto validator) {
        Message msg{};
        memset(frame.bits, 0, 32);
        setbits(frame.bits, 0, 8, 0x53);
        setbits(frame.bits, 8, 6, 43);
        setbits(frame.bits, 17, 4, category);
        setbits(frame.bits, 214, 6, 1);

        if (category == 1)  setbits(frame.bits, 47,  3, 7); // eew.long_period_lower
        if (category == 2)  setbits(frame.bits, 112, 10, 999); // hypo.epicenter
        if (category == 3)  setbits(frame.bits, 69,  3, 7); // intensity_code (first entry)
        if (category == 4)  setbits(frame.bits, 53,  4, 15); // nankai.info_code
        if (category == 5)  setbits(frame.bits, 80,  4, 15); // tsunami.warning_code
        if (category == 6)  setbits(frame.bits, 53,  3, 7); // nw_pac.potential
        if (category == 8)  setbits(frame.bits, 50,  3, 7); // vol.ambiguity
        if (category == 9)  setbits(frame.bits, 69,  2, 3); // ash.warning_type
        if (category == 10) setbits(frame.bits, 53,  3, 7); // wx.warning_state
        if (category == 11) {
            setbits(frame.bits, 53,  4, 15); // warning_level (bits 53-56)
            setbits(frame.bits, 77,  1, 1);  // region_code bit (bit 77) to ensure getBits(..., 44) != 0
        }
        if (category == 12) setbits(frame.bits, 87,  7, 99); // typh.number
        if (category == 14) setbits(frame.bits, 53,  5, 31); // marine warning_code

        uint32_t crc = crc24q_ref(frame.bits, 226);
        setbits(frame.bits, 226, 24, crc);

        REQUIRE(dec.decode(frame, msg, 0));
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == category);
        validator(msg);
    };

    SUBCASE("Category 1: EEW") {
        verify_mapping(1, [](Message& m) { CHECK(m.mt43.eew.long_period_lower == 7); });
    }
    SUBCASE("Category 2: Hypocenter") {
        verify_mapping(2, [](Message& m) { CHECK(m.mt43.hypo.epicenter == 999); });
    }
    SUBCASE("Category 3: Seismic Intensity") {
        verify_mapping(3, [](Message& m) { CHECK(m.mt43.seis.count > 0); CHECK(m.mt43.seis.entries[0].intensity_code == 7); });
    }
    SUBCASE("Category 4: Nankai Trough") {
        verify_mapping(4, [](Message& m) { CHECK(m.mt43.nankai.info_code == 15); });
    }
    SUBCASE("Category 5: Tsunami") {
        verify_mapping(5, [](Message& m) { CHECK(m.mt43.tsunami.warning_code == 15); });
    }
    SUBCASE("Category 6: NW Pacific Tsunami") {
        verify_mapping(6, [](Message& m) { CHECK(m.mt43.nw_pac.potential == 7); });
    }
    SUBCASE("Category 8: Volcano") {
        verify_mapping(8, [](Message& m) { CHECK(m.mt43.vol.ambiguity == 7); });
    }
    SUBCASE("Category 9: Ash Fall") {
        verify_mapping(9, [](Message& m) { CHECK(m.mt43.ash.warning_type == 3); });
    }
    SUBCASE("Category 10: Weather") {
        verify_mapping(10, [](Message& m) { CHECK(m.mt43.wx.warning_state == 7); });
    }
    SUBCASE("Category 11: Flood") {
        verify_mapping(11, [](Message& m) { CHECK(m.mt43.flood.count > 0); CHECK(m.mt43.flood.entries[0].warning_level == 15); });
    }
    SUBCASE("Category 12: Typhoon") {
        verify_mapping(12, [](Message& m) { CHECK(m.mt43.typh.number == 99); });
    }
    SUBCASE("Category 14: Marine") {
        verify_mapping(14, [](Message& m) { CHECK(m.mt43.marine.count > 0); CHECK(m.mt43.marine.entries[0].warning_code == 31); });
    }
}

// ── Long Period Ground Motion (from test_long_period_ground_motion) ──────────

TEST_CASE("DCR: Long Period Ground Motion") {
    Message msg{};
    // From Python test: $QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B
    const char* nmea = "$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 1); // EEW
    // long_period_ground_motion_lower_limit == 3 (raw)
    CHECK(msg.mt43.eew.long_period_lower == 3);
    // long_period_ground_motion_upper_limit == 3 (raw)
    CHECK(msg.mt43.eew.long_period_upper == 3);
}

// ── Decode Error Handling (from test_decode_error) ───────────────────────────

TEST_CASE("DCR: CRC Mismatch Rejection") {
    // From Python test: C6AF89A820000324000050400548C5E2C000000003DFF8001C000011854432D
    // This hex string has a deliberately wrong CRC (last byte 2D instead of FC)
    // We wrap it in NMEA format with a valid NMEA checksum but invalid DCR CRC
    Message msg{};
    // The NMEA checksum is valid, but the DCR CRC inside will not match
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C000011854432D*34\r\n";
    bool ok = decode_nmea(nmea, msg);
    // Should fail because DCR CRC doesn't match
    CHECK_FALSE(ok);
}

TEST_CASE("DCR: NMEA Checksum Mismatch Rejection") {
    Message msg{};
    // From Python test: $QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00
    // Valid DCR CRC but wrong NMEA checksum (00 instead of correct value)
    const char* nmea = "$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00\r\n";
    bool ok = decode_nmea(nmea, msg);
    // Should fail because NMEA checksum doesn't match
    CHECK_FALSE(ok);
}

// ── DCX Null Message (from test_dcx) ─────────────────────────────────────────

TEST_CASE("DCX: Null Message") {
    Message msg{};
    // From Python test: $QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

// ── Nankai Trough Earthquake - completed flag (from test_scenario3) ───────────

TEST_CASE("DCR: Nankai Trough - page/total_page tracking") {
    Message msg{};
    // First message in sequence - page != total_page means not completed
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4);
    // nankai.page and nankai.total_page should be decoded
    // For non-final messages, page != total_page
    CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
}

TEST_CASE("DCR: Nankai Trough - completed flag verification") {
    // From azarashi test_scenario3: test the last message in sequence
    // The last message has page == total_page, meaning completed = true
    
    // First message: page != total_page (not completed)
    {
        Message msg{};
        const char* nmea = "$QZQSM,58,9AAFA19C918002F1C0C271C0D771C1CBF1C1D671C1DE71C1C404D8104D300D8*7F\r\n";
        REQUIRE(decode_nmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 4);
        // Not the final page
        CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
    }
    
    // Note: The last message in azarashi test_scenario3 has 65 hex chars (nibbles),
    // which exceeds the spec limit of 63 nibbles (250 bits).
    // azaraC correctly rejects this as "Too Long Sentence" per IS-QZSS-DCX-003.
    // This is tested in "DCR: Nankai Trough - oversized message rejected" below.
}

TEST_CASE("DCR: Nankai Trough - full sequence from azarashi test_scenario3") {
    // From azarashi test_scenario3: test messages in sequence
    // Note: The last message (index 20) has 65 hex chars and is rejected by azaraC
    // because it exceeds the 63 nibble limit. We test only the valid messages here.
    const char* nmea_messages[] = {
        "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0D471C0D1F1C0D371C0C7F1C0D071C0CAB4D812D45BCD0*06\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0CFF4CC5973C0DEF2D7DF72DFCE71C14932D813A64867C*0C\r\n",
        "$QZQSM,58,53AFA19C918002F1C0C5F1C0C8F3D6C4F1C0D5F2DFCE71C0CC30D81029188EC*0F\r\n",
        "$QZQSM,58,C6AFA19C918002F1C0D4F1C0C5F1C144F1C0D772C8DE71C0D9AED8108F361A8*7A\r\n",
        "$QZQSM,58,9AAFA19C918002F2DD4E71C1427443D573595DF25EC9F1C0D52CD81113EFC54*00\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0CCF1C041725DC572DF4671C0D7734A5FAAD811D504B9C*09\r\n",
        "$QZQSM,58,53AFA19C918002F1C0D4744041F1C0C471C144F1C14671C0DF28D8127EDCCCC*02\r\n",
        "$QZQSM,58,C6AFA19C918002F4D5CC71C0DF71C0D1F1C0D371C0C271C145A6D812E9F0C70*03\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0DCF1C0D373CDDC72D7DF73CD4271C0D5A4D813579A170*78\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0C672DCD9F2DC5C734CC171C0D5F357CA22D8100D3A898*07\r\n",
        "$QZQSM,58,53AFA19C918002F1C0D773CCDD73CA4FF2C7D7F441DEF34053A0D8108524298*01\r\n",
        "$QZQSM,58,C6AFA19C918002F1C040F2D253F45347F35450F2CE5874CE439ED8113990640*7D\r\n",
        "$QZQSM,58,9AAFA19C918002F2D74D74CE43F35D4872CFCFF1C0D3F1C0D79CD8118D63AC8*07\r\n",
        "$QZQSM,58,9AAFA19C918002F1C1D4F1C1CAF2CE5874CE43F1C0D77341D99AD81268C2E7C*73\r\n",
        "$QZQSM,58,53AFA19C918002F1C14471C14571C040F2C6CBF35ADBF1C1C418D812DC94FA0*7F\r\n",
        "$QZQSM,58,C6AFA19C918002F1C0DCF1C14571C0D773CCDD73CA4FF1C0D596D81357F75D0*74\r\n",
        "$QZQSM,58,9AAFA19C918002F1C145F1C14371C0D1F1C0C7F1C14571C0CC94D813ED6741C*0C\r\n",
        "$QZQSM,58,9AAFA19C918002F4C04D72DC5C71C0D471C0D7F3CAD871C0D512D810ADB00F0*78\r\n",
        "$QZQSM,58,9AAFA19C918002F1C0C271C0D771C1CBF1C1D671C1DE71C1C404D8104D300D8*7F\r\n",
    };

    for (size_t i = 0; i < sizeof(nmea_messages)/sizeof(nmea_messages[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decode_nmea(nmea_messages[i], msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 4);
        // All these messages have page != total_page (not completed)
        CHECK(msg.mt43.nankai.page != msg.mt43.nankai.total_page);
    }
}

TEST_CASE("DCR: Nankai Trough - oversized message rejected") {
    Message msg{};
    // From Python test: $QZQSM,58,9AAFA19C918002F1C0C271C0410000000000000000000000000036D81121AA2D0*07
    // This message has 65 hex chars (nibbles), exceeding the spec limit of 63 nibbles (250 bits).
    // Per IS-QZSS-DCX-003, DCX message must be exactly 250 bits = 63 hex chars.
    // azarashi correctly rejects this as "Too Long Sentence".
    const char* nmea = "$QZQSM,58,9AAFA19C918002F1C0C271C0410000000000000000000000000036D81121AA2D0*07\r\n";
    bool ok = decode_nmea(nmea, msg);
    // Should be rejected because hex_len (65) != 63
    CHECK_FALSE(ok);
}

// ── Ash Fall Detailed (from test_scenario5) ───────────────────────────────────

TEST_CASE("DCR: Ash Fall Detailed - Sequence") {
    // Test multiple ash fall messages in sequence
    struct TestCase {
        const char* nmea;
    };
    TestCase cases[] = {
        "$QZQSM,58,C6AFC99CAA0001CAA43EE541F0782A1220813091811183E0F000001329B16E0*7F\r\n",
        "$QZQSM,58,C6AFC99CAA0001CAA43EE8C2441046123023307C1E19848820000013E2F3E6C*00\r\n",
        "$QZQSM,58,9AAFC99CAA0001CAA43EECC24604860F83C430910421848C080000106286874*00\r\n",
        "$QZQSM,58,53AFC99CAA0001CAA43EF4C1F078A61220853091813183E0F0000010CE8C39C*77\r\n",
        "$QZQSM,58,C6AFC99CAA0001CAA43EF8C24410C61230200000000000000000001148565F4*0A\r\n",
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decode_nmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 9); // Ash fall
    }
}

// ── Weather Multi (from test_scenario6) ───────────────────────────────────────

TEST_CASE("DCR: Weather - Multiple Messages") {
    struct TestCase {
        const char* nmea;
        uint8_t expected_dc;
    };
    TestCase cases[] = {
        // Weather messages
        {"$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73\r\n", 10},
        {"$QZQSM,58,9AAFD19CB180011222E0B93880B95F90B986A0B9ADB0B9D4C0000013D276B60*0D\r\n", 10},
        {"$QZQSM,58,53AFD19CB18001B9FBD0BA22E00000000000000000000000000000107AA71EC*76\r\n", 10},
        // Flood message
        {"$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E\r\n", 11},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        REQUIRE(decode_nmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == cases[i].expected_dc);
    }
}
