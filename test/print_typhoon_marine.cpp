// print_typhoon_marine.cpp — 台風・海洋デコード結果の出力
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

int main() {
    // 台風 (disaster_category=12) のテストベクトルを作成
    // 実際のNMEAメッセージ例（仮のデータ）
    // プリアンブル: 0x53, MT:43, DC:12 (0b1100)
    // 実際のデータは仕様書から取る必要があるが、ここでは既存のテスト形式に合わせる
    // ただし、チェックサムが必要なので、実際のメッセージを使用
    
    // 海洋 (disaster_category=14) のテストベクトルも同様
    
    // まず、既存のテストで台風・海洋のメッセージがあるか確認
    // ない場合は、仮のメッセージを構築
    
    printf("Typhoon and Marine tests require actual NMEA vectors.\n");
    printf("Please provide actual test vectors for disaster_category=12 and 14.\n");
    
    return 0;
}
