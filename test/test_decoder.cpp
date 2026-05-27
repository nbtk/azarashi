// test/test_decoder.cpp — 各デコード関数の詳細検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/DcxHelper.h"
#include "../src/internal/NmeaFramer.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// テスト用にprotected関数を公開
struct TestDecoderEx : Decoder {
    // EEWデコードのテスト
    static void testDecodeEEW(const uint8_t* bits, Message& out, uint32_t now_unix) {
        // 一時オブジェクトで呼び出し
        TestDecoderEx t;
        t.decodeEEW(bits, out, now_unix);
    }

    static void setBits(uint8_t* buf, uint16_t start, uint8_t len, uint32_t value) {
        if (len == 0) return;
        for (int i = static_cast<int>(len) - 1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    }
    // CRC計算ヘルパー
    static uint32_t calculateCRC(const uint8_t* data, uint16_t bit_len) {
        return crc24q(data, bit_len);
    }
};

TEST_CASE("decodeEEW: 基本的なEEWメッセージのデコード") {
    uint8_t bits[32] = {};
    Message msg{};

    // プリアンブル: 0x53, MT: 43 (0b101011), DC: 1 (EEW)
    TestDecoderEx::setBits(bits, 0, 8, 0x53);       // preamble
    TestDecoderEx::setBits(bits, 8, 6, 43);        // msg_type
    TestDecoderEx::setBits(bits, 14, 3, 1);        // report_classification (仮)
    TestDecoderEx::setBits(bits, 17, 4, 1);        // disaster_category = 1 (EEW)
    TestDecoderEx::setBits(bits, 41, 2, 0);        // information_type
    TestDecoderEx::setBits(bits, 214, 6, 1);      // version = 1

    // EEWフィールド: offset 47から
    // eew_long_period_lower: 3bit at [47]
    TestDecoderEx::setBits(bits, 47, 3, 3);        // long_period_lower = 3
    // eew_long_period_upper: 3bit at [50]
    TestDecoderEx::setBits(bits, 50, 3, 5);        // long_period_upper = 5

    // notifications: 3 × 9bits at [53..79]
    TestDecoderEx::setBits(bits, 53, 9, 100);      // notification 1
    TestDecoderEx::setBits(bits, 62, 9, 200);      // notification 2
    // notification 3 = 0 (終了)

    // eew_quake_time: extractDHM at [80] (day=15, hour=10, minute=30)
    // 実際のextractDHMはday(5)+hour(5)+minute(6)=16bit
    TestDecoderEx::setBits(bits, 80, 5, 15);       // day = 15
    TestDecoderEx::setBits(bits, 85, 5, 10);       // hour = 10
    TestDecoderEx::setBits(bits, 90, 6, 30);       // minute = 30

    // eew_depth: 9bit at [96]
    TestDecoderEx::setBits(bits, 96, 9, 50);       // depth = 50km

    // eew_magnitude: 7bit at [105]
    TestDecoderEx::setBits(bits, 105, 7, 65);      // magnitude = 6.5 (65 * 0.1)

    // eew_epicenter: 10bit at [112]
    TestDecoderEx::setBits(bits, 112, 10, 25);     // epicenter code = 25

    // eew_intensity_lower: 4bit at [122]
    TestDecoderEx::setBits(bits, 122, 4, 3);       // intensity lower = 3

    // eew_intensity_upper: 4bit at [126]
    TestDecoderEx::setBits(bits, 126, 4, 7);       // intensity upper = 7

    // EEW forecast regions: 80-bit bitmask at [130..209]
    // region 1, 5, 10を設定
    TestDecoderEx::setBits(bits, 130, 1, 1);       // region 1
    TestDecoderEx::setBits(bits, 134, 1, 1);       // region 5
    TestDecoderEx::setBits(bits, 139, 1, 1);       // region 10

    // CRC計算とセット (IS-QZSS-L1S では226ビットをカバーし、24ビットのCRC)
    uint32_t crc = TestDecoderEx::calculateCRC(bits, 226);
    TestDecoderEx::setBits(bits, 226, 24, crc);

    // デコーダ呼び出し
    uint32_t now_unix = 1704067200u; // 2024-01-01 00:00:00
    msg.payload_type = MsgPayloadType::Mt43;
    msg.mt43.disaster_category = 1; // decodeEEWはカテゴリをセットしないため手動設定
    TestDecoderEx::testDecodeEEW(bits, msg, now_unix);

    // 結果の検証
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

// ── MT=44 DCX テストヘルパー ───────────────────────────────────────────────
// DCX メッセージ (MT=44) のビット列を構築し、デコードして結果を返す
static Message decodeDcxHelper(uint8_t* bits, uint32_t now_unix = 1704067200u) {
    // CRC計算とセット
    uint32_t crc = TestDecoderEx::calculateCRC(bits, 226);
    TestDecoderEx::setBits(bits, 226, 24, crc);

    // デコーダ呼び出し
    TestDecoderEx decoder;
    Message msg{};
    Frame frame{};
    memcpy(frame.bits, bits, 32);
    frame.svid = 193;
    decoder.decode(frame, msg, now_unix);
    return msg;
}

// ── DCX MT44 テスト ─────────────────────────────────────────────────────────

TEST_CASE("decodeDcx: L-Alert メッセージのデコード") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44 (0b101100)
    TestDecoderEx::setBits(bits, 0, 8, 0x53);       // preamble
    TestDecoderEx::setBits(bits, 8, 6, 44);         // msg_type = 44

    // SD: SDMT=0, SDM=0x1FF (全衛星 For Japan)
    TestDecoderEx::setBits(bits, 14, 1, 0);         // SDMT = 0
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);     // SDM = 全1

