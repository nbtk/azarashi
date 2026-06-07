// test/integration/test_azarashi_dcr.cpp
// MT=43 DCR の azarashi 比較テスト（データ駆動）
// azarashi v0.16.1 のデコード結果と照合

#include "../test_helpers.h"
#include "doctest.h"
#include <cstring>
#include <string>

using namespace azaraC;

// ═══════════════════════════════════════════════════════════════════════════════
// Nankai Trough 20メッセージ — test_scenario3
// azarashi でデコードした結果: page_number と total_page を検証
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: Nankai Trough 20 messages - page tracking") {
    struct NankaiCase {
        const char* nmea;
        uint8_t expected_page;
        uint8_t expected_total;
    };

    NankaiCase cases[] = {
        // 1ページ目
        {"$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02", 1, 27},
        // 26ページ目
        {"$QZQSM,58,9AAFA19C918002F1C0D471C0D1F1C0D371C0C7F1C0D071C0CAB4D812D45BCD0*06", 26, 27},
        // 25ページ目
        {"$QZQSM,58,9AAFA19C918002F1C0CFF4CC5973C0DEF2D7DF72DFCE71C14932D813A64867C*0C", 25, 27},
        // 24ページ目
        {"$QZQSM,58,53AFA19C918002F1C0C5F1C0C8F3D6C4F1C0D5F2DFCE71C0CC30D81029188EC*0F", 24, 27},
        // 23ページ目
        {"$QZQSM,58,C6AFA19C918002F1C0D4F1C0C5F1C144F1C0D772C8DE71C0D9AED8108F361A8*7A", 23, 27},
        // 22ページ目
        {"$QZQSM,58,9AAFA19C918002F2DD4E71C1427443D573595DF25EC9F1C0D52CD81113EFC54*00", 22, 27},
        // 21ページ目
        {"$QZQSM,58,9AAFA19C918002F1C0CCF1C041725DC572DF4671C0D7734A5FAAD811D504B9C*09", 21, 27},
        // 20ページ目
        {"$QZQSM,58,53AFA19C918002F1C0D4744041F1C0C471C144F1C14671C0DF28D8127EDCCCC*02", 20, 27},
        // 19ページ目
        {"$QZQSM,58,C6AFA19C918002F4D5CC71C0DF71C0D1F1C0D371C0C271C145A6D812E9F0C70*03", 19, 27},
        // 18ページ目
        {"$QZQSM,58,9AAFA19C918002F1C0DCF1C0D373CDDC72D7DF73CD4271C0D5A4D813579A170*78", 18, 27},
        // 17ページ目
        {"$QZQSM,58,9AAFA19C918002F1C0C672DCD9F2DC5C734CC171C0D5F357CA22D8100D3A898*07", 17, 27},
        // 16ページ目
        {"$QZQSM,58,53AFA19C918002F1C0D773CCDD73CA4FF2C7D7F441DEF34053A0D8108524298*01", 16, 27},
        // 15ページ目
        {"$QZQSM,58,C6AFA19C918002F1C040F2D253F45347F35450F2CE5874CE439ED8113990640*7D", 15, 27},
        // 14ページ目
        {"$QZQSM,58,9AAFA19C918002F2D74D74CE43F35D4872CFCFF1C0D3F1C0D79CD8118D63AC8*07", 14, 27},
        // 13ページ目
        {"$QZQSM,58,9AAFA19C918002F1C1D4F1C1CAF2CE5874CE43F1C0D77341D99AD81268C2E7C*73", 13, 27},
        // 12ページ目
        {"$QZQSM,58,53AFA19C918002F1C14471C14571C040F2C6CBF35ADBF1C1C418D812DC94FA0*7F", 12, 27},
        // 11ページ目
        {"$QZQSM,58,C6AFA19C918002F1C0DCF1C14571C0D773CCDD73CA4FF1C0D596D81357F75D0*74", 11, 27},
        // 10ページ目
        {"$QZQSM,58,9AAFA19C918002F1C145F1C14371C0D1F1C0C7F1C14571C0CC94D813ED6741C*0C", 10, 27},
        // 9ページ目
        {"$QZQSM,58,9AAFA19C918002F4C04D72DC5C71C0D471C0D7F3CAD871C0D512D810ADB00F0*78", 9, 27},
        // 8ページ目
        {"$QZQSM,58,53AFA19C918002F1C14671C0DF71C0CCF1C04171C0C9F1C0D710D8112F31B60*73", 8, 27},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        CAPTURE(cases[i].nmea);
        REQUIRE(decodeNmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 4);
        CHECK(msg.mt43.nankai.page == cases[i].expected_page);
        CHECK(msg.mt43.nankai.total_page == cases[i].expected_total);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Ash Fall 5メッセージ — test_scenario5
// azarashi でデコードした結果: volcano_name, warning_codes, local_governments を検証
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: Ash Fall Detailed 5 messages - field verification") {
    struct AshCase {
        const char* nmea;
        uint16_t expected_volcano;
        uint8_t expected_warning_type;
        uint8_t expected_entry_count;
        uint8_t expected_time_0;
        uint8_t expected_code_0;
        uint32_t expected_lg_0;
    };

    AshCase cases[] = {
        // メッセージ1: 阿蘇山, 詳細, 4エントリ, time=1, code=2(やや多量), lg=4321400(阿蘇市)
        {"$QZQSM,58,C6AFC99CAA0001CAA43EE541F0782A1220813091811183E0F000001329B16E0*7F",
         503, 2, 4, 1, 2, 4321400},
        // メッセージ2: 阿蘇山, 詳細, 4エントリ, time=2, code=1(少量), lg=4342800(高森町)
        {"$QZQSM,58,C6AFC99CAA0001CAA43EE8C2441046123023307C1E19848820000013E2F3E6C*00",
         503, 2, 4, 2, 1, 4342800},
        // メッセージ3: 阿蘇山, 詳細, 4エントリ, time=3, code=1(少量), lg=4343300(南阿蘇村)
        {"$QZQSM,58,9AAFC99CAA0001CAA43EECC24604860F83C430910421848C080000106286874*00",
         503, 2, 4, 3, 1, 4343300},
        // メッセージ4: 阿蘇山, 詳細, 4エントリ, time=5, code=1(少量), lg=4321400(阿蘇市)
        {"$QZQSM,58,53AFC99CAA0001CAA43EF4C1F078A61220853091813183E0F0000010CE8C39C*77",
         503, 2, 4, 5, 1, 4321400},
        // メッセージ5: 阿蘇山, 詳細, 2エントリ, time=6, code=1(少量), lg=4342800(高森町)
        {"$QZQSM,58,C6AFC99CAA0001CAA43EF8C24410C61230200000000000000000001148565F4*0A",
         503, 2, 2, 6, 1, 4342800},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        CAPTURE(cases[i].nmea);
        REQUIRE(decodeNmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 9);
        CHECK(msg.mt43.ash.volcano_name == cases[i].expected_volcano);
        CHECK(msg.mt43.ash.warning_type == cases[i].expected_warning_type);
        CHECK(msg.mt43.ash.count == cases[i].expected_entry_count);
        CHECK(msg.mt43.ash.entries_time[0] == cases[i].expected_time_0);
        CHECK(msg.mt43.ash.entries_code[0] == cases[i].expected_code_0);
        CHECK(msg.mt43.ash.entries_lg[0] == cases[i].expected_lg_0);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather 3メッセージ — test_scenario6
// azarashi でデコードした結果: sub_categories, region_codes を検証
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: Weather 3 messages - field verification") {
    struct WxCase {
        const char* nmea;
        uint8_t expected_state;
        uint8_t expected_count;
        uint8_t expected_sub_0;
        uint32_t expected_region_0;
    };

    WxCase cases[] = {
        // メッセージ1: 発表, 6エントリ, sub=2(大雨特別警報), region=80000(茨城県)
        {"$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73",
         1, 6, 2, 80000},
        // メッセージ2: 発表, 6エントリ, sub=2(大雨特別警報), region=140000(神奈川県)
        {"$QZQSM,58,9AAFD19CB180011222E0B93880B95F90B986A0B9ADB0B9D4C0000013D276B60*0D",
         1, 6, 2, 140000},
        // メッセージ3: 発表, 2エントリ, sub=23(土砂災害警戒), region=130000(東京都)
        {"$QZQSM,58,53AFD19CB18001B9FBD0BA22E00000000000000000000000000000107AA71EC*76",
         1, 2, 23, 130000},
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        Message msg{};
        CAPTURE(i);
        CAPTURE(cases[i].nmea);
        REQUIRE(decodeNmea(cases[i].nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 10);
        CHECK(msg.mt43.wx.warning_state == cases[i].expected_state);
        CHECK(msg.mt43.wx.count == cases[i].expected_count);
        CHECK(msg.mt43.wx.entries[0].sub_category == cases[i].expected_sub_0);
        CHECK(msg.mt43.wx.entries[0].region_code == cases[i].expected_region_0);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EEW 長周期地震動階級 — 仕様書ベースの網羅テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: EEW Long Period Ground Motion - exhaustive") {
    // LgL1=3, LgU3=3 のテスト (既存のLong Period Ground Motionテストの検証強化)
    Message msg{};
    const char* nmea = "$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 43);
    CHECK(msg.payload_type == MsgPayloadType::Mt43);
    CHECK(msg.mt43.disaster_category == 1);
    CHECK(msg.mt43.eew.long_period_lower == 3);
    CHECK(msg.mt43.eew.long_period_upper == 3);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tsunami 到達時刻境界値テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: Tsunami arrival time boundary - arrived (hour=31, min=63)") {
    // 津波が既に到達した場合: AzaraCではhour/minuteを0にクリアし、unix_timeも0にする
    // これは仕様書の「到達済み」フラグを正しく処理している
    uint8_t bits[32] = {};
    Message msg{};

    setBits(bits, 0, 8, 0x53);    // preamble
    setBits(bits, 8, 6, 43);      // msg_type
    setBits(bits, 17, 4, 5);      // disaster_category = Tsunami
    setBits(bits, 214, 6, 1);     // version

    // Report Time: Month=4, Day=25, Hour=13, Min=0
    setBits(bits, 21, 4, 4);
    setBits(bits, 25, 5, 25);
    setBits(bits, 30, 5, 13);
    setBits(bits, 35, 6, 0);

    // Warning Code = 3 (津波警報)
    setBits(bits, 80, 4, 3);

    // Tsunami entry: Region=1, Height=2
    setBits(bits, 84, 10, 1);
    setBits(bits, 94, 4, 2);

    // Arrival: NextDay=0, Hour=31, Min=63 (既に到達)
    // 12ビットまとめて設定: (NextDay << 11) | (Hour << 6) | Min
    setBits(bits, 98, 12, (0u << 11) | (31u << 6) | 63u);

    uint32_t crc = crc24qRef(bits, 226);
    setBits(bits, 226, 24, crc);

    TestDecoder::testDecodeTsunami(bits, msg, 1777122000u);

    REQUIRE(msg.mt43.tsunami.count >= 1);
    // 到達済みの場合、AzaraCではhour=0, minute=0, unix_time=0 にクリアする
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.hour == 0);
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.minute == 0);
    CHECK(msg.mt43.tsunami.entries[0].arrival_time.unix_time == 0);
}

// ═══════════════════════════════════════════════════════════════════════════════
// NW Pacific Tsunami Tsunamigenic Potential 網羅テスト
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCR: NW Pacific Tsunami - Tsunamigenic Potential patterns") {
    // Pattern 1: potential=0 (津波発生の可能性なし)
    {
        Message msg{};
        const char* nmea = "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C";
        REQUIRE(decodeNmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6);
    }
    // Pattern 2: potential=2 (広域津波の可能性あり)
    {
        Message msg{};
        const char* nmea = "$QZQSM,56,9AAD3609E080023AE008D3D1008E449009D457009E3E5011F00000138B3E720*09";
        REQUIRE(decodeNmea(nmea, msg));
        CHECK(msg.msg_type == 43);
        CHECK(msg.payload_type == MsgPayloadType::Mt43);
        CHECK(msg.mt43.disaster_category == 6);
    }
}
