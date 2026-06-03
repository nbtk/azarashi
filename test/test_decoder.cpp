// test/test_decoder.cpp — デコーダーの詳細検証
// EEW, DCX (MT=44), decodePrefectureBitmask, B1 Refinement の単体テスト

#include "test_helpers.h"
#include "../src/internal/DcxHelper.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

// ═══════════════════════════════════════════════════════════════════════════════
// EEW デコードテスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeEEW: 基本的なEEWメッセージのデコード") {
    uint8_t bits[32] = {};
    Message msg{};

    // プリアンブル: 0x53, MT: 43 (0b101011), DC: 1 (EEW)
    setBits(bits, 0, 8, 0x53);       // preamble
    setBits(bits, 8, 6, 43);        // msg_type
    setBits(bits, 14, 3, 1);        // report_classification
    setBits(bits, 17, 4, 1);        // disaster_category = 1 (EEW)
    setBits(bits, 41, 2, 0);        // information_type
    setBits(bits, 214, 6, 1);      // version = 1

    // EEWフィールド: offset 47から
    setBits(bits, 47, 3, 3);        // long_period_lower = 3
    setBits(bits, 50, 3, 5);        // long_period_upper = 5

    // notifications: 3 × 9bits at [53..79]
    setBits(bits, 53, 9, 100);      // notification 1
    setBits(bits, 62, 9, 200);      // notification 2

    // eew_quake_time: day=15, hour=10, minute=30
    setBits(bits, 80, 5, 15);       // day = 15
    setBits(bits, 85, 5, 10);       // hour = 10
    setBits(bits, 90, 6, 30);       // minute = 30

    setBits(bits, 96, 9, 50);       // depth = 50km
    setBits(bits, 105, 7, 65);      // magnitude = 6.5 (65 * 0.1)
    setBits(bits, 112, 10, 25);     // epicenter code = 25
    setBits(bits, 122, 4, 3);       // intensity lower = 3
    setBits(bits, 126, 4, 7);       // intensity upper = 7

    // EEW forecast regions: 80-bit bitmask at [130..209]
    setBits(bits, 130, 1, 1);       // region 1
    setBits(bits, 134, 1, 1);       // region 5
    setBits(bits, 139, 1, 1);       // region 10

    // CRC計算とセット
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
    setBits(bits, 14, 1, 0);         // SDMT = 0
    setBits(bits, 15, 9, 0x1FF);     // SDM = 全1

    setBits(bits, 24, 2, 1);         // A1 = 01 (Alert)
    setBits(bits, 26, 9, 111);       // A2 = 111 (Japan)
    setBits(bits, 35, 5, 1);         // A3 = 1 (FMMC/L-Alert)
    setBits(bits, 40, 7, 10);        // A4 = 10 (Hazard)
    setBits(bits, 47, 2, 3);         // A5 = 3 (Severity)
    setBits(bits, 49, 1, 0);         // A6 = 0
    setBits(bits, 50, 14, 7200);     // A7 = 7200 (minute of week)
    setBits(bits, 64, 2, 2);         // A8 = 2 (Duration)
    setBits(bits, 66, 1, 0);         // A9 = 0
    setBits(bits, 67, 3, 1);         // A10 = 1
    setBits(bits, 70, 10, 1);        // A11 = 1 (Guidance)
    setBits(bits, 80, 16, 45761);    // A12 = 45761 (lat)
    setBits(bits, 96, 17, 116395);   // A13 = 116395 (lon)
    setBits(bits, 113, 5, 13);       // A14 = 13 (semi-major ~10.9km)
    setBits(bits, 118, 5, 11);       // A15 = 11 (semi-minor ~6.0km)
    setBits(bits, 123, 6, 48);       // A16 = 48 (azimuth ~45°)
    setBits(bits, 129, 2, 0);        // A17 = 0
    setBits(bits, 131, 15, 0);       // A18 = 0

    setBits(bits, 146, 16, 1100);    // EX1 = 1100 (札幌市)
    setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::LAlertOrLocal);
    CHECK(msg.mt44.sd.sdmt == 0);
    CHECK(msg.mt44.sd.sdm == 0x1FF);
    CHECK(msg.mt44.camf.a1 == 1);
    CHECK(msg.mt44.camf.a2 == 111);
    CHECK(msg.mt44.camf.a3 == 1);
    CHECK(msg.mt44.camf.a4 == 10);
    CHECK(msg.mt44.camf.a5 == 3);
    CHECK(msg.mt44.camf.a11 == 1);
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
    setBits(bits, 35, 5, 2);         // A3 = 2 (FDMA/J-Alert)
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

    setBits(bits, 146, 1, 0);        // EX8 = 0 (prefecture)
    setBits(bits, 147, 32, 0);       // EX9 hi = 0
    setBits(bits, 179, 32, 3);       // EX9 lo = 3 (Hokkaido + Aomori)
    setBits(bits, 211, 3, 0);        // EX10 = 0 (reserved)
    setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::JAlert);
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
    setBits(bits, 35, 5, 4);         // A3 = 4 (Local Government)
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

    setBits(bits, 146, 16, 1100);    // EX1 = 1100
    setBits(bits, 162, 1, 1);        // EX2 = 1 (Head to area)
    setBits(bits, 163, 17, 91522);   // EX3 = 91522 (lat)
    setBits(bits, 180, 17, 68950);   // EX4 = 68950 (lon)
    setBits(bits, 197, 5, 13);       // EX5 = 13
    setBits(bits, 202, 5, 11);       // EX6 = 11
    setBits(bits, 207, 7, 96);       // EX7 = 96
    setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LocalGovernment);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::LAlertOrLocal);
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
    setBits(bits, 26, 9, 32);        // A2 = 32 (Australia)
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

    // EX11 = 68bit raw data
    for (int i = 0; i < 8; ++i) {
        setBits(bits, 146 + i * 8, 8, 0xAB);
    }
    setBits(bits, 210, 4, 0xF);
    setBits(bits, 214, 6, 5);        // Vn = 5

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 32);
    CHECK(msg.mt44.ex_outside.vn == 5);
    for (int i = 0; i < 8; ++i) {
        CHECK(msg.mt44.ex_outside.ex11_raw[i] == 0xAB);
    }
    CHECK((msg.mt44.ex_outside.ex11_raw[8] & 0xF0) == 0xF0);
}

