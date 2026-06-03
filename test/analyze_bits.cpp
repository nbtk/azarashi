// test/analyze_bits.cpp
// azarashiテストデータのビット解析
// 各フィールドの値を出力してAzaraCとの差異を確認

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include <cstdio>
#include <cstring>
#include <cstdint>

using namespace azaraC;
using namespace azaraC::internal;

// NMEAデコードヘルパー
bool decodeNmeaHelper(const char* nmea, Message& msg, uint32_t now = 0) {
    NmeaFramer framer;
    Frame frame;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            Decoder dec;
            return dec.decode(frame, msg, now);
        }
    }
    return false;
}

// ビット抽出ヘルパー
uint32_t getBits(const uint8_t* b, uint16_t s, uint8_t l) {
    uint32_t v = 0;
    for (uint16_t i = 0; i < l; i++) {
        uint16_t pos = s + i;
        if (b[pos >> 3] & (1 << (7 - (pos & 7)))) v |= (1u << (l - 1 - i));
    }
    return v;
}

void printSeparator() {
    printf("----------------------------------------\n");
}

int main() {
    printf("=== azarashiテストデータ ビット解析 ===\n\n");
    
    // ═════════════════════════════════════════════════════════════════════════
    // EEW: 9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC
    // ═════════════════════════════════════════════════════════════════════════
    printf("【EEW】 $QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F\n");
    printSeparator();
    
    {
        const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F";
        Message msg{};
        bool ok = decodeNmeaHelper(nmea, msg);
        
        if (ok && msg.valid) {
            printf("デコード成功\n");
            printf("msg_type: %d\n", msg.msg_type);
            printf("disaster_category: %d\n", msg.mt43.disaster_category);
            printf("event_time: month=%d, day=%d, hour=%d, minute=%d\n",
                   msg.mt43.event_time.month, msg.mt43.event_time.day,
                   msg.mt43.event_time.hour, msg.mt43.event_time.minute);
            printf("eew: depth=%d, magnitude=%d, epicenter=%d\n",
                   msg.mt43.eew.depth, msg.mt43.eew.magnitude, msg.mt43.eew.epicenter);
            printf("eew: long_period_lower=%d, long_period_upper=%d\n",
                   msg.mt43.eew.long_period_lower, msg.mt43.eew.long_period_upper);
            
            // 生ビットから直接読み取り
            NmeaFramer framer;
            Frame frame;
            for (int i = 0; nmea[i]; i++) {
                if (framer.feed((uint8_t)nmea[i], frame)) break;
            }
            
            printf("\n生ビット直接読み取り:\n");
            printf("Preamble (0-7): 0x%02X = %d\n", getBits(frame.bits, 0, 8), getBits(frame.bits, 0, 8));
            printf("MT (8-13): %d\n", getBits(frame.bits, 8, 6));
            printf("Report Class (14-16): %d\n", getBits(frame.bits, 14, 3));
            printf("Disaster Cat (17-20): %d\n", getBits(frame.bits, 17, 4));
            printf("Month (21-24): %d\n", getBits(frame.bits, 21, 4));
            printf("Day (25-29): %d\n", getBits(frame.bits, 25, 5));
            printf("Hour (30-34): %d\n", getBits(frame.bits, 30, 5));
            printf("Minute (35-40): %d\n", getBits(frame.bits, 35, 6));
            printf("Info Type (41-42): %d\n", getBits(frame.bits, 41, 2));
            printf("Long Period Lower (47-49): %d\n", getBits(frame.bits, 47, 3));
            printf("Long Period Upper (50-52): %d\n", getBits(frame.bits, 50, 3));
        } else {
            printf("デコード失敗\n");
        }
    }
    
    printf("\n");
    
    // ═════════════════════════════════════════════════════════════════════════
    // Hypocenter: 53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908
    // ═════════════════════════════════════════════════════════════════════════
    printf("【Hypocenter】 $QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01\n");
    printSeparator();
    
    {
        const char* nmea = "$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01";
        Message msg{};
        bool ok = decodeNmeaHelper(nmea, msg);
        
        if (ok && msg.valid) {
            printf("デコード成功\n");
            printf("msg_type: %d\n", msg.msg_type);
            printf("disaster_category: %d\n", msg.mt43.disaster_category);
            printf("event_time: month=%d, day=%d, hour=%d, minute=%d\n",
                   msg.mt43.event_time.month, msg.mt43.event_time.day,
                   msg.mt43.event_time.hour, msg.mt43.event_time.minute);
            printf("hypo: depth=%d, magnitude=%d\n",
                   msg.mt43.hypo.depth, msg.mt43.hypo.magnitude);
            
            // 生ビットから直接読み取り
            NmeaFramer framer;
            Frame frame;
            for (int i = 0; nmea[i]; i++) {
                if (framer.feed((uint8_t)nmea[i], frame)) break;
            }
            
            printf("\n生ビット直接読み取り:\n");
            printf("Preamble (0-7): 0x%02X = %d\n", getBits(frame.bits, 0, 8), getBits(frame.bits, 0, 8));
            printf("MT (8-13): %d\n", getBits(frame.bits, 8, 6));
            printf("Report Class (14-16): %d\n", getBits(frame.bits, 14, 3));
            printf("Disaster Cat (17-20): %d\n", getBits(frame.bits, 17, 4));
            printf("Month (21-24): %d\n", getBits(frame.bits, 21, 4));
            printf("Day (25-29): %d\n", getBits(frame.bits, 25, 5));
            printf("Hour (30-34): %d\n", getBits(frame.bits, 30, 5));
            printf("Minute (35-40): %d\n", getBits(frame.bits, 35, 6));
        } else {
            printf("デコード失敗\n");
        }
    }
    
    printf("\n");
    
    // ═════════════════════════════════════════════════════════════════════════
    // DCX L-Alert: 9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238
    // ═════════════════════════════════════════════════════════════════════════
    printf("【DCX L-Alert】 $QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04\n");
    printSeparator();
    
    {
        const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
        Message msg{};
        bool ok = decodeNmeaHelper(nmea, msg);
        
        if (ok && msg.valid) {
            printf("デコード成功\n");
            printf("msg_type: %d\n", msg.msg_type);
            printf("service_kind: %d\n", (int)msg.mt44.service_kind);
            printf("is_null_message: %d\n", msg.mt44.is_null_message);
            printf("camf.a1: %d\n", msg.mt44.camf.a1);
            printf("camf.a2: %d\n", msg.mt44.camf.a2);
            printf("camf.a3: %d\n", msg.mt44.camf.a3);
            printf("ex_lalert_local.ex1: %d\n", msg.mt44.ex_lalert_local.ex1);
            printf("ex_lalert_local.vn: %d\n", msg.mt44.ex_lalert_local.vn);
            
            // 生ビットから直接読み取り
            NmeaFramer framer;
            Frame frame;
            for (int i = 0; nmea[i]; i++) {
                if (framer.feed((uint8_t)nmea[i], frame)) break;
            }
            
            printf("\n生ビット直接読み取り:\n");
            printf("Preamble (0-7): 0x%02X = %d\n", getBits(frame.bits, 0, 8), getBits(frame.bits, 0, 8));
            printf("MT (8-13): %d\n", getBits(frame.bits, 8, 6));
            printf("SDMT (14): %d\n", getBits(frame.bits, 14, 1));
            printf("SDM (15-23): %d\n", getBits(frame.bits, 15, 9));
            printf("A1 (24-25): %d\n", getBits(frame.bits, 24, 2));
            printf("A2 (26-34): %d\n", getBits(frame.bits, 26, 9));
            printf("A3 (35-39): %d\n", getBits(frame.bits, 35, 5));
            printf("A4 (40-46): %d\n", getBits(frame.bits, 40, 7));
            printf("A5 (47-48): %d\n", getBits(frame.bits, 47, 2));
            printf("A6 (49): %d\n", getBits(frame.bits, 49, 1));
            printf("A7 (50-63): %d\n", getBits(frame.bits, 50, 14));
            printf("A8 (64-65): %d\n", getBits(frame.bits, 64, 2));
            printf("A9 (66): %d\n", getBits(frame.bits, 66, 1));
            printf("A10 (67-69): %d\n", getBits(frame.bits, 67, 3));
            printf("A11 (70-79): %d\n", getBits(frame.bits, 70, 10));
            printf("A12 (80-95): %d\n", getBits(frame.bits, 80, 16));
            printf("A13 (96-112): %d\n", getBits(frame.bits, 96, 17));
            printf("EX1 (146-161): %d\n", getBits(frame.bits, 146, 16));
            printf("VN (214-219): %d\n", getBits(frame.bits, 214, 6));
        } else {
            printf("デコード失敗\n");
        }
    }
    
    printf("\n");
    
    // ═════════════════════════════════════════════════════════════════════════
    // DCX J-Alert: 53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628
    // ═════════════════════════════════════════════════════════════════════════
    printf("【DCX J-Alert】 $QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00\n");
    printSeparator();
    
    {
        const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00";
        Message msg{};
        bool ok = decodeNmeaHelper(nmea, msg);
        
        if (ok && msg.valid) {
            printf("デコード成功\n");
            printf("msg_type: %d\n", msg.msg_type);
            printf("service_kind: %d\n", (int)msg.mt44.service_kind);
            printf("camf.a2: %d\n", msg.mt44.camf.a2);
            printf("camf.a3: %d\n", msg.mt44.camf.a3);
            printf("ex_jalert.ex8: %d\n", msg.mt44.ex_jalert.ex8);
            printf("ex_jalert.ex9: 0x%016llX\n", (unsigned long long)msg.mt44.ex_jalert.ex9);
            printf("ex_jalert.vn: %d\n", msg.mt44.ex_jalert.vn);
            
            // 生ビットから直接読み取り
            NmeaFramer framer;
            Frame frame;
            for (int i = 0; nmea[i]; i++) {
                if (framer.feed((uint8_t)nmea[i], frame)) break;
            }
            
            printf("\n生ビット直接読み取り:\n");
            printf("A3 (35-39): %d\n", getBits(frame.bits, 35, 5));
            printf("EX8 (146): %d\n", getBits(frame.bits, 146, 1));
            uint32_t ex9_hi = getBits(frame.bits, 147, 32);
            uint32_t ex9_lo = getBits(frame.bits, 179, 32);
            printf("EX9 hi (147-178): 0x%08X\n", ex9_hi);
            printf("EX9 lo (179-210): 0x%08X\n", ex9_lo);
            printf("EX9 full: 0x%08X%08X\n", ex9_hi, ex9_lo);
            printf("EX9 >> 17: 0x%016llX\n", (unsigned long long)((uint64_t)ex9_hi << 32 | ex9_lo) >> 17);
            printf("VN (214-219): %d\n", getBits(frame.bits, 214, 6));
        } else {
            printf("デコード失敗\n");
        }
    }
    
    printf("\n");
    
    // ═════════════════════════════════════════════════════════════════════════
    // DCX Outside Japan: 9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410
    // ═════════════════════════════════════════════════════════════════════════
    printf("【DCX Outside Japan】 $QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C\n");
    printSeparator();
    
    {
        const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C";
        Message msg{};
        bool ok = decodeNmeaHelper(nmea, msg);
        
        if (ok && msg.valid) {
            printf("デコード成功\n");
            printf("msg_type: %d\n", msg.msg_type);
            printf("service_kind: %d\n", (int)msg.mt44.service_kind);
            printf("camf.a2: %d\n", msg.mt44.camf.a2);
            printf("ex_outside.vn: %d\n", msg.mt44.ex_outside.vn);
            
            // 生ビットから直接読み取り
            NmeaFramer framer;
            Frame frame;
            for (int i = 0; nmea[i]; i++) {
                if (framer.feed((uint8_t)nmea[i], frame)) break;
            }
            
            printf("\n生ビット直接読み取り:\n");
            printf("A2 (26-34): %d\n", getBits(frame.bits, 26, 9));
            printf("VN (214-219): %d\n", getBits(frame.bits, 214, 6));
        } else {
            printf("デコード失敗\n");
        }
    }
    
    return 0;
}
