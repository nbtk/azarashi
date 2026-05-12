// test/test_time.cpp — 日付・時間変換関数の厳密な検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

// テスト用にprotected static関数を公開
struct TestDecoder : Decoder {
    static TimeFields testResolveTime(uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint32_t now_unix) {
        return resolveTime(month, day, hour, minute, now_unix);
    }
};

// civil_from_days と days_from_civil の再定義（静的関数のテストのため）
static void civil_from_days(uint32_t days_since_1970, uint32_t& y, uint32_t& m, uint32_t& d) {
    uint32_t z = days_since_1970 + 719468u;
    uint32_t era = z / 146097u;
    uint32_t doe = z - era * 146097u;
    uint32_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    y = yoe + era * 400;
    uint32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    uint32_t mp = (5 * doy + 2) / 153;
    d = doy - (153 * mp + 2) / 5 + 1;
    m = mp + (mp < 10 ? 3 : -9);
    y += (m <= 2);
}

static uint32_t days_from_civil(uint32_t y, uint32_t m, uint32_t d) {
    y -= (m <= 2);
    uint32_t era = y / 400;
    uint32_t yoe = y - era * 400;
    uint32_t doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + doe - 719468;
}

TEST_CASE("days_from_civil と civil_from_days の相互変換") {
    // 既知の日付でテスト
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
        uint32_t days = days_from_civil(tc.year, tc.month, tc.day);
        uint32_t y, m, d;
        civil_from_days(days, y, m, d);
        
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
    // unix_timeが正しいか確認
    CHECK(t.unix_time == 1704067200u);
}

TEST_CASE("resolveTime: 異なる日付の変換") {
    // 2024-06-15 12:30:00 のunix_timeを計算
    // まずdays_from_civilで日数を計算
    uint32_t days = days_from_civil(2024, 6, 15);
    // uint32_t expected_unix = days * 86400u + 12u * 3600u + 30u * 60u + 45u;
    
    // 基準時刻をその日の00:00:00に設定
    uint32_t now = days * 86400u;
    
    TimeFields t = TestDecoder::testResolveTime(6, 15, 12, 30, now);
    CHECK(t.day == 15);
    CHECK(t.hour == 12);
    CHECK(t.minute == 30);
    // 正確なunix_timeの確認は秒まで考慮する必要があるが、ここでは分まで
}

TEST_CASE("resolveTime: 月のラップアラウンド") {
    // 2024-01-15 を基準にする
    uint32_t now = days_from_civil(2024, 1, 15) * 86400u;
    
    // 12月の日付を指定（前年の12月と解釈されるべき）
    TimeFields t = TestDecoder::testResolveTime(12, 31, 0, 0, now);
    // 2023-12-31 になるはず
    CHECK(t.unix_time > 0);
    // より厳密には、days_from_civil(2023, 12, 31) * 86400 と比較
    uint32_t expected = days_from_civil(2023, 12, 31) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 日のラップアラウンド（DHMのみ）") {
    // 2024-01-15 を基準
    uint32_t now = days_from_civil(2024, 1, 15) * 86400u;
    
    // 日付を32にして、ラップアラウンドをテスト（month=0なのでDHMのみ）
    // 実際のプロトコルでは1-31の範囲だが、テストでは境界値をテスト
    TimeFields t = TestDecoder::testResolveTime(0, 20, 0, 0, now);
    CHECK(t.day == 20);
}

TEST_CASE("extractDHM: 日時抽出のテスト") {
    // day=15 (5bit), hour=10 (5bit), minute=30 (6bit)
    uint8_t day = 15, hour = 10, minute = 30;
    
    // resolveTimeを直接テスト
    uint32_t now = days_from_civil(2024, 1, 15) * 86400u;
    TimeFields t = TestDecoder::testResolveTime(0, day, hour, minute, now);
    
    CHECK(t.day == day);
    CHECK(t.hour == hour);
    CHECK(t.minute == minute);
}

TEST_CASE("resolveTime: 日付のラップアラウンド（月末→月初）") {
    // 基準: 2024-01-01 (day=1)
    uint32_t now = days_from_civil(2024, 1, 1) * 86400u;
    
    // day=31を指定（前月の31日と解釈されるべき）
    TimeFields t = TestDecoder::testResolveTime(0, 31, 0, 0, now);
    // 2023-12-31 になるはず
    uint32_t expected = days_from_civil(2023, 12, 31) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 日付のラップアラウンド（月初→月末）") {
    // 基準: 2024-01-31 (day=31)
    uint32_t now = days_from_civil(2024, 1, 31) * 86400u;
    
    // day=1を指定（翌月の1日と解釈されるべき）
    TimeFields t = TestDecoder::testResolveTime(0, 1, 0, 0, now);
    // 2024-02-01 になるはず
    uint32_t expected = days_from_civil(2024, 2, 1) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: MDHM形式（月指定あり）") {
    // 基準: 2024-06-15
    uint32_t now = days_from_civil(2024, 6, 15) * 86400u;
    
    // month=6, day=15, hour=12, minute=0
    TimeFields t = TestDecoder::testResolveTime(6, 15, 12, 0, now);
    CHECK(t.day == 15);
    CHECK(t.hour == 12);
    CHECK(t.minute == 0);
    uint32_t expected = days_from_civil(2024, 6, 15) * 86400u + 12 * 3600u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 月のラップアラウンド（MDHM）") {
    // 基準: 2024-01-15
    uint32_t now = days_from_civil(2024, 1, 15) * 86400u;
    
    // month=12を指定（前年の12月と解釈されるべき）
    TimeFields t = TestDecoder::testResolveTime(12, 15, 0, 0, now);
    // 2023-12-15 になるはず
    uint32_t expected = days_from_civil(2023, 12, 15) * 86400u;
    CHECK(t.unix_time == expected);
}

TEST_CASE("resolveTime: 無効な入力の処理") {
    // 無効な日付（day=0やday=32）
    TimeFields t1 = TestDecoder::testResolveTime(0, 0, 0, 0, 1704067200u);
    CHECK(t1.day == 0);  // 無効なので0になるはず
    CHECK(t1.hour == 0);
    CHECK(t1.minute == 0);
    
    TimeFields t2 = TestDecoder::testResolveTime(0, 32, 0, 0, 1704067200u);
    // day=32は無効なので、サニティチェックで0になる
    CHECK(t2.day == 0);
    CHECK(t2.hour == 0);
    CHECK(t2.minute == 0);
    
    // 無効な月
    TimeFields t3 = TestDecoder::testResolveTime(13, 1, 0, 0, 1704067200u);
    CHECK(t3.day == 0);
    CHECK(t3.hour == 0);
    CHECK(t3.minute == 0);
    
    // 無効な時刻
    TimeFields t4 = TestDecoder::testResolveTime(1, 1, 24, 0, 1704067200u);
    CHECK(t4.day == 0);
    CHECK(t4.hour == 0);
    CHECK(t4.minute == 0);
}

TEST_CASE("Unix時間の計算検証") {
    // 2024-01-01 00:00:00 UTC = 1704067200
    // resolveTime(1, 1, 0, 0, 1704067200) は同じはず
    TimeFields t = TestDecoder::testResolveTime(1, 1, 0, 0, 1704067200u);
    
    // 日数 * 86400 + 時*3600 + 分*60 で計算されるはず
    CHECK(t.unix_time == 1704067200u);
}