    // CAMF
    TestDecoderEx::setBits(bits, 24, 2, 1);         // A1 = 01 (Alert)
    TestDecoderEx::setBits(bits, 26, 9, 111);       // A2 = 111 (Japan)
    TestDecoderEx::setBits(bits, 35, 5, 1);         // A3 = 1 (FMMC/L-Alert)
    TestDecoderEx::setBits(bits, 40, 7, 10);        // A4 = 10 (Hazard)
    TestDecoderEx::setBits(bits, 47, 2, 3);         // A5 = 3 (Severity)
    TestDecoderEx::setBits(bits, 49, 1, 0);         // A6 = 0
    TestDecoderEx::setBits(bits, 50, 14, 7200);     // A7 = 7200 (minute of week)
    TestDecoderEx::setBits(bits, 64, 2, 2);         // A8 = 2 (Duration)
    TestDecoderEx::setBits(bits, 66, 1, 0);         // A9 = 0
    TestDecoderEx::setBits(bits, 67, 3, 1);         // A10 = 1
    TestDecoderEx::setBits(bits, 70, 10, 1);        // A11 = 1 (Guidance)
    // A12 = 45761 (latitude code for ~35.688°N - Tokyo area)
    // Formula: code = (lat + 90) * 65535 / 180 = (35.688 + 90) * 65535 / 180 ≈ 45761
    TestDecoderEx::setBits(bits, 80, 16, 45761);    // A12 = 45761 (lat)
    // A13 = 116395 (longitude code for ~139.691°E - Tokyo area)
    // Formula: code = (lon + 180) * 131071 / 360 = (139.691 + 180) * 131071 / 360 ≈ 116395
    TestDecoderEx::setBits(bits, 96, 17, 116395);   // A13 = 116395 (lon)
    TestDecoderEx::setBits(bits, 113, 5, 13);       // A14 = 13 (semi-major ~10.9km)
    TestDecoderEx::setBits(bits, 118, 5, 11);       // A15 = 11 (semi-minor ~6.0km)
    TestDecoderEx::setBits(bits, 123, 6, 48);       // A16 = 48 (azimuth ~45°)
    TestDecoderEx::setBits(bits, 129, 2, 0);        // A17 = 0
    TestDecoderEx::setBits(bits, 131, 15, 0);       // A18 = 0

