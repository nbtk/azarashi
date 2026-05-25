// test/test_coverage.cpp — 不足しているテストケースの追加
// 仕様書(IS-QZSS-DCR-016/IS-QZSS-DCX-003)およびazarashiからのテストデータ

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// ── ヘルパー ──────────────────────────────────────────────────────────────────

static bool decode_nmea(const char* nmea, Message& msg) {
    internal::NmeaFramer framer;
    internal::Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) { found = true; break; }
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

// テスト用にprotected関数を公開
struct TestDecoderEx : Decoder {
    static void testDecodeNankai(const uint8_t* bits, Message& out) {
        TestDecoderEx t; t.decodeNankai(bits, out);
    }
    static void testDecodeAshFall(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoderEx t; t.decodeAshFall(bits, out, now);
    }
    static void testDecodeFlood(const uint8_t* bits, Message& out) {
        TestDecoderEx t; t.decodeFlood(bits, out);
    }
    static void testDecodeWeather(const uint8_t* bits, Message& out) {
        TestDecoderEx t; t.decodeWeather(bits, out);
    }
    static void testDecodeSeismic(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoderEx t; t.decodeSeismic(bits, out, now);
    }
    static void testDecodeVolcano(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoderEx t; t.decodeVolcano(bits, out, now);
    }
    static void testDecodeTsunami(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoderEx t; t.decodeTsunami(bits, out, now);
    }
    static void testDecodeNwPacTsu(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoderEx t; t.decodeNwPacTsu(bits, out, now);
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// MT=43 サブデコーダーの詳細テスト
// ═══════════════════════════════════════════════════════════════════════════════

// ── Nankai Trough Earthquake (DC=4) ───────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.5
// [53..56] info_code(4), [57..200] text(18bytes), [201..206] page(6), [207..212] total_page(6)

TEST_CASE("decodeNankai: 南海トラフ地震の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 4);
    setbits(bits, 214, 6, 1);

    setbits(bits, 53, 4, 1);       // info_code = 1
    setbits(bits, 57, 8, 'T');     // text[0]
    setbits(bits, 65, 8, 'e');     // text[1]
    setbits(bits, 73, 8, 's');     // text[2]
    setbits(bits, 81, 8, 't');     // text[3]
    setbits(bits, 201, 6, 2);      // page = 2
    setbits(bits, 207, 6, 3);      // total_page = 3

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeNankai(bits, msg);

    CHECK(msg.mt43.nankai_info_code == 1);
    CHECK(msg.mt43.nankai_page == 2);
    CHECK(msg.mt43.nankai_total_page == 3);
    CHECK(msg.mt43.nankai_text[0] == 'T');
    CHECK(msg.mt43.nankai_text[1] == 'e');
    CHECK(msg.mt43.nankai_text[2] == 's');
    CHECK(msg.mt43.nankai_text[3] == 't');
}

TEST_CASE("decodeNankai: 最終ページの判定") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 4);
    CHECK(msg.mt43.nankai_page != msg.mt43.nankai_total_page);
}

// ── Ash Fall (DC=9) ───────────────────────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.9
// [53..68] activity_time(16), [69..70] warning_type(2), [71..82] volcano_name(12)
// entries: [83..] ×4: time(3)+code(3)+local_gov(23)=29bit each

TEST_CASE("decodeAshFall: 降灰予報の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 9);
    setbits(bits, 214, 6, 1);

    // activity_time: day=15, hour=10, minute=30
    setbits(bits, 53, 5, 15);
    setbits(bits, 58, 5, 10);
    setbits(bits, 63, 6, 30);

    setbits(bits, 69, 2, 1);       // warning_type = 1 (速報)
    setbits(bits, 71, 12, 503);    // volcano_name = 503 (桜島)

    // entry 1: time=3, code=2, local_gov=1100000
    setbits(bits, 83, 3, 3);
    setbits(bits, 86, 3, 2);
    setbits(bits, 89, 23, 1100000);

    // entry 2: time=6, code=5, local_gov=1200000
    setbits(bits, 112, 3, 6);
    setbits(bits, 115, 3, 5);
    setbits(bits, 118, 23, 1200000);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeAshFall(bits, msg, 1704067200u);

    CHECK(msg.mt43.ash_warning_type == 1);
    CHECK(msg.mt43.ash_volcano_name == 503);
    CHECK(msg.mt43.ash_activity_time.day == 15);
    CHECK(msg.mt43.ash_activity_time.hour == 10);
    CHECK(msg.mt43.ash_activity_time.minute == 30);
    CHECK(msg.mt43.ash_count == 2);
    CHECK(msg.mt43.ash_entries_time[0] == 3);
    CHECK(msg.mt43.ash_entries_code[0] == 2);
    CHECK(msg.mt43.ash_entries_lg[0] == 1100000);
    CHECK(msg.mt43.ash_entries_time[1] == 6);
    CHECK(msg.mt43.ash_entries_code[1] == 5);
    CHECK(msg.mt43.ash_entries_lg[1] == 1200000);
}

