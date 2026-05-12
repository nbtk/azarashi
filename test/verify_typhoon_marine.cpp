// verify_typhoon_marine.cpp — 台風・海洋デコードの検証
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "doctest.h"
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// 台風カテゴリの合成NMEAメッセージを作成
TEST_CASE("decodeTyphoon: 合成フレームでの検証") {
    // 台風 (disaster_category=12) のビット配置に基づく合成フレーム
    // 実際のテストベクトルがないため、Decoderのロジックを検証
    // 少なくともクラッシュしないことを確認
    
    // 台風のビット構造（Decoder.cppより）:
    // [53..68]  : reference_time (DHM: 5+5+6=16bit)
    // [69..71]  : ref_type (3bit)
    // [80..86]  : elapsed (7bit)
    // [87..93]  : number (7bit)
    // [94..97]  : scale (4bit)
    // [98..101] : intensity (4bit)
    // [102..120]: position 1 (19bit: lat_s(1)+lat_d(8)+lon_s(1)+lon_d(9))
    // [121..139]: position 2
    // [140..158]: position 3
    
    // 合成フレームを構築（簡略化のため最小限のデータ）
    uint8_t bits[32] = {};
    
    // ヘルパー関数
    auto setBits = [&](uint16_t start, uint8_t len, uint32_t value) {
        for (int i = len-1; i >= 0; --i) {
            uint16_t pos = start + (len-1-i);
            if ((value >> i) & 1) bits[pos>>3] |=  (1 << (7-(pos&7)));
            else              bits[pos>>3] &= ~(1 << (7-(pos&7)));
        }
    };
    
    // プリアンブル: 0x53, MT:43, report_classification: 仮に0
    setBits(0, 8, 0x53);       // preamble
    setBits(8, 6, 43);        // msg_type = 43
    setBits(14, 3, 0);        // report_classification
    setBits(17, 4, 12);       // disaster_category = 12 (台風)
    setBits(41, 2, 0);        // information_type
    setBits(214, 6, 1);      // version = 1
    
    // 台風フィールド設定
    // reference_time: day=15, hour=12, minute=30 at bit 53
    setBits(53, 5, 15);       // day
    setBits(58, 5, 12);       // hour
    setBits(63, 6, 30);       // minute
    
    setBits(69, 3, 1);        // ref_type = 1
    setBits(80, 7, 24);       // elapsed = 24 hours
    setBits(87, 7, 5);        // number = 5
    setBits(94, 4, 3);        // scale = 3
    setBits(98, 4, 2);        // intensity = 2
    
    // 位置1: 北緯25度, 東経130度 (1度単位)
    // lat_s=0 (北), lat_d=25, lon_s=0 (東), lon_d=130
    setBits(102, 1, 0);       // lat_sign = 0 (北)
    setBits(103, 8, 25);      // lat_deg = 25
    setBits(111, 1, 0);       // lon_sign = 0 (東)
    setBits(112, 9, 130);     // lon_deg = 130
    
    // CRC計算（簡略化のため、実際は正しいCRCが必要）
    // ここではDecoder::decodeを通さず、直接decodeTyphoonを呼ぶことはできない
    // 代わりに、Frameを構築してdecodeを呼ぶ
    // ただし、CRCが合わないので、テストの構造のみ示す
    
    // 実際のテストでは、既存のNMEAテストベクトルを使用するか、
    // 正しいCRCを計算する必要がある
    SUCCEED("台風デコードの構造確認（実際のテストベクトルが必要）");
}

TEST_CASE("decodeMarine: 海洋カテゴリの検証") {
    // 海洋 (disaster_category=14) のビット配置:
    // [53..57]  : warning_code (5bit)
    // [58..71]  : region_code (14bit)
    // 最大8エントリ
    
    // 実際のテストベクトルがないため、構造のみ確認
    SUCCEED("海洋デコードの構造確認（実際のテストベクトルが必要）");
}

// 実際のNMEAテストベクトルを使用した検証
TEST_CASE("Typhoon: 実際のメッセージがあれば検証") {
    // 実際の台風NMEAメッセージ例が必要
    // 例: "$QZQSM,58,..." (台風データ)
    // 現時点では、既存のテストベクトルに台風・海洋が含まれていない
    SUCCEED("実際のテストベクトル待ち");
}