    // Extended Message (L-Alert)
    TestDecoderEx::setBits(bits, 146, 16, 1100);    // EX1 = 1100 (札幌市)
    TestDecoderEx::setBits(bits, 162, 1, 0);        // EX2 = 0 (未使用)
    TestDecoderEx::setBits(bits, 163, 17, 0);       // EX3 = 0
    TestDecoderEx::setBits(bits, 180, 17, 0);       // EX4 = 0
    TestDecoderEx::setBits(bits, 197, 5, 0);        // EX5 = 0
    TestDecoderEx::setBits(bits, 202, 5, 0);        // EX6 = 0
    TestDecoderEx::setBits(bits, 207, 7, 0);        // EX7 = 0
    TestDecoderEx::setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::LAlertOrLocal);
    CHECK(msg.mt44.sd.sdmt == 0);
    CHECK(msg.mt44.sd.sdm == 0x1FF);
    CHECK(msg.mt44.camf.a1 == 1);        // Alert
    CHECK(msg.mt44.camf.a2 == 111);      // Japan
    CHECK(msg.mt44.camf.a3 == 1);        // FMMC
    CHECK(msg.mt44.camf.a4 == 10);       // Hazard
    CHECK(msg.mt44.camf.a5 == 3);        // Severity
    CHECK(msg.mt44.camf.a11 == 1);       // Guidance
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1100);  // 札幌市
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

TEST_CASE("decodeDcx: J-Alert メッセージのデコード") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44
    TestDecoderEx::setBits(bits, 0, 8, 0x53);
    TestDecoderEx::setBits(bits, 8, 6, 44);

    // SD
    TestDecoderEx::setBits(bits, 14, 1, 0);
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);

    // CAMF
    TestDecoderEx::setBits(bits, 24, 2, 1);         // A1 = Alert
    TestDecoderEx::setBits(bits, 26, 9, 111);       // A2 = Japan
    TestDecoderEx::setBits(bits, 35, 5, 2);         // A3 = 2 (FDMA/J-Alert)
    TestDecoderEx::setBits(bits, 40, 7, 5);         // A4 = 5
    TestDecoderEx::setBits(bits, 47, 2, 3);         // A5 = 3
    TestDecoderEx::setBits(bits, 49, 1, 0);         // A6 = 0
    TestDecoderEx::setBits(bits, 50, 14, 0);        // A7 = 0
    TestDecoderEx::setBits(bits, 64, 2, 0);         // A8 = 0
    TestDecoderEx::setBits(bits, 66, 1, 0);         // A9 = 0
    TestDecoderEx::setBits(bits, 67, 3, 0);         // A10 = 0
    TestDecoderEx::setBits(bits, 70, 10, 0);        // A11 = 0
    TestDecoderEx::setBits(bits, 80, 16, 0);        // A12 = 0 (未使用)
    TestDecoderEx::setBits(bits, 96, 17, 0);        // A13 = 0
    TestDecoderEx::setBits(bits, 113, 5, 0);        // A14 = 0
    TestDecoderEx::setBits(bits, 118, 5, 0);        // A15 = 0
    TestDecoderEx::setBits(bits, 123, 6, 0);        // A16 = 0
    TestDecoderEx::setBits(bits, 129, 2, 0);        // A17 = 0
    TestDecoderEx::setBits(bits, 131, 15, 0);       // A18 = 0

    // Extended Message (J-Alert)
    // EX8 = 0 (prefecture code), EX9 = 都道府県ビットマスク
    TestDecoderEx::setBits(bits, 146, 1, 0);        // EX8 = 0 (prefecture)
    // EX9: 北海道(bit0)と青森(bit1)を設定 = 0b11 = 3
    TestDecoderEx::setBits(bits, 147, 32, 0);       // EX9 hi = 0
    TestDecoderEx::setBits(bits, 179, 32, 3);       // EX9 lo = 3 (Hokkaido + Aomori)
    TestDecoderEx::setBits(bits, 211, 3, 0);        // EX10 = 0 (reserved)
    TestDecoderEx::setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::JAlert);
    CHECK(msg.mt44.camf.a2 == 111);      // Japan
    CHECK(msg.mt44.camf.a3 == 2);        // FDMA
    CHECK(msg.mt44.ex_jalert.ex8 == 0);  // prefecture code
    CHECK(msg.mt44.ex_jalert.ex9 == 3);  // Hokkaido + Aomori
    CHECK(msg.mt44.ex_jalert.vn == 1);
}