// ── Flood (DC=11) ──────────────────────────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.11
// entries: [53..] ×3: warning_level(4)+region_code(40)=44bit each
// entry1: [53..96], entry2: [97..140], entry3: [141..184]

TEST_CASE("decodeFlood: 洪水予報の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 11);
    setbits(bits, 214, 6, 1);

    // entry 1: [53..96] warning_level=3, region_code=1234567 (40bit)
    setbits(bits, 53, 4, 3);           // warning_level
    uint64_t region1 = 1234567ULL;
    setbits(bits, 57, 20, (uint32_t)(region1 >> 20));  // hi 20bit
    setbits(bits, 77, 20, (uint32_t)(region1 & 0xFFFFF)); // lo 20bit

    // entry 2: [97..140] warning_level=4, region_code=890
    setbits(bits, 97, 4, 4);           // warning_level
    uint64_t region2 = 890ULL;
    setbits(bits, 101, 20, (uint32_t)(region2 >> 20));
    setbits(bits, 121, 20, (uint32_t)(region2 & 0xFFFFF));

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeFlood(bits, msg);

    CHECK(msg.mt43.flood_count == 2);
    CHECK(msg.mt43.flood_entries[0].warning_level == 3);
    CHECK(msg.mt43.flood_entries[0].region_code == 1234567ULL);
    CHECK(msg.mt43.flood_entries[1].warning_level == 4);
    CHECK(msg.mt43.flood_entries[1].region_code == 890ULL);
}

TEST_CASE("decodeFlood: 警報解除のデコード") {
    Message msg{};
    const char* nmea = "$QZQSM,58,C6AFD99CB90000E0A8F5528600000000000000000000000000000013A699D5C*76\r\n";
    REQUIRE(decode_nmea(nmea, msg));
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 11);
}

// ── Weather (DC=10) ────────────────────────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.10
// [53..55] warning_state(3), entries: [56..] ×6: sub_category(5)+region_code(19)=24bit

TEST_CASE("decodeWeather: 気象警報の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 10);
    setbits(bits, 214, 6, 1);

    setbits(bits, 53, 3, 1);       // warning_state = 1 (発表)

    // entry 1: [56..79] sub_category=2, region_code=11000
    setbits(bits, 56, 5, 2);
    setbits(bits, 61, 19, 11000);

    // entry 2: [80..103] sub_category=3, region_code=12000
    setbits(bits, 80, 5, 3);
    setbits(bits, 85, 19, 12000);

    // entry 3: [104..127] sub_category=7, region_code=13000
    setbits(bits, 104, 5, 7);
    setbits(bits, 109, 19, 13000);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeWeather(bits, msg);

    CHECK(msg.mt43.wx_warning_state == 1);
    CHECK(msg.mt43.wx_count == 3);
    CHECK(msg.mt43.wx_entries[0].sub_category == 2);
    CHECK(msg.mt43.wx_entries[0].region_code == 11000);
    CHECK(msg.mt43.wx_entries[1].sub_category == 3);
    CHECK(msg.mt43.wx_entries[1].region_code == 12000);
    CHECK(msg.mt43.wx_entries[2].sub_category == 7);
    CHECK(msg.mt43.wx_entries[2].region_code == 13000);
}

// ── Seismic Intensity (DC=3) ───────────────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.4
// [53..68] quake_time(16), entries: [69..] ×16: intensity_code(3)+prefecture_code(6)=9bit

TEST_CASE("decodeSeismic: 震度情報の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 3);
    setbits(bits, 214, 6, 1);

    // quake_time: day=20, hour=15, minute=45 at [53..68]
    setbits(bits, 53, 5, 20);
    setbits(bits, 58, 5, 15);
    setbits(bits, 63, 6, 45);

    // entry 1: [69..77] intensity=4, prefecture=13
    setbits(bits, 69, 3, 4);
    setbits(bits, 72, 6, 13);

    // entry 2: [78..86] intensity=3, prefecture=14
    setbits(bits, 78, 3, 3);
    setbits(bits, 81, 6, 14);

    // entry 3: [87..95] intensity=2, prefecture=11
    setbits(bits, 87, 3, 2);
    setbits(bits, 90, 6, 11);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeSeismic(bits, msg, 1704067200u);

    CHECK(msg.mt43.seis_quake_time.day == 20);
    CHECK(msg.mt43.seis_quake_time.hour == 15);
    CHECK(msg.mt43.seis_quake_time.minute == 45);
    CHECK(msg.mt43.seis_count == 3);
    CHECK(msg.mt43.seis_entries[0].intensity_code == 4);
    CHECK(msg.mt43.seis_entries[0].prefecture_code == 13);
    CHECK(msg.mt43.seis_entries[1].intensity_code == 3);
    CHECK(msg.mt43.seis_entries[1].prefecture_code == 14);
    CHECK(msg.mt43.seis_entries[2].intensity_code == 2);
    CHECK(msg.mt43.seis_entries[2].prefecture_code == 11);
}

