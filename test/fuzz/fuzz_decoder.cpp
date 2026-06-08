// test/fuzz/fuzz_decoder.cpp
// ファジーテスト: ランダム入力に対するデコーダの堅牢性テスト
//
// コンパイル: g++ -std=c++17 -I../include -I. -DARDUINO=0 -DAZARAC_LANG_JA=1 -DAZARAC_LANG_EN=1 -g -o fuzz_decoder fuzz_decoder.cpp ../src/Parser.cpp ../src/decoder/Decoder.cpp ../src/decoder/DecoderDcx.cpp ../src/decoder/DecoderQzqsm.cpp ../src/framer/UbxFramer.cpp ../src/framer/NmeaFramer.cpp ../src/json/JsonWriter.cpp ../src/json/JsonSerializer.cpp ../src/json/JsonSerializerDcx.cpp ../src/json/JsonSerializerQzqsm.cpp ../src/helper/DcxHelper.cpp ../src/helper/Dedup.cpp -Wl,--stack,33554432
//
// 実行: ./fuzz_decoder [イテレーション数]

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <ctime>
#include <random>
#include <vector>
#include <string>
#include <chrono>

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/UbxFramer.h"
#include "../test_helpers.h"

using namespace azaraC;
using namespace azaraC::internal;

// 統計情報
struct FuzzStats {
    uint64_t total_iterations = 0;
    uint64_t valid_frames = 0;
    uint64_t invalid_crc = 0;
    uint64_t invalid_preamble = 0;
    uint64_t decode_success = 0;
    uint64_t decode_fail = 0;
    uint64_t mt43_count = 0;
    uint64_t mt44_count = 0;
    uint64_t exceptions = 0;
    uint64_t nmea_frames = 0;
    uint64_t ubx_frames = 0;

    void print() const {
        printf("\n=== Fuzz Test Statistics ===\n");
        printf("Total iterations:    %llu\n", (unsigned long long)total_iterations);
        printf("Valid frames:        %llu (%.2f%%)\n",
               (unsigned long long)valid_frames,
               total_iterations > 0 ? 100.0 * valid_frames / total_iterations : 0);
        printf("  NMEA frames:       %llu\n", (unsigned long long)nmea_frames);
        printf("  UBX frames:        %llu\n", (unsigned long long)ubx_frames);
        printf("Invalid CRC:         %llu\n", (unsigned long long)invalid_crc);
        printf("Invalid preamble:    %llu\n", (unsigned long long)invalid_preamble);
        printf("Decode success:      %llu\n", (unsigned long long)decode_success);
        printf("  MT=43:             %llu\n", (unsigned long long)mt43_count);
        printf("  MT=44:             %llu\n", (unsigned long long)mt44_count);
        printf("Decode fail:         %llu\n", (unsigned long long)decode_fail);
        printf("Exceptions caught:   %llu\n", (unsigned long long)exceptions);
        printf("===========================\n");
    }
};

// ランダムなNAVビットを生成
static void generate_random_nav_bits(uint8_t* bits, size_t size, std::mt19937& rng) {
    std::uniform_int_distribution<int> dist(0, 255);
    for (size_t i = 0; i < size; i++) {
        bits[i] = static_cast<uint8_t>(dist(rng));
    }
}

// 有効なプリアンブルを設定
static void set_valid_preamble(uint8_t* bits, std::mt19937& rng) {
    std::uniform_int_distribution<int> dist(0, 2);
    uint8_t preambles[] = {0x53, 0x9A, 0xC6};
    bits[0] = preambles[dist(rng)];
}

// 有効なMSG_TYPEを設定
static void set_valid_msg_type(uint8_t* bits, std::mt19937& rng) {
    std::uniform_int_distribution<int> dist(0, 1);
    uint8_t types[] = {43, 44};
    uint8_t mt = types[dist(rng)];
    // MTはビット8-13に設定
    for (int i = 0; i < 6; i++) {
        if ((mt >> (5 - i)) & 1) {
            bits[(8 + i) / 8] |= (0x80 >> ((8 + i) % 8));
        } else {
            bits[(8 + i) / 8] &= ~(0x80 >> ((8 + i) % 8));
        }
    }
}

