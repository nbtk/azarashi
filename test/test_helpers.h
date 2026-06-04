// test/test_helpers.h — 共通テストユーティリティ
// 複数のテストファイルで共有するヘルパー関数・クラスを定義

#ifndef TEST_HELPERS_H
#define TEST_HELPERS_H

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include <cstdint>
#include <cstring>

using namespace azaraC;
using namespace azaraC::internal;

// ── ビット操作ヘルパー ────────────────────────────────────────────────────────

inline void setBits(uint8_t* buf, uint16_t start, uint8_t len, uint32_t value) {
    if (len == 0) return;
    for (int i = static_cast<int>(len) - 1; i >= 0; --i) {
        uint16_t pos = start + (len - 1 - i);
        if ((value >> i) & 1) buf[pos >> 3] |=  (1 << (7 - (pos & 7)));
        else                  buf[pos >> 3] &= ~(1 << (7 - (pos & 7)));
    }
}

// ── CRC-24Q リファレンス実装 ──────────────────────────────────────────────────

inline uint32_t crc24qRef(const uint8_t* d, int total_bits) {
    uint32_t crc = 0;
    int bytes = (total_bits + 7) / 8;
    for (int i = 0; i < bytes; i++) {
        uint8_t b = d[i];
        int bits_to_process = 8;
        if (i == bytes - 1 && (total_bits & 7)) {
            b &= 0xFFu << (8 - (total_bits & 7));
            bits_to_process = total_bits & 7;
        }
        crc ^= (uint32_t)b << 16;
        for (int j = 0; j < bits_to_process; j++) {
            crc <<= 1;
            if (crc & 0x1000000) crc ^= 0x1864CFB;
        }
    }
    return crc & 0xFFFFFF;
}

// ── NMEAデコードヘルパー ─────────────────────────────────────────────────────

inline bool decodeNmea(const char* nmea, Message& msg) {
    NmeaFramer framer;
    Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            found = true;
            break;
        }
    }
    if (!found) return false;
    Decoder dec;
    return dec.decode(frame, msg, 0);
}

// ── テスト用デコーダー（protected関数を公開） ─────────────────────────────────

struct TestDecoder : Decoder {
    // CRC計算
    static uint32_t calcCRC(const uint8_t* data, uint16_t bit_len) {
        return crc24q(data, bit_len);
    }

    // ビット抽出
    static uint32_t extractBits(const uint8_t* b, uint16_t s, uint8_t l) {
        return getBits(b, s, l);
    }

    // 各サブデコーダーのテスト用ラッパー
    static void testDecodeEEW(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoder t;
        t.decodeEEW(bits, out, now_unix);
    }

    static void testDecodeHypocenter(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoder t;
        t.decodeHypocenter(bits, out, now_unix);
    }

    static void testDecodeTsunami(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoder t;
        t.decodeTsunami(bits, out, now_unix);
    }

    static void testDecodeNankai(const uint8_t* bits, Message& out) {
        TestDecoder t;
        t.decodeNankai(bits, out);
    }

    static void testDecodeAshFall(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoder t;
        t.decodeAshFall(bits, out, now);
    }

    static void testDecodeFlood(const uint8_t* bits, Message& out) {
        TestDecoder t;
        t.decodeFlood(bits, out);
    }

    static void testDecodeWeather(const uint8_t* bits, Message& out) {
        TestDecoder t;
        t.decodeWeather(bits, out);
    }

    static void testDecodeSeismic(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoder t;
        t.decodeSeismic(bits, out, now);
    }

    static void testDecodeVolcano(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoder t;
        t.decodeVolcano(bits, out, now);
    }

    static void testDecodeNwPacTsu(const uint8_t* bits, Message& out, uint32_t now) {
        TestDecoder t;
        t.decodeNwPacTsu(bits, out, now);
    }

    static void testDecodeTyphoon(const uint8_t* bits, Message& out, uint32_t now_unix) {
        TestDecoder t;
        t.decodeTyphoon(bits, out, now_unix);
    }

    static void testDecodeMarine(const uint8_t* bits, Message& out) {
        TestDecoder t;
        t.decodeMarine(bits, out);
    }

    // 時間解決
    static TimeFields testResolveTime(uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint32_t now_unix) {
        return resolveTime(month, day, hour, minute, now_unix);
    }

    // 緯度経度抽出
    static LatLon testExtractLatLon(const uint8_t* buf, uint16_t start) {
        return extractLatLon(buf, start);
    }

    // 日付変換
    static void testCivilFromDays(uint32_t days, uint32_t& y, uint32_t& m, uint32_t& d) {
        civil_from_days(days, y, m, d);
    }

    static uint32_t testDaysFromCivil(uint32_t y, uint32_t m, uint32_t d) {
        return days_from_civil(y, m, d);
    }
};

// ── 日付計算ヘルパー ─────────────────────────────────────────────────────────

inline void civilFromDays(uint32_t days_since_1970, uint32_t& y, uint32_t& m, uint32_t& d) {
    TestDecoder::testCivilFromDays(days_since_1970, y, m, d);
}

inline uint32_t daysFromCivil(uint32_t y, uint32_t m, uint32_t d) {
    return TestDecoder::testDaysFromCivil(y, m, d);
}

#endif // TEST_HELPERS_H
