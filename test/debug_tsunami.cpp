// debug_tsunami.cpp — 津波到達時刻のデバッグ
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

// ビット抽出のテスト用
uint32_t manualGetBits(const uint8_t* buf, uint16_t start, uint8_t len) {
    uint32_t val = 0;
    for (uint8_t i = 0; i < len; ++i) {
        uint16_t pos = start + i;
        val = (val << 1) | ((buf[pos >> 3] >> (7u - (pos & 7u))) & 1u);
    }
    return val;
}

int main() {
    // 津波テストベクトル
    const char* nmea = "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F\r\n";

    NmeaFramer framer;
    Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            found = true;
            break;
        }
    }
    if (!found) {
        printf("Failed to frame\n");
        return 1;
    }

    // フレームサイズの検証
    if (frame.length < 32) {
        printf("Frame too small: %u bytes (expected 32)\n", frame.length);
        return 1;
    }

    // 生のバイナリデータを16進数で出力
    printf("Raw bytes (32 bytes):\n");
    for (int i = 0; i < 32; i++) {
        printf("%02X ", frame.bits[i]);
        if ((i+1) % 16 == 0) printf("\n");
    }
    printf("\n");

    // オフセット84付近のビットを詳細表示
    printf("\nBits around offset 84 (entry 0 start):\n");
    for (int bit = 80; bit < 120; bit++) {
        uint16_t pos = bit;
        uint8_t bit_val = (frame.bits[pos >> 3] >> (7u - (pos & 7u))) & 1u;
        printf("%d", bit_val);
        if ((bit - 80 + 1) % 26 == 0) printf(" | ");
        else if ((bit - 80 + 1) % 13 == 0) printf(" ");
    }
    printf("\n");

    // エントリ0の各フィールドを手動抽出
    printf("\nManual extraction of entry 0:\n");
    uint16_t off = 84; // 津波エントリの開始オフセット
    uint32_t region = manualGetBits(frame.bits, off, 10); // 地域コード(10ビット)
    uint32_t height = manualGetBits(frame.bits, off + 10, 4); // 津波高さ(4ビット)
    uint32_t arrival = manualGetBits(frame.bits, off + 14, 12); // 津波到達時刻(12ビット: next_day(1) + hour(5) + minute(6))

    printf("  region_code: %u (0x%X)\n", region, region);
    printf("  height_code: %u (0x%X)\n", height, height);
    printf("  arrival_raw: %u (0x%03X)\n", arrival, arrival);

    uint8_t next = (arrival >> 11) & 1;
    uint8_t hour = (arrival >> 6) & 0x1F;
    uint8_t min = arrival & 0x3F;
    printf("  next_day: %u, hour: %u, minute: %u\n", next, hour, min);

    // DecoderのgetBitsもテスト
    printf("\nDecoder::getBits test:\n");
    Decoder dec;
    // リフレクションが使えないので、手動で確認

    // バイト10,11,12を表示
    printf("Bytes 10-12: 0x%02X 0x%02X 0x%02X\n",
           frame.bits[10], frame.bits[11], frame.bits[12]);
    printf("Binary: ");
    for (int i = 10; i <= 12; i++) {
        for (int b = 7; b >= 0; b--) {
            printf("%d", (frame.bits[i] >> b) & 1);
        }
        printf(" ");
    }
    // デコード実行
    Message msg{};
    bool ok = dec.decode(frame, msg, 1704067200u);  // 2024-01-01 00:00:00 UTC

    if (!ok) {
        printf("\nDecode failed\n");
        return 1;
    }

    printf("\nTsunami Decoded Fields:\n");
    printf("  tsunami_warning_code: %u\n", msg.tsunami_warning_code);
    printf("  tsunami_count: %u\n", msg.tsunami_count);

    for (int i = 0; i < msg.tsunami_count; i++) {
        printf("\n  Entry[%d]:\n", i);
        printf("    region_code: %u\n", msg.tsunamis[i].region_code);
        printf("    height_code: %u\n", msg.tsunamis[i].height_code);
        printf("    arrival_time_raw: %u (0x%03X)\n",
               msg.tsunamis[i].arrival_time_raw, msg.tsunamis[i].arrival_time_raw);

        uint16_t raw = msg.tsunamis[i].arrival_time_raw;
        uint8_t next = (raw >> 11) & 1;
        uint8_t hour = (raw >> 6) & 0x1F;
        uint8_t min  = raw & 0x3F;
        printf("    next_day: %u, hour: %u, minute: %u\n", next, hour, min);

        printf("    arrival_time: day=%u hour=%u minute=%u unix=%u\n",
               msg.tsunamis[i].arrival_time.day,
               msg.tsunamis[i].arrival_time.hour,
               msg.tsunamis[i].arrival_time.minute,
               msg.tsunamis[i].arrival_time.unix_time);
    }

    return 0;
}