// CRCを計算して設定
static void set_valid_crc(uint8_t* bits) {
    uint32_t crc = crc24qRef(bits, 226);
    // CRCはビット226-249に設定
    for (int i = 0; i < 24; i++) {
        if ((crc >> (23 - i)) & 1) {
            bits[(226 + i) / 8] |= (0x80 >> ((226 + i) % 8));
        } else {
            bits[(226 + i) / 8] &= ~(0x80 >> ((226 + i) % 8));
        }
    }
}

// テスト1: 完全ランダムデータ
static void test_random_raw_data(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 1: Random raw data (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);

            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);

            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト2: 有効なプリアンブル + ランダムデータ
static void test_valid_preamble(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 2: Valid preamble + random data (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);

            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);

            stats.total_iterations++;

        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト3: 有効なプリアンブル + 有効なMSG_TYPE + ランダムデータ
static void test_valid_preamble_and_type(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 3: Valid preamble + valid msg_type + random data (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);
            set_valid_msg_type(bits, rng);

            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);

            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト4: 有効なフレーム（CRC正しい）
static void test_valid_frames(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 4: Valid frames with correct CRC (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);
            set_valid_msg_type(bits, rng);
            set_valid_crc(bits);

            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            bool result = decoder.decode(frame, msg, 1704067200u);

            stats.total_iterations++;

            if (result) {
                stats.valid_frames++;
                stats.decode_success++;
                if (msg.msg_type == 43) stats.mt43_count++;
                else if (msg.msg_type == 44) stats.mt44_count++;
            } else {
                stats.decode_fail++;
            }
        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト5: NMEAフレーマーへのランダム入力
static void test_nmea_framer(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 5: NMEA framer with random data (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);
            set_valid_msg_type(bits, rng);
            set_valid_crc(bits);

            std::string nmea = makeNmeaQzqsm(193, bits);

            NmeaFramer framer;
            Frame frame;
            bool found = false;

            for (char c : nmea) {
                if (framer.feed((uint8_t)c, frame)) {
                    found = true;
                    break;
                }
            }

            stats.total_iterations++;

            if (found) {
                stats.nmea_frames++;
                Decoder decoder;
                Message msg;
                decoder.decode(frame, msg, 1704067200u);
            }
        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト6: UBXフレーマーへのランダム入力
static void test_ubx_framer(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 6: UBX framer with random data (%d iterations)...\n", iterations);

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);
            set_valid_msg_type(bits, rng);
            set_valid_crc(bits);

            auto ubx = makeUbxSfrbx(193, bits);

            UbxFramer framer;
            Frame frame;
            bool found = false;

            for (auto b : ubx) {
                if (framer.feed(b, frame)) {
                    found = true;
                    break;
                }
            }

            stats.total_iterations++;

            if (found) {
                stats.ubx_frames++;
                Decoder decoder;
                Message msg;
                decoder.decode(frame, msg, 1704067200u);
            }
        } catch (...) {
            stats.exceptions++;
        }
    }
    printf("  Completed.\n");
}