TEST_CASE("decodeDcx: NULL Message のデコード") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0);         // SDM = 0

    // NULL Message requires A2=111 (Japan) and A3=0
    setBits(bits, 26, 9, 111);       // A2 = 111 (Japan)
    // A3=0, A4-A18=0, Extended=0 (already zeroed)

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

TEST_CASE("decodeDcx: 未知の A3 値は破棄されるが SD は維持される") {
    uint8_t bits[32] = {};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 44);
    setBits(bits, 14, 1, 0);
    setBits(bits, 15, 9, 0x1FF);

    setBits(bits, 24, 2, 1);
    setBits(bits, 26, 9, 111);
    setBits(bits, 35, 5, 5);         // A3 = 5 (未知)
    setBits(bits, 40, 7, 10);
    setBits(bits, 47, 2, 3);

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::Unknown);
    CHECK(msg.mt44.sd.sdmt == 0);
    CHECK(msg.mt44.sd.sdm == 0x1FF);
}

// ═══════════════════════════════════════════════════════════════════════════════
// decodePrefectureBitmask 単体テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodePrefectureBitmask: 仕様書例（北海道・青森・岩手）") {
    uint64_t ex9 = (uint64_t)7 << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 3);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[1] == 2);   // 青森県
    CHECK(positions[2] == 3);   // 岩手県
}

TEST_CASE("decodePrefectureBitmask: 沖縄のみ（MSB）") {
    uint64_t ex9 = (uint64_t)1 << 63;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 47);  // 沖縄県
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

TEST_CASE("decodePrefectureBitmask: ビット17だけ設定（北海道）") {
    uint64_t ex9 = (uint64_t)1 << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 1);
}