// ── Volcano (DC=8) ─────────────────────────────────────────────────────────────
// IS-QZSS-DCR-016 §4.1.2.3.8
// [50..52] ambiguity(3), [53..68] activity_time(16), [69..75] warning_code(7)
// [76..87] volcano_name(12), [88..] ×5: local_gov(23)

TEST_CASE("decodeVolcano: 火山情報の詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 8);
    setbits(bits, 214, 6, 1);

    setbits(bits, 50, 3, 0);       // ambiguity = 0
    setbits(bits, 53, 5, 10);      // day=10
    setbits(bits, 58, 5, 8);       // hour=8
    setbits(bits, 63, 6, 0);       // minute=0
    setbits(bits, 69, 7, 52);      // warning_code = 52
    setbits(bits, 76, 12, 503);    // volcano_name = 503 (桜島)
    setbits(bits, 88, 23, 4600000); // local_gov 1

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeVolcano(bits, msg, 1704067200u);

    CHECK(msg.mt43.vol_ambiguity == 0);
    CHECK(msg.mt43.vol_activity_time.day == 10);
    CHECK(msg.mt43.vol_activity_time.hour == 8);
    CHECK(msg.mt43.vol_activity_time.minute == 0);
    CHECK(msg.mt43.vol_warning_code == 52);
    CHECK(msg.mt43.vol_volcano_name == 503);
    CHECK(msg.mt43.vol_lg_count == 1);
    CHECK(msg.mt43.vol_local_govs[0] == 4600000);
}

// ═══════════════════════════════════════════════════════════════════════════════
// エッジケーステスト
// ═══════════════════════════════════════════════════════════════════════════════

// ── 不正なMT値の拒否 ──────────────────────────────────────────────────────────

TEST_CASE("Edge Case: 不正なMT=42の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 42);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: 不正なMT=45の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 45);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

// ── バージョン番号の検証 ──────────────────────────────────────────────────────

TEST_CASE("Edge Case: バージョン0の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 0);     // version = 0
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: バージョン2の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 2);     // version = 2
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

// ── 不正なプリアンブルの拒否 ──────────────────────────────────────────────────

TEST_CASE("Edge Case: 不正なプリアンブル0x00の拒否") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x00);
    setbits(bits, 8, 6, 43);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK_FALSE(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: プリアンブル0x53は許可") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: プリアンブル0x9Aは許可") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x9A);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, 0));
}

TEST_CASE("Edge Case: プリアンブル0xC6は許可") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0xC6);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 1);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
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
    CHECK_FALSE(decode_nmea(nmea, msg));
}

TEST_CASE("Edge Case: NMEA 64文字の拒否") {
    char nmea[256];
    strcpy(nmea, "$QZQSM,55,");
    for (int i = 0; i < 64; i++) sprintf(nmea + strlen(nmea), "%X", i % 16);
    uint8_t xsum = 0;
    for (size_t i = 1; i < strlen(nmea); i++) xsum ^= (uint8_t)nmea[i];
    sprintf(nmea + strlen(nmea), "*%02X\r\n", xsum);
    Message msg{};
    CHECK_FALSE(decode_nmea(nmea, msg));
}

// ── 津波到着時間の境界値 ──────────────────────────────────────────────────────

TEST_CASE("Edge Case: 津波到着時間の不明値 (hour=31, min=63)") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 5);   // Tsunami
    setbits(bits, 214, 6, 1);

    // report_time: month=4, day=25, hour=13, min=0
    setbits(bits, 21, 4, 4);
    setbits(bits, 25, 5, 25);
    setbits(bits, 30, 5, 13);
    setbits(bits, 35, 6, 0);

    setbits(bits, 80, 4, 3);   // warning_code

    // entry 1: region=1, height=2, arrival: hour=31, min=63 (不明)
    setbits(bits, 84, 10, 1);
    setbits(bits, 94, 4, 2);
    // raw = (0 << 11) | (31 << 6) | 63 = 0x1F3F
    setbits(bits, 98, 12, (0u << 11) | (31u << 6) | 63u);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    TestDecoderEx::testDecodeTsunami(bits, msg, 1777122000u);

    CHECK(msg.mt43.tsunami_count >= 1);
    if (msg.mt43.tsunami_count >= 1) {
        // hour=31, min=63 は無効なので arrival_time はゼロ
        CHECK(msg.mt43.tsunamis[0].arrival_time.hour == 0);
        CHECK(msg.mt43.tsunamis[0].arrival_time.minute == 0);
        CHECK(msg.mt43.tsunamis[0].arrival_time.unix_time == 0);
    }
}

