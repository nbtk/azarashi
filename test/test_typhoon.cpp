// test/test_typhoon.cpp — 台風デコード関数の検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// テスト用にprotected関数を公開
struct TestDecoderTyphoon : public Decoder {
    static void testDecodeTyphoon(const uint8_t* bits, Message& out, uint32_t now_unix) {
        // 一時オブジェクトで呼び出し
        TestDecoderTyphoon t;
        t.decodeTyphoon(bits, out, now_unix);
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

    // プリアンブル: 0x53, MT:43, report_classification:0, disaster_category:12
    TestDecoderTyphoon::setBits(bits, 0, 8, 0x53);       // preamble
    TestDecoderTyphoon::setBits(bits, 8, 6, 43);        // msg_type
    TestDecoderTyphoon::setBits(bits, 14, 3, 0);        // report_classification
    TestDecoderTyphoon::setBits(bits, 17, 4, 12);       // disaster_category = 12
    TestDecoderTyphoon::setBits(bits, 41, 2, 0);        // information_type
    TestDecoderTyphoon::setBits(bits, 214, 6, 1);      // version = 1

    // reference_time: day=15, hour=12, minute=30 at bit 53
    TestDecoderTyphoon::setBits(bits, 53, 5, 15);       // day
    TestDecoderTyphoon::setBits(bits, 58, 5, 12);       // hour
    TestDecoderTyphoon::setBits(bits, 63, 6, 30);       // minute

    // ref_type:1 at bit 69
    TestDecoderTyphoon::setBits(bits, 69, 3, 1);

    // elapsed: 24 at bit 80
    TestDecoderTyphoon::setBits(bits, 80, 7, 24);

    // number: 5 at bit 87
    TestDecoderTyphoon::setBits(bits, 87, 7, 5);

    // scale: 3 at bit 94
    TestDecoderTyphoon::setBits(bits, 94, 4, 3);

    // intensity: 2 at bit 98
    TestDecoderTyphoon::setBits(bits, 98, 4, 2);

    // position 1: 北緯25度, 東経130度 (1度単位)
    // lat_s=0 (北), lat_d=25, lon_s=0 (東), lon_d=130 at bit 102
    TestDecoderTyphoon::setBits(bits, 102, 1, 0);       // lat_sign = 0
    TestDecoderTyphoon::setBits(bits, 103, 8, 25);      // lat_d = 25
    TestDecoderTyphoon::setBits(bits, 111, 1, 0);       // lon_sign = 0
    TestDecoderTyphoon::setBits(bits, 112, 9, 130);     // lon_d = 130

    // 直接decodeTyphoonを呼び出す（CRCチェックを回避）
    // 2024-01-01 00:00:00 UTC
    TestDecoderTyphoon::testDecodeTyphoon(bits, msg, 1704067200u);

    // 結果を検証
    CHECK(msg.mt43.typh.ref_type == 1);
    CHECK(msg.mt43.typh.elapsed == 24);
    CHECK(msg.mt43.typh.number == 5);
    CHECK(msg.mt43.typh.scale == 3);
    CHECK(msg.mt43.typh.intensity == 2);
    // 座標の検証
    CHECK(msg.mt43.typh.coords.lat_ns == 0);   // 北緯
    CHECK(msg.mt43.typh.coords.lat_deg == 25);
    CHECK(msg.mt43.typh.coords.lon_ew == 0);   // 東経
    CHECK(msg.mt43.typh.coords.lon_deg == 130);
}

TEST_CASE("decodeTyphoon: 無効なデータの処理") {
    uint8_t bits[32] = {};
    Message msg{};

    // 最小限の設定
    TestDecoderTyphoon::setBits(bits, 8, 6, 43);        // msg_type
    TestDecoderTyphoon::setBits(bits, 17, 4, 12);       // disaster_category
    TestDecoderTyphoon::setBits(bits, 214, 6, 1);      // version

    TestDecoderTyphoon::testDecodeTyphoon(bits, msg, 1704067200u);

    // 少なくともクラッシュしないことを確認
    CHECK(true);
}