TEST_CASE("decodePrefectureBitmask: reservedビットは無視される") {
    uint64_t ex9 = (uint64_t)0xFFFF;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// B1 (A17=00) - Improved Resolution of Main Ellipse Tests
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("decodeB1Refinement: 基本的な分割") {
    // A18 bit layout: bit[14]=MSB (spec bit 131), bit[0]=LSB (spec bit 145)
    // C1 = (a18 >> 12) & 0x07, C2 = (a18 >> 9) & 0x07
    // C3 = (a18 >> 6) & 0x07,  C4 = (a18 >> 3) & 0x07
    // C1=5, C2=3, C3=2, C4=1
    // a18 = 0b0101_0011_0010_0001 = (5<<12)|(3<<9)|(2<<3)|1 = 0x5321... wait
    // C1=5 → bits 14:12 = 0b101 → (5 << 12)
    // C2=3 → bits 11:9  = 0b011 → (3 << 9)
    // C3=2 → bits 8:6   = 0b010 → (2 << 6)
    // C4=1 → bits 5:3   = 0b001 → (1 << 3)
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
    // C1=7 → (7 << 12), C2=7 → (7 << 9), C3=7 → (7 << 6), C4=7 → (7 << 3)
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

    setBits(bits, 129, 2, 0);       // A17 = 00 (B1)
    // A18: C1=5, C2=3, C3=2, C4=1 (MSB-first)
    // C1=5 → (5 << 12), C2=3 → (3 << 9), C3=2 → (2 << 6), C4=1 → (1 << 3)
    setBits(bits, 131, 15, (5 << 12) | (3 << 9) | (2 << 6) | (1 << 3));  // A18

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

    CHECK(msg.mt44.mt44_decoded.main_ellipse_present == true);
    CHECK(msg.mt44.mt44_decoded.main_ellipse.b1_lat_offset_deg == doctest::Approx(5.0 * 180.0 / (8.0 * 65535.0)));
    CHECK(msg.mt44.mt44_decoded.main_ellipse.b1_lon_offset_deg == doctest::Approx(3.0 * 360.0 / (8.0 * 131071.0)));
    CHECK(msg.mt44.mt44_decoded.main_ellipse.b1_major_factor == 0.25);
    CHECK(msg.mt44.mt44_decoded.main_ellipse.b1_minor_factor == 0.125);
}

TEST_CASE("DCX B1: B1なしメッセージ（A17=00だがC1-C4全ゼロ）") {
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
    setBits(bits, 131, 15, 0);

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
    CHECK(msg.mt44.camf.b1_present == false);
}

// ═══════════════════════════════════════════════════════════════════════════════
// B2 (A17=01) - Position of the Centre of the Hazard 統合テスト
// B2 が mt44_decoded.main_ellipse の lat/lon に加算されることを検証
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
    setBits(bits, 35, 5, 1);          // A3=1 (L-Alert)
    setBits(bits, 40, 7, 74);
    setBits(bits, 47, 2, 2);
    setBits(bits, 49, 1, 0);
    setBits(bits, 50, 14, 100);
    setBits(bits, 64, 2, 1);
    setBits(bits, 66, 1, 1);
    setBits(bits, 67, 3, 0);
    setBits(bits, 70, 10, 0);

    // 主楕円 (A12-A16): Tokyo 付近
    setBits(bits, 80, 16, 32768);     // A12: lat ~0°
    setBits(bits, 96, 17, 65536);     // A13: lon ~0°
    setBits(bits, 113, 5, 10);        // A14: semi-major
    setBits(bits, 118, 5, 8);         // A15: semi-minor
    setBits(bits, 123, 6, 32);        // A16: azimuth ~0°

    // A17=01 → B2
    setBits(bits, 129, 2, 1);
    // A18: C5[0:6]=63(ほぼ0.0°), C6[7:13]=63(ほぼ0.0°)
    // B2: delta = -10 + (20/128) * C  (C <= 63)
    // C5=63: -10 + (20/128)*63 = -10 + 9.84375 = -0.15625
    // C6=63: -10 + (20/128)*63 = -10 + 9.84375 = -0.15625
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

    // B2 フラグ確認
    CHECK(msg.mt44.camf.b2_present == true);
    CHECK(msg.mt44.camf.b2_c5 == 63);
    CHECK(msg.mt44.camf.b2_c6 == 63);

    // mt44_decoded.main_ellipse に B2 オフセットが加算されているか確認
    // C5=63: delta_lat = -10 + (20/128)*63 = -0.15625
    // C6=63: delta_lon = -10 + (20/128)*63 = -0.15625
    // 元の lat/lon ≈ 0 + (-0.15625) = -0.15625 (許容±0.01°)
    CHECK(msg.mt44.mt44_decoded.main_ellipse_present == true);
    CHECK(msg.mt44.mt44_decoded.main_ellipse.lat_deg == doctest::Approx(-0.15625).epsilon(0.01));
    CHECK(msg.mt44.mt44_decoded.main_ellipse.lon_deg == doctest::Approx(-0.15625).epsilon(0.01));
}

