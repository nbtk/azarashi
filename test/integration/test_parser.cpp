// test/integration/test_parser.cpp — パーサー統合テスト
// EEW, DCX (MT=44), decodePrefectureBitmask, B1 Refinement の統合テスト

#include "../test_helpers.h"
#include "../include/internal/DcxHelper.h"
#include "doctest.h"

using namespace azaraC;

// ═══════════════════════════════════════════════════════════════════════════════
// EEW デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeEEW: 基本的なEEWメッセージのデコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);       // preamble
    setBits(bits, 8, 6, 43);        // msg_type
    setBits(bits, 14, 3, 1);        // report_classification
    setBits(bits, 17, 4, 1);        // disaster_category = 1 (EEW)
    setBits(bits, 41, 2, 0);        // information_type
    setBits(bits, 214, 6, 1);      // version = 1

    setBits(bits, 47, 3, 3);        // long_period_lower = 3
    setBits(bits, 50, 3, 5);        // long_period_upper = 5

    setBits(bits, 53, 9, 100);      // notification 1
    setBits(bits, 62, 9, 200);      // notification 2

    setBits(bits, 80, 5, 15);       // day = 15
    setBits(bits, 85, 5, 10);       // hour = 10
    setBits(bits, 90, 6, 30);       // minute = 30

    setBits(bits, 96, 9, 50);       // depth = 50km
    setBits(bits, 105, 7, 65);      // magnitude = 6.5
    setBits(bits, 112, 10, 25);     // epicenter code = 25
    setBits(bits, 122, 4, 3);       // intensity lower = 3
    setBits(bits, 126, 4, 7);       // intensity upper = 7

    setBits(bits, 130, 1, 1);       // region 1
    setBits(bits, 134, 1, 1);       // region 5
    setBits(bits, 139, 1, 1);       // region 10

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    uint32_t now_unix = 1704067200u;
    msg.payload_type = MsgPayloadType::Mt43;
    msg.mt43.disaster_category = 1;
    TestDecoder::testDecodeEEW(bits, msg, now_unix);

    CHECK(msg.mt43.disaster_category == 1);
    CHECK(msg.mt43.eew.long_period_lower == 3);
    CHECK(msg.mt43.eew.long_period_upper == 5);
    CHECK(msg.mt43.eew.notification_count == 2);
    CHECK(msg.mt43.eew.notification[0] == 100);
    CHECK(msg.mt43.eew.notification[1] == 200);
    CHECK(msg.mt43.eew.quake_time.day == 15);
    CHECK(msg.mt43.eew.quake_time.hour == 10);
    CHECK(msg.mt43.eew.quake_time.minute == 30);
    CHECK(msg.mt43.eew.depth == 50);
    CHECK(msg.mt43.eew.magnitude == 65);
    CHECK(msg.mt43.eew.epicenter == 25);
    CHECK(msg.mt43.eew.intensity_lower == 3);
    CHECK(msg.mt43.eew.intensity_upper == 7);
    CHECK(msg.mt43.eew.region_count == 3);
    CHECK(msg.mt43.eew.regions[0] == 1);
    CHECK(msg.mt43.eew.regions[1] == 5);
    CHECK(msg.mt43.eew.regions[2] == 10);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DCX (MT=44) デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

static Message decodeDcxHelper(uint8_t* bits, uint32_t now_unix = 1704067200u) {
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    TestDecoder decoder;
    Message msg{};
    Frame frame{};
    memcpy(frame.bits, bits, 32);
    frame.svid = 193;
    decoder.decode(frame, msg, now_unix);
    return msg;
}

TEST_CASE("decodeDcx: L-Alert メッセージのデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0x1FF);

    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 1);
    setBits(bits, 40, 7, 10);
    setBits(bits, 47, 2, 3);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 7200);
    setBits(bits, 64, 2, 2);
    setBits(bits, 66, 1, 0);
    setBits(bits, 67, 3, 1);
    setBits(bits, 70, 10, 1);
    setBits(bits, 80, 16, 45761);
    setBits(bits, 96, 17, 116395);
    setBits(bits, 113, 5, 13);
    setBits(bits, 118, 5, 11);
    setBits(bits, 123, 6, 48);
    setBits(bits, 129, 2, 0);
    setBits(bits, 131, 15, 0);

    setBits(bits, 146, 16, 1100);
    setBits(bits, 214, 6, 1);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.sd.sdmt == 0);
    CHECK(msg.mt44.sd.sdm == 0x1FF);
    CHECK(msg.mt44.camf.a1 == 1);
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 1);
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1100);
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