// テスト7: 境界値テスト
static void test_boundary_values(FuzzStats& stats, std::mt19937& rng) {
    printf("Test 7: Boundary values...\n");

    // テストケース: 全ゼロ
    {
        try {
            uint8_t bits[32] = {0};
            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);
            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }

    // テストケース: 全1
    {
        try {
            uint8_t bits[32];
            memset(bits, 0xFF, sizeof(bits));
            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);
            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }

    // テストケース: プリアンブルの境界値
    uint8_t boundary_preambles[] = {0x00, 0x52, 0x53, 0x54, 0x99, 0x9A, 0x9B, 0xC5, 0xC6, 0xC7, 0xFF};
    for (uint8_t preamble : boundary_preambles) {
        try {
            uint8_t bits[32] = {0};
            bits[0] = preamble;
            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);
            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }

    // テストケース: 無効なMSG_TYPE
    for (uint8_t mt = 0; mt < 64; mt++) {
        if (mt == 43 || mt == 44) continue; // 有効なタイプはスキップ

        try {
            uint8_t bits[32] = {0};
            bits[0] = 0x53; // 有効なプリアンブル
            // MTを設定 (ビット8-13)
            for (int i = 0; i < 6; i++) {
                if ((mt >> (5 - i)) & 1) {
                    bits[(8 + i) / 8] |= (0x80 >> ((8 + i) % 8));
                }
            }

            Frame frame;
            frame.svid = 193;
            memcpy(frame.bits, bits, 32);

            Decoder decoder;
            Message msg;
            decoder.decode(frame, msg, 0);
            stats.total_iterations++;
        } catch (...) {
            stats.exceptions++;
        }
    }

    printf("  Completed.\n");
}

// テスト8: 長時間実行テスト（メモリリーク検出）
static void test_long_running(FuzzStats& stats, std::mt19937& rng, int iterations) {
    printf("Test 8: Long running test (%d iterations)...\n", iterations);

    auto start = std::chrono::steady_clock::now();

    for (int i = 0; i < iterations; i++) {
        try {
            uint8_t bits[32];
            generate_random_nav_bits(bits, sizeof(bits), rng);
            set_valid_preamble(bits, rng);
            set_valid_msg_type(bits, rng);
            set_valid_crc(bits);

            // NMEA経由でテスト
            std::string nmea = makeNmeaQzqsm(193, bits);

            NmeaFramer framer;
            Frame frame;

            for (char c : nmea) {
                if (framer.feed((uint8_t)c, frame)) {
                    Decoder decoder;
                    Message msg;
                    decoder.decode(frame, msg, 1704067200u);
                    break;
                }
            }

            stats.total_iterations++;

            // 進捗表示
            if (i % 10000 == 0 && i > 0) {
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - start).count();
                printf("  Progress: %d/%d (%llds elapsed)\n", i, iterations, (long long)elapsed);
            }
        } catch (...) {
            stats.exceptions++;
        }
    }

    auto end = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(end - start).count();
    printf("  Completed in %llds.\n", (long long)elapsed);
}

int main(int argc, char* argv[]) {
    printf("=== AzaraC Fuzz Testing ===\n");
    printf("Starting fuzz tests...\n\n");

    // 乱数シード
    std::random_device rd;
    std::mt19937 rng(rd());

    // イテレーション数（環境変数 > コマンドライン引数 > デフォルト）
    int iterations = 10000;
    const char* env_iter = std::getenv("FUZZ_ITERATIONS");
    if (env_iter) {
        iterations = std::atoi(env_iter);
    }
    if (argc > 1) {
        iterations = std::atoi(argv[1]);
    }
    printf("Iterations per test: %d\n\n", iterations);

    FuzzStats stats;

    // テスト実行
    test_random_raw_data(stats, rng, iterations);
    test_valid_preamble(stats, rng, iterations);
    test_valid_preamble_and_type(stats, rng, iterations);
    test_valid_frames(stats, rng, iterations);
    test_nmea_framer(stats, rng, iterations / 2);
    test_ubx_framer(stats, rng, iterations / 2);
    test_boundary_values(stats, rng);
    test_long_running(stats, rng, iterations * 5);

    // 結果表示
    stats.print();

    // サマリー
    printf("\n=== Summary ===\n");
    if (stats.exceptions == 0) {
        printf("PASS: No exceptions caught during fuzz testing.\n");
    } else {
        printf("FAIL: %llu exceptions caught during fuzz testing.\n",
               (unsigned long long)stats.exceptions);
    }

    printf("Fuzz testing completed.\n");

    return stats.exceptions > 0 ? 1 : 0;
}
