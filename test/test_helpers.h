// test/test_helpers.h — 共通テストユーティリティ
// 複数のテストファイルで共有するヘルパー関数・クラスを定義

#ifndef TEST_HELPERS_H
#define TEST_HELPERS_H

#define ARDUINO 0
#include "../include/azaraC.h"
#include "../include/internal/Decoder.h"
#include "../include/internal/NmeaFramer.h"
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>

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

// ── UBX SFRBX パケット生成 ────────────────────────────────────────────────────

inline std::vector<uint8_t> makeUbxSfrbx(uint8_t svId, const uint8_t* nav_bits) {
    std::vector<uint8_t> out;
    out.push_back(0xB5); out.push_back(0x62); // SYNC
    out.push_back(0x02); out.push_back(0x13); // CLASS/ID (RXM-SFRBX)

    uint16_t len = 8 + 8 * 4; // header(8) + 8 words(32)
    out.push_back(len & 0xFF);
    out.push_back(len >> 8);

    // Header
    out.push_back(5);    // gnssId (QZSS)
    out.push_back(svId); // svId
    out.push_back(0);    // sigId (L1S)
    out.push_back(0);    // freqId
    out.push_back(8);    // numWords
    out.push_back(0);    // chn
    out.push_back(1);    // version
    out.push_back(0);    // reserved

    // Payload (8 words)
    for (int w = 0; w < 8; ++w) {
        uint32_t val = 0;
        for (int b = 0; b < 32; ++b) {
            int bit_idx = w * 32 + b;
            if (bit_idx < 250) {
                if (nav_bits[bit_idx / 8] & (0x80u >> (bit_idx % 8))) {
                    val |= (1u << (31 - b));
                }
            }
        }
        out.push_back(val & 0xFF);
        out.push_back((val >> 8) & 0xFF);
        out.push_back((val >> 16) & 0xFF);
        out.push_back(val >> 24);
    }

    // Checksum
    uint8_t cka = 0, ckb = 0;
    for (size_t i = 2; i < out.size(); ++i) {
        cka += out[i];
        ckb += cka;
    }
    out.push_back(cka);
    out.push_back(ckb);

    return out;
}

// ── NMEA QZQSM 文生成 ─────────────────────────────────────────────────────────

inline std::string makeNmeaQzqsm(uint8_t svid, const uint8_t* nav_bits) {
    char buf[256];
    sprintf(buf, "QZQSM,%d,", svid);
    std::string s = "$";
    s += buf;
    // Output 31 full bytes (62 hex chars)
    for (int i = 0; i < 31; ++i) {
        char hex[3];
        sprintf(hex, "%02X", nav_bits[i]);
        s += hex;
    }
    // Output 1 nibble (1 hex char) for the remaining 2 bits
    char hex[2];
    sprintf(hex, "%01X", (nav_bits[31] >> 4) & 0xF);
    s += hex;


    uint8_t xsum = 0;
    for (size_t i = 1; i < s.size(); ++i) {
        xsum ^= (uint8_t)s[i];
    }

    char tail[6];
    snprintf(tail, sizeof(tail), "*%02X\r\n", xsum);
    s += tail;
    return s;
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