TEST_CASE("decodeDcx: J-Alert メッセージのデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0x1FF);

    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 2);
    setBits(bits, 40, 7, 5);
    setBits(bits, 47, 2, 3);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 0);
    setBits(bits, 64, 2, 0);
    setBits(bits, 66, 1, 0);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);
    setBits(bits, 80, 16, 0);
    setBits(bits, 96, 17, 0);
    setBits(bits, 113, 5, 0);
    setBits(bits, 118, 5, 0);
    setBits(bits, 123, 6, 0);
    setBits(bits, 129, 2, 0);
    setBits(bits, 131, 15, 0);

    setBits(bits, 146, 1, 0);
    setBits(bits, 147, 32, 0);
    setBits(bits, 179, 32, 3);
    setBits(bits, 211, 3, 0);
    setBits(bits, 214, 6, 1);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 2);
    CHECK(msg.mt44.ex_jalert.ex8 == 0);
    CHECK(msg.mt44.ex_jalert.ex9 == 3);
    CHECK(msg.mt44.ex_jalert.vn == 1);
}

TEST_CASE("decodeDcx: Local Government メッセージのデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0x1FF);

    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 4);
    setBits(bits, 40, 7, 10);
    setBits(bits, 47, 2, 3);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 7200);
    setBits(bits, 64, 2, 2);
    setBits(bits, 66, 1, 0);
    setBits(bits, 67, 3, 1);
    setBits(bits, 70, 10, 1);
    setBits(bits, 80, 16, 45761);
    setBits(bits, 96, 17, 116395);
    setBits(bits, 113, 5, 13);
    setBits(bits, 118, 5, 11);
    setBits(bits, 123, 6, 48);
    setBits(bits, 129, 2, 0);
    setBits(bits, 131, 15, 0);

    setBits(bits, 146, 16, 1100);
    setBits(bits, 162, 1, 1);
    setBits(bits, 163, 17, 91522);
    setBits(bits, 180, 17, 68950);
    setBits(bits, 197, 5, 13);
    setBits(bits, 202, 5, 11);
    setBits(bits, 207, 7, 96);
    setBits(bits, 214, 6, 1);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LocalGovernment);
    CHECK(msg.mt44.camf.a3 == 4);
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1100);
    CHECK(msg.mt44.ex_lalert_local.ex2 == 1);
    CHECK(msg.mt44.ex_lalert_local.ex3 == 91522);
    CHECK(msg.mt44.ex_lalert_local.ex4 == 68950);
    CHECK(msg.mt44.ex_lalert_local.ex5 == 13);
    CHECK(msg.mt44.ex_lalert_local.ex6 == 11);
    CHECK(msg.mt44.ex_lalert_local.ex7 == 96);
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

TEST_CASE("decodeDcx: Outside Japan メッセージのデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0x1FF);

    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 32);
    setBits(bits, 35, 5, 1);
    setBits(bits, 40, 7, 10);
    setBits(bits, 47, 2, 3);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 0);
    setBits(bits, 64, 2, 0);
    setBits(bits, 66, 1, 0);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);
    setBits(bits, 80, 16, 0);
    setBits(bits, 96, 17, 0);
    setBits(bits, 113, 5, 0);
    setBits(bits, 118, 5, 0);
    setBits(bits, 123, 6, 0);
    setBits(bits, 129, 2, 0);
    setBits(bits, 131, 15, 0);

    for (int i = 0; i < 8; ++i) {
        setBits(bits, 146 + i * 8, 8, 0xAB);
    }
    setBits(bits, 210, 4, 0xF);
    setBits(bits, 214, 6, 5);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 32);
    CHECK(msg.mt44.ex_outside.vn == 5);
}