TEST_CASE("decodeDcx: Local Government メッセージのデコード") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44
    TestDecoderEx::setBits(bits, 0, 8, 0x53);
    TestDecoderEx::setBits(bits, 8, 6, 44);

    // SD
    TestDecoderEx::setBits(bits, 14, 1, 0);
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);

    // CAMF
    TestDecoderEx::setBits(bits, 24, 2, 1);         // A1 = Alert
    TestDecoderEx::setBits(bits, 26, 9, 111);       // A2 = Japan
    TestDecoderEx::setBits(bits, 35, 5, 4);         // A3 = 4 (Local Government)
    TestDecoderEx::setBits(bits, 40, 7, 10);        // A4 = 10
    TestDecoderEx::setBits(bits, 47, 2, 3);         // A5 = 3
    TestDecoderEx::setBits(bits, 49, 1, 0);         // A6 = 0
    TestDecoderEx::setBits(bits, 50, 14, 7200);     // A7 = 7200
    TestDecoderEx::setBits(bits, 64, 2, 2);         // A8 = 2
    TestDecoderEx::setBits(bits, 66, 1, 0);         // A9 = 0
    TestDecoderEx::setBits(bits, 67, 3, 1);         // A10 = 1
    TestDecoderEx::setBits(bits, 70, 10, 1);        // A11 = 1
    // Main ellipse: Tokyo area coordinates
    TestDecoderEx::setBits(bits, 80, 16, 45761);    // A12 = 45761 (lat ~35.688°N)
    TestDecoderEx::setBits(bits, 96, 17, 116395);   // A13 = 116395 (lon ~139.691°E)
    TestDecoderEx::setBits(bits, 113, 5, 13);       // A14 = 13 (semi-major ~10.9km)
    TestDecoderEx::setBits(bits, 118, 5, 11);       // A15 = 11 (semi-minor ~6.0km)
    TestDecoderEx::setBits(bits, 123, 6, 48);       // A16 = 48 (azimuth ~45°)
    TestDecoderEx::setBits(bits, 129, 2, 0);        // A17 = 0
    TestDecoderEx::setBits(bits, 131, 15, 0);       // A18 = 0

    // Extended Message (Local Government with Additional Ellipse)
    TestDecoderEx::setBits(bits, 146, 16, 1100);    // EX1 = 1100 (札幌市)
    TestDecoderEx::setBits(bits, 162, 1, 1);        // EX2 = 1 (Head to area)
    // Additional ellipse: slightly offset from main ellipse
    // EX3 = 91522 (latitude code for ~35.687°N, 17bit precision)
    // Formula: code = (lat + 90) * 131071 / 180 = (35.687 + 90) * 131071 / 180 ≈ 91522
    TestDecoderEx::setBits(bits, 163, 17, 91522);   // EX3 = 91522 (lat)
    // EX4 = 68950 (longitude code for ~139.689°E, 17bit precision, range 45-225°)
    // Formula: code = (lon - 45) * 131071 / 180 = (139.689 - 45) * 131071 / 180 ≈ 68950
    TestDecoderEx::setBits(bits, 180, 17, 68950);   // EX4 = 68950 (lon)
    TestDecoderEx::setBits(bits, 197, 5, 13);       // EX5 = 13 (semi-major ~10.9km)
    TestDecoderEx::setBits(bits, 202, 5, 11);       // EX6 = 11 (semi-minor ~6.0km)
    // EX7 = 96 (azimuth code for ~45°, 7bit precision)
    // Formula: code = (azimuth + 90) * 128 / 180 = (45 + 90) * 128 / 180 = 96
    TestDecoderEx::setBits(bits, 207, 7, 96);       // EX7 = 96 (azimuth ~45°)
    TestDecoderEx::setBits(bits, 214, 6, 1);        // Vn = 1

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LocalGovernment);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::LAlertOrLocal);
    CHECK(msg.mt44.camf.a3 == 4);        // Local Government
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1100);
    CHECK(msg.mt44.ex_lalert_local.ex2 == 1);    // Head to area
    CHECK(msg.mt44.ex_lalert_local.ex3 == 91522);
    CHECK(msg.mt44.ex_lalert_local.ex4 == 68950);
    CHECK(msg.mt44.ex_lalert_local.ex5 == 13);
    CHECK(msg.mt44.ex_lalert_local.ex6 == 11);
    CHECK(msg.mt44.ex_lalert_local.ex7 == 96);
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

