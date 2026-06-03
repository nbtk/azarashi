// test/test_coverage.cpp — エッジケース・境界値テスト
// 単体テスト的な詳細検証は test_decoder.cpp に任せ、ここでは境界値・エラーケースに特化

#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

// ═══════════════════════════════════════════════════════════════════════════════
// エッジケーステスト
// ═══════════════════════════════════════════════════════════════════════════════

// ── 不正なMT値の拒否 ──────────────────────────────────────────────────────────

TEST_CASE("Edge Case: 不正なMT=42の拒否") {
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

TEST_CASE("Edge Case: 不正なMT=45の拒否") {
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

// ── バージョン番号の検証 ──────────────────────────────────────────────────────

TEST_CASE("Edge Case: バージョン0の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 0);     // version = 0
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: バージョン2の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 2);     // version = 2
    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

// ── プリアンブルの検証 ────────────────────────────────────────────────────────

TEST_CASE("Edge Case: 不正なプリアンブル0x00の拒否") {
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

TEST_CASE("Edge Case: プリアンブル0x53は許可") {
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

TEST_CASE("Edge Case: プリアンブル0x9Aは許可") {
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

TEST_CASE("Edge Case: プリアンブル0xC6は許可") {
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

// ── NMEAフレーマーのエッジケース ──────────────────────────────────────────────

TEST_CASE("Edge Case: NMEA 62文字の拒否") {
    char nmea[256];
    strcpy(nmea, "$QZQSM,55,");
    for (int i = 0; i < 62; i++) sprintf(nmea + strlen(nmea), "%X", i % 16);
    uint8_t xsum = 0;
    for (size_t i = 1; i < strlen(nmea); i++) xsum ^= (uint8_t)nmea[i];
    sprintf(nmea + strlen(nmea), "*%02X\r\n", xsum);
    Message msg{};
    CHECK_FALSE(decodeNmea(nmea, msg));
}

TEST_CASE("Edge Case: NMEA 63文字の受け入れ（正常ペイロード長）") {
    // 63文字 = 31バイト×2 + 1ニブル = IS-QZSS-L1S の正規ペイロード長
    // ペイロードの内容はゼロ埋め（CRCは通らないが、フレーマーが受け入れることを確認）
    // 実際の正常デコードは test_azarashi.cpp の実NMEAデータでカバー済み
    const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\r\n";
    // ペイロード部 = "53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908"
    // 長さ確認: 63文字
    const char* payload_start = nmea + 10; // "$QZQSM,55," の後
    size_t payload_len = 0;
    while (payload_start[payload_len] != '*') payload_len++;
    CHECK(payload_len == 63); // NMEAフレーマーが受け入れる正規ペイロード長

    Message msg{};
    // この電文は実際にデコード成功するはず（test_azarashi.cpp でも使用）
    bool ok = decodeNmea(nmea, msg);
    CHECK(ok == true);
    CHECK(msg.valid == true);
    CHECK(msg.msg_type == 43);
}

TEST_CASE("Edge Case: NMEA 64文字の拒否") {
    char nmea[256];
    strcpy(nmea, "$QZQSM,55,");
    for (int i = 0; i < 64; i++) sprintf(nmea + strlen(nmea), "%X", i % 16);
    uint8_t xsum = 0;
    for (size_t i = 1; i < strlen(nmea); i++) xsum ^= (uint8_t)nmea[i];
    sprintf(nmea + strlen(nmea), "*%02X\r\n", xsum);
    Message msg{};
    CHECK_FALSE(decodeNmea(nmea, msg));
}

// ── 津波到着時間の境界値 ──────────────────────────────────────────────────────

TEST_CASE("Edge Case: 津波到着時間の不明値 (hour=31, min=63)") {
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 5);   // Tsunami
    setBits(bits, 214, 6, 1);

    // report_time: month=4, day=25, hour=13, min=0
    setBits(bits, 21, 4, 4);
    setBits(bits, 25, 5, 25);
    setBits(bits, 30, 5, 13);
    setBits(bits, 35, 6, 0);

    setBits(bits, 80, 4, 3);   // warning_code

    // entry 1: region=1, height=2, arrival: hour=31, min=63 (不明)
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

// ── うるう年の処理 ─────────────────────────────────────────────────────────────

TEST_CASE("Edge Case: うるう年2月29日の処理") {
    uint32_t now = 1709164800u; // 2024-02-29 00:00:00 UTC
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    setBits(bits, 21, 4, 2);   // month=2
    setBits(bits, 25, 5, 29);  // day=29
    setBits(bits, 30, 5, 0);
    setBits(bits, 35, 6, 0);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, now));
    CHECK(msg.mt43.event_time.day == 29);
}

// ── 年末年始の日付遷移 ────────────────────────────────────────────────────────

TEST_CASE("Edge Case: 年末年始の日付遷移") {
    uint32_t now = 1735686000u; // 2024-12-31 23:00:00 UTC
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);
    setBits(bits, 8, 6, 43);
    setBits(bits, 17, 4, 1);
    setBits(bits, 214, 6, 1);
    setBits(bits, 21, 4, 12);  // month=12
    setBits(bits, 25, 5, 31);  // day=31
    setBits(bits, 30, 5, 23);
    setBits(bits, 35, 6, 0);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, now));
    CHECK(msg.mt43.event_time.day == 31);
}

// ── 深さ・マグニチュードの境界値 ──────────────────────────────────────────────

TEST_CASE("Edge Case: 深さ501km以上 (コード501)") {
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

TEST_CASE("Edge Case: 深さ511 (不明)") {
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

TEST_CASE("Edge Case: マグニチュード126 (8.0以上不明)") {
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

TEST_CASE("Edge Case: マグニチュード127 (不明)") {
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