TEST_CASE("decodeDcx: NULL Message のデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0);

    setBits(bits, 26, 9, 111);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

// ═══════════════════════════════════════════════════════════════════════════════
// decodePrefectureBitmask 単体テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodePrefectureBitmask: 仕様書例（北海道・青森・岩手）") {
    uint64_t ex9 = (uint64_t)7 << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 3);
    CHECK(positions[0] == 1);
    CHECK(positions[1] == 2);
    CHECK(positions[2] == 3);
}

TEST_CASE("decodePrefectureBitmask: 沖縄のみ（MSB）") {
    uint64_t ex9 = (uint64_t)1 << 63;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 47);
}

TEST_CASE("decodePrefectureBitmask: 全都道府県（全ビット=1）") {
    uint64_t ex9 = ((1ULL << 47) - 1) << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 47);
    CHECK(positions[0] == 1);
    CHECK(positions[46] == 47);
}

TEST_CASE("decodePrefectureBitmask: 空（ゼロ）") {
    uint64_t ex9 = 0;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// B1 (A17=00) - Improved Resolution of Main Ellipse Tests
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeB1Refinement: 基本的な分割") {
    uint16_t a18 = (5 << 12) | (3 << 9) | (2 << 6) | (1 << 3);
    B1Refinement b1 = azaraC::internal::decodeB1Refinement(a18);

    CHECK(b1.c1 == 5);
    CHECK(b1.c2 == 3);
    CHECK(b1.c3 == 2);
    CHECK(b1.c4 == 1);
}

TEST_CASE("decodeB1Refinement: 全ゼロ") {
    B1Refinement b1 = azaraC::internal::decodeB1Refinement(0);

    CHECK(b1.c1 == 0);
    CHECK(b1.c2 == 0);
    CHECK(b1.c3 == 0);
    CHECK(b1.c4 == 0);
}

TEST_CASE("decodeB1Refinement: 最大値（全7）") {
    uint16_t a18 = (7 << 12) | (7 << 9) | (7 << 6) | (7 << 3);
    B1Refinement b1 = azaraC::internal::decodeB1Refinement(a18);

    CHECK(b1.c1 == 7);
    CHECK(b1.c2 == 7);
    CHECK(b1.c3 == 7);
    CHECK(b1.c4 == 7);
}

TEST_CASE("b1RefinedLatitudeOffset: 計算値検証") {
    CHECK(azaraC::internal::b1RefinedLatitudeOffset(0) == 0.0);

    double expected_1 = 180.0 / (8.0 * 65535.0);
    CHECK(azaraC::internal::b1RefinedLatitudeOffset(1) == doctest::Approx(expected_1));

    double expected_7 = 7.0 * 180.0 / (8.0 * 65535.0);
    CHECK(azaraC::internal::b1RefinedLatitudeOffset(7) == doctest::Approx(expected_7));
}

TEST_CASE("b1RefinedLongitudeOffset: 計算値検証") {
    CHECK(azaraC::internal::b1RefinedLongitudeOffset(0) == 0.0);

    double expected_1 = 360.0 / (8.0 * 131071.0);
    CHECK(azaraC::internal::b1RefinedLongitudeOffset(1) == doctest::Approx(expected_1));

    double expected_7 = 7.0 * 360.0 / (8.0 * 131071.0);
    CHECK(azaraC::internal::b1RefinedLongitudeOffset(7) == doctest::Approx(expected_7));
}

TEST_CASE("b1InterpolationFactor: 計算値検証") {
    CHECK(azaraC::internal::b1InterpolationFactor(0) == 0.0);
    CHECK(azaraC::internal::b1InterpolationFactor(1) == 0.125);
    CHECK(azaraC::internal::b1InterpolationFactor(4) == 0.5);
    CHECK(azaraC::internal::b1InterpolationFactor(7) == 0.875);
}