TEST_CASE("DCX B2: C5=0/C6=0 はオフセット-10.0°を加算する") {
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

    // 主楕円: code=32768 → lat≈0°, code=65536 → lon≈0°
    setBits(bits, 80, 16, 32768);
    setBits(bits, 96, 17, 65536);
    setBits(bits, 113, 5, 10);
    setBits(bits, 118, 5, 8);
    setBits(bits, 123, 6, 32);

    // A17=01, A18: C5=0, C6=0
    setBits(bits, 129, 2, 1);
    setBits(bits, 131, 15, 0);  // C5=0, C6=0

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
    CHECK(msg.mt44.camf.b2_present == true);
    CHECK(msg.mt44.camf.b2_c5 == 0);
    CHECK(msg.mt44.camf.b2_c6 == 0);

    // C5=0, C6=0: delta = -10.0° → lat≈0+(-10)=-10°, lon≈0+(-10)=-10°
    CHECK(msg.mt44.mt44_decoded.main_ellipse.lat_deg == doctest::Approx(-10.0).epsilon(0.01));
    CHECK(msg.mt44.mt44_decoded.main_ellipse.lon_deg == doctest::Approx(-10.0).epsilon(0.01));
}

// ═══════════════════════════════════════════════════════════════════════════════
// B3 (A17=10) - Secondary Ellipse Definition 統合テスト
// B3 が camf フラグと shift_km/homothetic_factor/bearing_deg に反映されることを検証
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

    // 主楕円: semi-major=code13→10.933km で B3 の shift 計算基準になる
    setBits(bits, 80, 16, 45761);    // lat ~35.7°
    setBits(bits, 96, 17, 116395);   // lon ~139.7°
    setBits(bits, 113, 5, 13);       // A14=13 (semi-major ~10.933km)
    setBits(bits, 118, 5, 8);
    setBits(bits, 123, 6, 32);

    // A17=10 → B3
    // A18 = C7[0:1] + C8[2:4] + C9[5:9] + C10[10:14]
    // C7=3, C8=7, C9=31, C10=0
    // shift=C7 * semi_major_km = 3 * 10.933 = 32.799km
    // homothetic=C8=7 → 0.25 * (7+1) = 2.0
    // bearing=C9=31 → 31 * 11.25 = 348.75°
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

    // B3 フラグ確認
    CHECK(msg.mt44.camf.b3_present == true);
    CHECK(msg.mt44.camf.b3_c7  == 3);
    CHECK(msg.mt44.camf.b3_c8  == 7);
    CHECK(msg.mt44.camf.b3_c9  == 31);
    CHECK(msg.mt44.camf.b3_c10 == 0);

    // デコード済み値の確認
    // shift_km = C7 * semi_major_km = 3 * 10.933 = 32.799km
    // (semi_major_km は A14=13 から decodeRadiusCode(13) = 10.933 で計算)
    CHECK(msg.mt44.camf.b3_shift_km == doctest::Approx(32.799).epsilon(0.01));
    // homothetic_factor: C8=7 → 0.25 * (7+1) = 2.0
    CHECK(msg.mt44.camf.b3_homothetic_factor == doctest::Approx(2.0).epsilon(0.01));
    // bearing_deg: C9=31 → 31 * 11.25 = 348.75°
    CHECK(msg.mt44.camf.b3_bearing_deg == doctest::Approx(348.75).epsilon(0.01));

    // B3 の場合、主楕円自体は変更されない（B2 と異なり座標シフトなし）
    CHECK(msg.mt44.mt44_decoded.main_ellipse_present == true);
}