TEST_CASE("decodeDcx: Outside Japan メッセージのデコード") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44
    TestDecoderEx::setBits(bits, 0, 8, 0x53);
    TestDecoderEx::setBits(bits, 8, 6, 44);

    // SD
    TestDecoderEx::setBits(bits, 14, 1, 0);
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);

    // CAMF - Australia (A2 = 32)
    TestDecoderEx::setBits(bits, 24, 2, 1);         // A1 = Alert
    TestDecoderEx::setBits(bits, 26, 9, 32);        // A2 = 32 (Australia)
    TestDecoderEx::setBits(bits, 35, 5, 1);         // A3 = 1
    TestDecoderEx::setBits(bits, 40, 7, 10);        // A4 = 10
    TestDecoderEx::setBits(bits, 47, 2, 3);         // A5 = 3
    TestDecoderEx::setBits(bits, 49, 1, 0);         // A6 = 0
    TestDecoderEx::setBits(bits, 50, 14, 0);        // A7 = 0
    TestDecoderEx::setBits(bits, 64, 2, 0);         // A8 = 0
    TestDecoderEx::setBits(bits, 66, 1, 0);         // A9 = 0
    TestDecoderEx::setBits(bits, 67, 3, 0);         // A10 = 0
    TestDecoderEx::setBits(bits, 70, 10, 0);        // A11 = 0
    TestDecoderEx::setBits(bits, 80, 16, 0);        // A12 = 0
    TestDecoderEx::setBits(bits, 96, 17, 0);        // A13 = 0
    TestDecoderEx::setBits(bits, 113, 5, 0);        // A14 = 0
    TestDecoderEx::setBits(bits, 118, 5, 0);        // A15 = 0
    TestDecoderEx::setBits(bits, 123, 6, 0);        // A16 = 0
    TestDecoderEx::setBits(bits, 129, 2, 0);        // A17 = 0
    TestDecoderEx::setBits(bits, 131, 15, 0);       // A18 = 0

    // Extended Message (Outside Japan - EX11 raw)
    // EX11 = 68bit raw data
    for (int i = 0; i < 8; ++i) {
        TestDecoderEx::setBits(bits, 146 + i * 8, 8, 0xAB);  // raw data
    }
    TestDecoderEx::setBits(bits, 210, 4, 0xF);      // remaining 4 bits
    TestDecoderEx::setBits(bits, 214, 6, 5);        // Vn = 5 (outside Japan は可変)

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.is_null_message == false);
    CHECK(msg.mt44.ex_kind == ExtendedKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 32);       // Australia
    CHECK(msg.mt44.ex_outside.vn == 5);
    // EX11 raw data の検証
    for (int i = 0; i < 8; ++i) {
        CHECK(msg.mt44.ex_outside.ex11_raw[i] == 0xAB);
    }
    // 9バイト目の上位4ビットを検証（0xF0）
    CHECK((msg.mt44.ex_outside.ex11_raw[8] & 0xF0) == 0xF0);
}


