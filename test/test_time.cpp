// test/test_time.cpp — 日付・時間変換関数の厳密な検証
#include "test_helpers.h"
#include "doctest.h"

using namespace azaraC;
using namespace azaraC::internal;

TEST_CASE("daysFromCivil と civilFromDays の相互変換") {
    struct TestCase {
        uint32_t year, month, day;
    };
    TestCase cases[] = {
        {2024, 1, 1},
        {2024, 12, 31},
        {2023, 2, 28},
        {2024, 2, 29}, // うるう年
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
    // 2024-01-01 00:00:00 UTC = 1704067200
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
    // ESP32/Arduinoで NTP 未同期の場合、report_unix=0 を渡すことがある
    // unix_time は 0 のままだが、day/hour/minute は保持されることを確認
    TimeFields t = TestDecoder::testResolveTime(0, 15, 10, 30, 0u);
    CHECK(t.day == 15);
    CHECK(t.hour == 10);
    CHECK(t.minute == 30);
    CHECK(t.unix_time == 0); // 年解決不許可のため 0
}

TEST_CASE("resolveTime: now_unix < 2000年 (複数時刻覚ケース)") {
    // 1999-12-31: unix=946684799 (閘値946684800未満)
    // 準拠として無効なので unix_time=0 のまま
    TimeFields t = TestDecoder::testResolveTime(0, 20, 12, 0, 946684799u);
    CHECK(t.day == 20);
    CHECK(t.hour == 12);
    CHECK(t.minute == 0);
    CHECK(t.unix_time == 0);

    // 専門の記込みシステムで GPS 連操前にメッセージを受信するケース
    // 2000-01-01 00:00:00 UTC = 946684800 (閘値以上なら有効)
    TimeFields t2 = TestDecoder::testResolveTime(1, 1, 0, 0, 946684800u);
    CHECK(t2.unix_time == 946684800u);
}
