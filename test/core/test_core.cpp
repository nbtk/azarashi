// test/core/test_core.cpp — コア機能テスト
// CRC-24Q, 時間変換, 緯度経度, 重複除去の統合テスト
// test_crc.cpp, test_time.cpp, test_latlon.cpp, test_dedup.cpp を統合

#include "../test_helpers.h"
#include "doctest.h"

using namespace azaraC;

// ── CRC-24Q テスト (from test_crc.cpp) ─────────────────────────────────────

TEST_CASE("CRC-24Q vs reference") {
    uint8_t buf[29] = {};
    uint32_t a = TestDecoder::calcCRC(buf, 226);
    uint32_t b = crc24qRef(buf, 226);
    CHECK(a == b);

    for (auto& v : buf) v = 0xA5;
    a = TestDecoder::calcCRC(buf, 226);
    b = crc24qRef(buf, 226);
    CHECK(a == b);
}

TEST_CASE("getBits extraction") {
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
    bool ok = dec.decode(f, msg);
    CHECK(ok == false);
}

TEST_CASE("MT=44 field extraction on synthetic frame") {
    uint8_t buf[32] = {};

    setBits(buf, 0,  8, 0x53);
    setBits(buf, 8,  6, 44);
    setBits(buf, 24, 2, 1);
    setBits(buf, 26, 9, 111);
    setBits(buf, 35, 5, 2);

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

// ── 時間変換テスト (from test_time.cpp) ────────────────────────────────────

TEST_CASE("daysFromCivil と civilFromDays の相互変換") {
    struct TestCase {
        uint32_t year, month, day;
    };
    TestCase cases[] = {
        {2024, 1, 1},
        {2024, 12, 31},
        {2023, 2, 28},
        {2024, 2, 29},
        {2000, 1, 1},
        {1970, 1, 1},
    };

    for (auto& tc : cases) {
        uint32_t days = daysFromCivil(tc.year, tc.month, tc.day);
        uint32_t y, m, d;
        civilFromDays(days, y, m, d);

        CAPTURE(tc.year);
        CAPTURE(tc.month);
        CAPTURE(tc.day);
        CHECK(y == tc.year);
        CHECK(m == tc.month);
        CHECK(d == tc.day);
    }
}

TEST_CASE("resolveTime: 基本的な日付変換") {
    uint32_t now = 1704067200u;
    TimeFields t = TestDecoder::testResolveTime(1, 1, 0, 0, now);
    CHECK(t.day == 1);
    CHECK(t.hour == 0);
    CHECK(t.minute == 0);
    CHECK(t.unix_time == 1704067200u);
}

TEST_CASE("resolveTime: 異なる日付の変換") {
    uint32_t days = daysFromCivil(2024, 6, 15);
    uint32_t expected_unix = days * 86400u + 12u * 3600u + 30u * 60u;
    uint32_t now = days * 86400u;

    TimeFields t = TestDecoder::testResolveTime(6, 15, 12, 30, now);
    CHECK(t.day == 15);
    CHECK(t.hour == 12);
    CHECK(t.minute == 30);
    CHECK(t.unix_time == expected_unix);
}

TEST_CASE("resolveTime: 月のラップアラウンド") {
    uint32_t now = daysFromCivil(2024, 1, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(12, 31, 0, 0, now);
    uint32_t expected = daysFromCivil(2023, 12, 31) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 日のラップアラウンド（DHMのみ）") {
    uint32_t now = daysFromCivil(2024, 1, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(0, 20, 0, 0, now);
    CHECK(t.day == 20);
}

TEST_CASE("resolveTime: DHM形式のテスト") {
    uint8_t day = 15, hour = 10, minute = 30;
    uint32_t now = daysFromCivil(2024, 1, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(0, day, hour, minute, now);

    CHECK(t.day == day);
    CHECK(t.hour == hour);
    CHECK(t.minute == minute);
}

TEST_CASE("resolveTime: 日付のラップアラウンド（月末→月初）") {
    uint32_t now = daysFromCivil(2024, 1, 1) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(0, 31, 0, 0, now);
    uint32_t expected = daysFromCivil(2023, 12, 31) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 日付のラップアラウンド（月初→月末）") {
    uint32_t now = daysFromCivil(2024, 1, 31) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(0, 1, 0, 0, now);
    uint32_t expected = daysFromCivil(2024, 2, 1) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: MDHM形式（月指定あり）") {
    uint32_t now = daysFromCivil(2024, 6, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(6, 15, 12, 0, now);
    CHECK(t.day == 15);
    CHECK(t.hour == 12);
    CHECK(t.minute == 0);
    uint32_t expected = daysFromCivil(2024, 6, 15) * 86400u + 12 * 3600u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 月のラップアラウンド（MDHM）") {
    uint32_t now = daysFromCivil(2024, 1, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(12, 15, 0, 0, now);
    uint32_t expected = daysFromCivil(2023, 12, 15) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 無効な入力の処理") {
    TimeFields t1 = TestDecoder::testResolveTime(0, 0, 0, 0, 1704067200u);
    CHECK(t1.day == 0);
    CHECK(t1.hour == 0);
    CHECK(t1.minute == 0);
    CHECK(t1.unix_time == 0);

    TimeFields t2 = TestDecoder::testResolveTime(0, 32, 0, 0, 1704067200u);
    CHECK(t2.day == 0);
    CHECK(t2.hour == 0);
    CHECK(t2.minute == 0);
    CHECK(t2.unix_time == 0);

    TimeFields t3 = TestDecoder::testResolveTime(13, 1, 0, 0, 1704067200u);
    CHECK(t3.day == 0);
    CHECK(t3.hour == 0);
    CHECK(t3.minute == 0);
    CHECK(t3.unix_time == 0);

    TimeFields t4 = TestDecoder::testResolveTime(1, 1, 24, 0, 1704067200u);
    CHECK(t4.day == 0);
    CHECK(t4.hour == 0);
    CHECK(t4.minute == 0);
    CHECK(t4.unix_time == 0);
}

TEST_CASE("Unix時間の計算検証") {
    TimeFields t = TestDecoder::testResolveTime(1, 1, 0, 0, 1704067200u);
    CHECK(t.unix_time == 1704067200u);
}

TEST_CASE("resolveTime: now_unix=0 (未同期シナリオ)") {
    TimeFields t = TestDecoder::testResolveTime(0, 15, 10, 30, 0u);
    CHECK(t.day == 15);
    CHECK(t.hour == 10);
    CHECK(t.minute == 30);
    CHECK(t.unix_time == 0);
}

TEST_CASE("resolveTime: now_unix < 2000年 (閾値テスト)") {
    TimeFields t = TestDecoder::testResolveTime(0, 20, 12, 0, 946684799u);
    CHECK(t.day == 20);
    CHECK(t.hour == 12);
    CHECK(t.minute == 0);
    CHECK(t.unix_time == 0);

    TimeFields t2 = TestDecoder::testResolveTime(1, 1, 0, 0, 946684800u);
    CHECK(t2.unix_time == 946684800u);
}

TEST_CASE("daysFromCivil と civilFromDays の網羅的ストレステスト (1970-2100)") {
    uint32_t start_days = daysFromCivil(1970, 1, 1);
    uint32_t end_days = daysFromCivil(2100, 12, 31);

    for (uint32_t days = start_days; days <= end_days; ++days) {
        uint32_t y = 0, m = 0, d = 0;
        civilFromDays(days, y, m, d);
        uint32_t reconstructed = daysFromCivil(y, m, d);

        if (reconstructed != days) {
            CAPTURE(days);
            CAPTURE(y);
            CAPTURE(m);
            CAPTURE(d);
            CAPTURE(reconstructed);
            FAIL("日付のラウンドトリップ変換が一致しません");
        }
    }
}

// ── 緯度経度テスト (from test_latlon.cpp) ──────────────────────────────────

TEST_CASE("extractLatLon: 基本的な緯度経度抽出") {
    uint8_t buf[32] = {};

    setBits(buf, 0, 1, 0);
    setBits(buf, 1, 7, 35);
    setBits(buf, 8, 6, 30);
    setBits(buf, 14, 6, 45);

    setBits(buf, 20, 1, 0);
    setBits(buf, 21, 8, 139);
    setBits(buf, 29, 6, 45);
    setBits(buf, 35, 6, 30);

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

    CHECK(ll.lat_ns == 0);
    CHECK(ll.lat_deg == 35);
    CHECK(ll.lat_min == 30);
    CHECK(ll.lat_sec == 45);
    CHECK(ll.lon_ew == 0);
    CHECK(ll.lon_deg == 139);
    CHECK(ll.lon_min == 45);
    CHECK(ll.lon_sec == 30);
}

TEST_CASE("extractLatLon: 南緯と西経") {
    uint8_t buf[32] = {};

    setBits(buf, 0, 1, 1);
    setBits(buf, 1, 7, 33);
    setBits(buf, 8, 6, 0);
    setBits(buf, 14, 6, 0);

    setBits(buf, 20, 1, 1);
    setBits(buf, 21, 8, 151);
    setBits(buf, 29, 6, 0);
    setBits(buf, 35, 6, 0);

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

    CHECK(ll.lat_ns == 1);
    CHECK(ll.lat_deg == 33);
    CHECK(ll.lon_ew == 1);
    CHECK(ll.lon_deg == 151);
}

TEST_CASE("extractLatLon: 境界値テスト") {
    uint8_t buf[32] = {};

    setBits(buf, 0, 1, 0);
    setBits(buf, 1, 7, 90);
    setBits(buf, 8, 6, 59);
    setBits(buf, 14, 6, 59);

    setBits(buf, 20, 1, 0);
    setBits(buf, 21, 8, 180);
    setBits(buf, 29, 6, 59);
    setBits(buf, 35, 6, 59);

    LatLon ll = TestDecoder::testExtractLatLon(buf, 0);

    CHECK(ll.lat_deg == 90);
    CHECK(ll.lat_min == 59);
    CHECK(ll.lat_sec == 59);
    CHECK(ll.lon_deg == 180);
    CHECK(ll.lon_min == 59);
    CHECK(ll.lon_sec == 59);
}

// ── 重複除去テスト (from test_dedup.cpp) ───────────────────────────────────

TEST_CASE("DedupFilter: 新規メッセージは重複しない") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: 同じキーは重複と判定される") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
    CHECK(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: 異なるsvidは重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{194, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 異なるmsg_typeは重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{193, 44, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 異なるcrc24は重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{193, 43, 0x123456};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 複数メッセージの管理") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xAAAAAA};
    DedupKey key2{193, 43, 0xBBBBBB};
    DedupKey key3{193, 43, 0xCCCCCC};

    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
    CHECK_FALSE(filter.isDuplicate(key3));

    CHECK(filter.isDuplicate(key1));
    CHECK(filter.isDuplicate(key2));
    CHECK(filter.isDuplicate(key3));
}

TEST_CASE("DedupFilter: reset後に新規として扱われる") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
    CHECK(filter.isDuplicate(key));

    filter.reset();
    CHECK_FALSE(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: リングバッファのラップアラウンド") {
    DedupFilter filter;
    DedupKey keys[33];
    for (int i = 0; i < 33; i++) {
        keys[i] = {193, 43, (uint32_t)(0x100000 + i)};
    }

    for (int i = 0; i < 32; i++) {
        CHECK_FALSE(filter.isDuplicate(keys[i]));
    }

    CHECK_FALSE(filter.isDuplicate(keys[32]));
    CHECK_FALSE(filter.isDuplicate(keys[0]));
    CHECK(filter.isDuplicate(keys[32]));
}

TEST_CASE("DedupFilter: 同一CRCでもsvidが異なれば別メッセージ") {
    DedupFilter filter;
    DedupKey key1{55, 43, 0xABCDEF};
    DedupKey key2{56, 43, 0xABCDEF};
    DedupKey key3{57, 43, 0xABCDEF};

    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
    CHECK_FALSE(filter.isDuplicate(key3));
}

TEST_CASE("DedupFilter: 大量メッセージの処理") {
    DedupFilter filter;
    for (int i = 0; i < 512; i++) {
        DedupKey key{193, 43, (uint32_t)(0x100000 + i)};
        CHECK_FALSE(filter.isDuplicate(key));
    }

    for (int i = 512 - AZARAC_DEDUP_SLOTS; i < 512; i++) {
        DedupKey key{193, 43, (uint32_t)(0x100000 + i)};
        CHECK(filter.isDuplicate(key));
    }
}