TEST_CASE("decodeDcx: NULL Message のデコード") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44
    TestDecoderEx::setBits(bits, 0, 8, 0x53);
    TestDecoderEx::setBits(bits, 8, 6, 44);

    // SD (正常な値)
    TestDecoderEx::setBits(bits, 14, 1, 0);
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);

    // CAMF - NULL Message パターン
    TestDecoderEx::setBits(bits, 24, 2, 0);         // A1 = 0
    TestDecoderEx::setBits(bits, 26, 9, 111);       // A2 = Japan
    TestDecoderEx::setBits(bits, 35, 5, 0);         // A3 = 0
    TestDecoderEx::setBits(bits, 40, 7, 0);         // A4 = 0
    TestDecoderEx::setBits(bits, 47, 2, 0);         // A5 = 0
    TestDecoderEx::setBits(bits, 49, 1, 0);         // A6 = 0
    TestDecoderEx::setBits(bits, 50, 14, 0);        // A7 = 0
    TestDecoderEx::setBits(bits, 64, 2, 0);         // A8 = 0
    TestDecoderEx::setBits(bits, 66, 1, 0);         // A9 = 0
    TestDecoderEx::setBits(bits, 67, 3, 0);         // A10 = 0
    TestDecoderEx::setBits(bits, 70, 10, 0);        // A11 = 0
    TestDecoderEx::setBits(bits, 80, 16, 0);        // A12 = 0
    TestDecoderEx::setBits(bits, 96, 17, 0);        // A13 = 0
    TestDecoderEx::setBits(bits, 113, 5, 0);        // A14 = 0
    TestDecoderEx::setBits(bits, 118, 5, 0);        // A15 = 0
    TestDecoderEx::setBits(bits, 123, 6, 0);        // A16 = 0
    TestDecoderEx::setBits(bits, 129, 2, 0);        // A17 = 0
    TestDecoderEx::setBits(bits, 131, 15, 0);       // A18 = 0

    // Extended Message = all 0
    // (bits 146..219 は既に 0)

    Message msg = decodeDcxHelper(bits);

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

TEST_CASE("decodeDcx: 未知の A3 値は破棄されるが SD は維持される") {
    uint8_t bits[32] = {};

    // PAB=0x53, MT=44
    TestDecoderEx::setBits(bits, 0, 8, 0x53);
    TestDecoderEx::setBits(bits, 8, 6, 44);

    // SD
    TestDecoderEx::setBits(bits, 14, 1, 0);
    TestDecoderEx::setBits(bits, 15, 9, 0x1FF);

    // CAMF - 未知の A3 = 5
    TestDecoderEx::setBits(bits, 24, 2, 1);         // A1 = Alert
    TestDecoderEx::setBits(bits, 26, 9, 111);       // A2 = Japan
    TestDecoderEx::setBits(bits, 35, 5, 5);         // A3 = 5 (未知)
    TestDecoderEx::setBits(bits, 40, 7, 10);        // A4 = 10
    TestDecoderEx::setBits(bits, 47, 2, 3);         // A5 = 3
    // 残りは 0

    Message msg = decodeDcxHelper(bits);

    // IS-QZSS-DCX-003 §5.7: 未知の A3 は本文破棄となるが SD は処理されるため valid=true
    CHECK(msg.valid == true);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::Unknown);
    CHECK(msg.mt44.sd.sdmt == 0);
    CHECK(msg.mt44.sd.sdm == 0x1FF);
}



