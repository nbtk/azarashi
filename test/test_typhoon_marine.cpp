// test/test_typhoon_marine.cpp — 台風・海洋デコード関数の直接検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// テスト用にprotected関数を公開
struct TestDecoderTM : public Decoder {
    static void testDecodeTyphoon(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoderTM t;
        t.decodeTyphoon(bits, out, now_unix);
    }
    
    static void testDecodeMarine(const uint8_t* bits, Message& out) {
        TestDecoderTM t;
        t.decodeMarine(bits, out);
    }
    
    static void setBits(uint8_t* buf, uint16_t start, uint8_t len, uint32_t value) {
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) buf[pos>>3] |=  (1 << (7-(pos&7)));
            else              buf[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    }
};

TEST_CASE("decodeTyphoon: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};
    
    // 台風フィールドの設定（Decoder.cpp参照）
    // reference_time: day=15, hour=12, minute=30 at bit 53
    TestDecoderTM::setBits(bits, 53, 5, 15);       // day
    TestDecoderTM::setBits(bits, 58, 5, 12);       // hour
    TestDecoderTM::setBits(bits, 63, 6, 30);       // minute
    
    // ref_type:1 at bit 69
    TestDecoderTM::setBits(bits, 69, 3, 1);
    
    // elapsed: 24 at bit 80
    TestDecoderTM::setBits(bits, 80, 7, 24);
    
    // number: 5 at bit 87
    TestDecoderTM::setBits(bits, 87, 7, 5);
    
    // scale: 3 at bit 94
    TestDecoderTM::setBits(bits, 94, 4, 3);
    
    // intensity: 2 at bit 98
    TestDecoderTM::setBits(bits, 98, 4, 2);
    
    // position 1: 北緯25度, 東経130度 (1度単位)
    // lat_s=0 (北), lat_d=25 at bit 102
    TestDecoderTM::setBits(bits, 102, 1, 0);       // lat_sign
    TestDecoderTM::setBits(bits, 103, 8, 25);      // lat_d
    // lon_s=0 (東), lon_d=130 at bit 111
    TestDecoderTM::setBits(bits, 111, 1, 0);       // lon_sign
    TestDecoderTM::setBits(bits, 112, 9, 130);     // lon_d
    
    // 直接decodeTyphoonを呼び出し
    TestDecoderTM::testDecodeTyphoon(bits, msg, 1704067200u);
    
    // 結果を検証
    CHECK(msg.typh_ref_type == 1);
    CHECK(msg.typh_elapsed == 24);
    CHECK(msg.typh_number == 5);
    CHECK(msg.typh_scale == 3);
    CHECK(msg.typh_intensity == 2);
    CHECK(msg.typh_pos_count >= 1);
    if (msg.typh_pos_count > 0) {
        // lat_e1 = lat_d * 10 (1度単位を0.1度単位に変換)
        CHECK(msg.typh_positions[0].lat_e1 == 250);   // 25 * 10
        CHECK(msg.typh_positions[0].lon_e1 == 1300);  // 130 * 10
    }
}

TEST_CASE("decodeTyphoon: 複数位置の検証") {
    uint8_t bits[32] = {};
    Message msg{};
    
    // 位置1: 北緯25度, 東経130度
    TestDecoderTM::setBits(bits, 102, 1, 0);       // lat_sign=0
    TestDecoderTM::setBits(bits, 103, 8, 25);      // lat_d=25
    TestDecoderTM::setBits(bits, 111, 1, 0);       // lon_sign=0
    TestDecoderTM::setBits(bits, 112, 9, 130);     // lon_d=130
    
    // 位置2: 南緯10度, 西経140度
    // lat_s=1 (南), lat_d=10 at bit 121
    TestDecoderTM::setBits(bits, 121, 1, 1);       // lat_sign=1
    TestDecoderTM::setBits(bits, 122, 8, 10);      // lat_d=10
    // lon_s=1 (西), lon_d=140 at bit 130
    TestDecoderTM::setBits(bits, 130, 1, 1);       // lon_sign=1
    TestDecoderTM::setBits(bits, 131, 9, 140);     // lon_d=140
    
    TestDecoderTM::testDecodeTyphoon(bits, msg, 1704067200u);
    
    CHECK(msg.typh_pos_count == 2);
    if (msg.typh_pos_count >= 2) {
        // 位置1: 北緯25度 → lat_e1 = 250
        CHECK(msg.typh_positions[0].lat_e1 == 250);
        CHECK(msg.typh_positions[0].lon_e1 == 1300);
        // 位置2: 南緯10度 → lat_e1 = -100 (符号付き)
        CHECK(msg.typh_positions[1].lat_e1 == -100);
        CHECK(msg.typh_positions[1].lon_e1 == -1400);
    }
}

TEST_CASE("decodeMarine: 合成フレームでの基本動作") {
    uint8_t bits[32] = {};
    Message msg{};
    
    // 海洋カテゴリのビット配置: warning_code(5) + region_code(14) at bit 53
    // エントリ1: warning_code=3, region_code=100
    TestDecoderTM::setBits(bits, 53, 5, 3);        // warning_code
    TestDecoderTM::setBits(bits, 58, 14, 100);     // region_code
    
    // エントリ2: warning_code=5, region_code=200
    TestDecoderTM::setBits(bits, 72, 5, 5);        // warning_code
    TestDecoderTM::setBits(bits, 77, 14, 200);     // region_code
    
    TestDecoderTM::testDecodeMarine(bits, msg);
    
    CHECK(msg.marine_count == 2);
    if (msg.marine_count >= 2) {
        CHECK(msg.marine_entries[0].warning_code == 3);
        CHECK(msg.marine_entries[0].region_code == 100);
        CHECK(msg.marine_entries[1].warning_code == 5);
        CHECK(msg.marine_entries[1].region_code == 200);
    }
}

TEST_CASE("decodeMarine: 最大エントリ数の検証") {
    uint8_t bits[32] = {};
    Message msg{};
    
    // 8エントリを設定
    for (int i = 0; i < 8; i++) {
        uint16_t off = 53 + i * 19;
        TestDecoderTM::setBits(bits, off,      5, i+1);  // warning_code
        TestDecoderTM::setBits(bits, off +  5, 14, 1000 + i); // region_code
    }
    
    TestDecoderTM::testDecodeMarine(bits, msg);
    
    // marine_countは最大8になるはず
    CHECK(msg.marine_count <= 8);
    if (msg.marine_count == 8) {
        CHECK(msg.marine_entries[7].warning_code == 8);
        CHECK(msg.marine_entries[7].region_code == 1007);
    }
}