TEST_CASE("DCX B1: L-AlertメッセージでのB1解析") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0);
    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 1);
    setBits(bits, 40, 7, 74);
    setBits(bits, 47, 2, 2);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 100);
    setBits(bits, 64, 2, 1);
    setBits(bits, 66, 1, 1);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);

    setBits(bits, 80, 16, 32768);
    setBits(bits, 96, 17, 65536);
    setBits(bits, 113, 5, 10);
    setBits(bits, 118, 5, 8);
    setBits(bits, 123, 6, 32);

    setBits(bits, 129, 2, 0);
    setBits(bits, 131, 15, (5 << 12) | (3 << 9) | (2 << 6) | (1 << 3));

    setBits(bits, 146, 16, 1100);
    setBits(bits, 214, 6, 1);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    Decoder decoder;
    Frame frame;
    frame.svid = 56;
    memcpy(frame.bits, bits, 32);

    uint32_t report_unix = 1704067200u;
    bool result = decoder.decode(frame, msg, report_unix);

    CHECK(result == true);
    CHECK(msg.valid == true);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.camf.b1_present == true);
    CHECK(msg.mt44.camf.b1_c1 == 5);
    CHECK(msg.mt44.camf.b1_c2 == 3);
    CHECK(msg.mt44.camf.b1_c3 == 2);
    CHECK(msg.mt44.camf.b1_c4 == 1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// B2 (A17=01) - Position of the Centre of the Hazard 統合テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX B2: ハザード中心オフセットが主楕円座標に反映される") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0);
    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 1);
    setBits(bits, 40, 7, 74);
    setBits(bits, 47, 2, 2);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 100);
    setBits(bits, 64, 2, 1);
    setBits(bits, 66, 1, 1);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);

    setBits(bits, 80, 16, 32768);
    setBits(bits, 96, 17, 65536);
    setBits(bits, 113, 5, 10);
    setBits(bits, 118, 5, 8);
    setBits(bits, 123, 6, 32);

    setBits(bits, 129, 2, 1);
    uint16_t a18_b2 = (63u & 0x7Fu) | ((63u & 0x7Fu) << 7);
    setBits(bits, 131, 15, a18_b2);

    setBits(bits, 146, 16, 1100);
    setBits(bits, 214, 6, 1);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    Decoder decoder;
    Frame frame;
    frame.svid = 56;
    memcpy(frame.bits, bits, 32);

    bool result = decoder.decode(frame, msg, 1704067200u);

    REQUIRE(result == true);
    CHECK(msg.valid == true);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.camf.b2_present == true);
    CHECK(msg.mt44.camf.b2_c5 == 63);
    CHECK(msg.mt44.camf.b2_c6 == 63);
}

// ═══════════════════════════════════════════════════════════════════════════════
// B3 (A17=10) - Secondary Ellipse Definition 統合テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX B3: 副楕円パラメータが camf に反映される") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0);
    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 1);
    setBits(bits, 40, 7, 74);
    setBits(bits, 47, 2, 2);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 100);
    setBits(bits, 64, 2, 1);
    setBits(bits, 66, 1, 1);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);

    setBits(bits, 80, 16, 45761);
    setBits(bits, 96, 17, 116395);
    setBits(bits, 113, 5, 13);
    setBits(bits, 118, 5, 8);
    setBits(bits, 123, 6, 32);

    uint16_t a18_b3 = (3u & 0x03u) | ((7u & 0x07u) << 2) | ((31u & 0x1Fu) << 5) | (0u << 10);
    setBits(bits, 129, 2, 2);
    setBits(bits, 131, 15, a18_b3);

    setBits(bits, 146, 16, 1100);
    setBits(bits, 214, 6, 1);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    Decoder decoder;
    Frame frame;
    frame.svid = 56;
    memcpy(frame.bits, bits, 32);

    bool result = decoder.decode(frame, msg, 1704067200u);

    REQUIRE(result == true);
    CHECK(msg.valid == true);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.camf.b3_present == true);
    CHECK(msg.mt44.camf.b3_c7  == 3);
    CHECK(msg.mt44.camf.b3_c8  == 7);
    CHECK(msg.mt44.camf.b3_c9  == 31);
    CHECK(msg.mt44.camf.b3_c10 == 0);
}