TEST_CASE("decodeHypocenter: 震源情報のデコード") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A\r\n";
    internal::NmeaFramer framer;
    internal::Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) { found = true; break; }
    }
    REQUIRE(found == true);

    internal::Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 2);
    CHECK(msg.mt43.hypo.depth == 40);
    CHECK(msg.mt43.hypo.magnitude == 64);
    CHECK(msg.mt43.hypo.epicenter == 791);
    CHECK(msg.mt43.hypo.quake_time.day == 7);
    CHECK(msg.mt43.hypo.quake_time.hour == 4);
    CHECK(msg.mt43.hypo.quake_time.minute == 5);
}
TEST_CASE("decodeTsunami: 津波情報のデコード") {
    Message msg{};
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F\r\n";
    internal::NmeaFramer framer;
    internal::Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) { found = true; break; }
    }
    REQUIRE(found == true);

    internal::Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 5);
    CHECK(msg.mt43.tsunami.warning_code == 3);
    REQUIRE(msg.mt43.tsunami.count >= 3);
    // Actual decoded values from the test vector
    CHECK(msg.mt43.tsunami.entries[0].height_code == 4);
    CHECK(msg.mt43.tsunami.entries[1].height_code == 4);
    CHECK(msg.mt43.tsunami.entries[2].height_code == 4);
    CHECK(msg.mt43.tsunami.entries[0].region_code == 65);
    CHECK(msg.mt43.tsunami.entries[1].region_code == 65);
    CHECK(msg.mt43.tsunami.entries[2].region_code == 65);
}
TEST_CASE("decodeVolcano: 火山情報のデコード") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70\r\n";
    internal::NmeaFramer framer;
    internal::Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) { found = true; break; }
    }
    REQUIRE(found == true);

    internal::Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));

    CHECK(msg.valid == true);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 8);
    CHECK(msg.mt43.vol.warning_code == 52);
    CHECK(msg.mt43.vol.volcano_name == 503);
}

// ── decodePrefectureBitmask 単体テスト ───────────────────────────────────────

TEST_CASE("decodePrefectureBitmask: 仕様書例（北海道・青森・岩手）") {
    // IS-QZSS-DCX-003 §4.2.4.2.2 の例: 0b111 → Hokkaido, Aomori, Iwate
    // 47-bit integer = 7, EX9 64-bit = 7 << 17 = 0x000E0000
    uint64_t ex9 = (uint64_t)7 << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 3);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[1] == 2);   // 青森県
    CHECK(positions[2] == 3);   // 岩手県
}

TEST_CASE("decodePrefectureBitmask: 沖縄のみ（MSB）") {
    // Okinawa = bit 46 of 47-bit integer = ex9 bit 63
    uint64_t ex9 = (uint64_t)1 << 63;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 47);  // 沖縄県
}

TEST_CASE("decodePrefectureBitmask: 全都道府県（全ビット=1）") {
    // All 47 bits set: 47-bit all-ones = (1ULL<<47)-1, shifted to ex9[63:17]
    uint64_t ex9 = ((1ULL << 47) - 1) << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 47);
    CHECK(positions[0] == 1);   // 北海道
    CHECK(positions[46] == 47); // 沖縄県
}

TEST_CASE("decodePrefectureBitmask: 空（ゼロ）") {
    uint64_t ex9 = 0;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}

TEST_CASE("decodePrefectureBitmask: ビット17だけ設定（北海道）") {
    // ex9 bit 17 = 47-bit integer bit 0 = Hokkaido
    uint64_t ex9 = (uint64_t)1 << 17;
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 1);
    CHECK(positions[0] == 1);  // 北海道
}

TEST_CASE("decodePrefectureBitmask: reservedビットは無視される") {
    // ex9 bits [16:0] は reserved で、prefecture として検出されない
    uint64_t ex9 = (uint64_t)0xFFFF;  // bits [16:0] = all 1s
    uint8_t positions[47] = {};
    uint8_t count = azaraC::internal::decodePrefectureBitmask(ex9, positions);

    CHECK(count == 0);
}