// ── うるう年の処理 ─────────────────────────────────────────────────────────────

TEST_CASE("Edge Case: うるう年2月29日の処理") {
    uint32_t now = 1709164800u; // 2024-02-29 00:00:00 UTC
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 1);
    setbits(bits, 21, 4, 2);   // month=2
    setbits(bits, 25, 5, 29);  // day=29
    setbits(bits, 30, 5, 0);
    setbits(bits, 35, 6, 0);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
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

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 1);
    setbits(bits, 214, 6, 1);
    setbits(bits, 21, 4, 12);  // month=12
    setbits(bits, 25, 5, 31);  // day=31
    setbits(bits, 30, 5, 23);
    setbits(bits, 35, 6, 0);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    CHECK(dec.decode(frame, msg, now));
    CHECK(msg.mt43.event_time.day == 31);
}

// ── NW太平洋津波の詳細テスト ──────────────────────────────────────────────────

TEST_CASE("decodeNwPacTsu: 合成フレームでの詳細デコード") {
    uint8_t bits[32] = {};
    Message msg{};

    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 6);   // NW Pacific Tsunami
    setbits(bits, 214, 6, 1);

    // report_time: month=5, day=15, hour=10, min=0
    setbits(bits, 21, 4, 5);
    setbits(bits, 25, 5, 15);
    setbits(bits, 30, 5, 10);
    setbits(bits, 35, 6, 0);

    setbits(bits, 53, 3, 2);   // nw_pac_potential = 2

    // entry 1: region=1, arrival: nextday=1, hour=2, min=30, height=3
    setbits(bits, 56, 7, 1);
    // raw = (1 << 11) | (2 << 6) | 30 = 0x8BE
    setbits(bits, 63, 12, (1u << 11) | (2u << 6) | 30u);
    setbits(bits, 75, 9, 3);

    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);

    // 2026-05-15 10:00:00 UTC
    constexpr uint32_t NOW = 1747303200;

    TestDecoderEx::testDecodeNwPacTsu(bits, msg, NOW);

    CHECK(msg.mt43.nw_pac_potential == 2);
    CHECK(msg.mt43.nw_pac_count >= 1);
    if (msg.mt43.nw_pac_count >= 1) {
        CHECK(msg.mt43.nw_pac_tsunamis[0].region_code == 1);
        CHECK(msg.mt43.nw_pac_tsunamis[0].height_code == 3);
        // event_timeが解決されていれば到着時間も解決される
        if (msg.mt43.event_time.unix_time > 0) {
            CHECK(msg.mt43.nw_pac_tsunamis[0].arrival_time.hour == 2);
            CHECK(msg.mt43.nw_pac_tsunamis[0].arrival_time.minute == 30);
        }
    }
}

// ── 深さ501km以上の処理 ───────────────────────────────────────────────────────

TEST_CASE("Edge Case: 深さ501km以上 (コード501)") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 2);
    setbits(bits, 214, 6, 1);
    setbits(bits, 96, 9, 501);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo_depth == 501);
}

TEST_CASE("Edge Case: 深さ511 (不明)") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 2);
    setbits(bits, 214, 6, 1);
    setbits(bits, 96, 9, 511);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo_depth == 511);
}

TEST_CASE("Edge Case: マグニチュード126 (8.0以上不明)") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 2);
    setbits(bits, 214, 6, 1);
    setbits(bits, 105, 7, 126);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo_magnitude == 126);
}

TEST_CASE("Edge Case: マグニチュード127 (不明)") {
    uint8_t bits[32] = {};
    Message msg{};
    setbits(bits, 0, 8, 0x53);
    setbits(bits, 8, 6, 43);
    setbits(bits, 17, 4, 2);
    setbits(bits, 214, 6, 1);
    setbits(bits, 105, 7, 127);
    uint32_t crc = crc24q_ref(bits, 226);
    setbits(bits, 226, 24, crc);
    Frame frame{}; memcpy(frame.bits, bits, 32); frame.svid = 55;
    Decoder dec;
    REQUIRE(dec.decode(frame, msg, 0));
    CHECK(msg.mt43.hypo_magnitude == 127);
}

