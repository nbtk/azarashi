#pragma once
// azaraC - src/internal/Decoder.h

#include "Frame.h"
#include "../Message.h"

namespace azaraC {
namespace internal {

class Decoder {
public:
    bool decode(const Frame& frame, Message& out, uint32_t now_unix = 0);

protected:
    // CRC-24Q (IS-QZSS-L1S §3.2.8)
    static uint32_t crc24q(const uint8_t* data, uint16_t bit_len);

    // Bit extraction helpers (MSB-first, 0-indexed from frame start)
    static uint32_t getBits(const uint8_t* buf, uint16_t start, uint8_t len);

    // LatLon from 41-bit field (lat_ns:1, lat_d:7, lat_m:6, lat_s:6, lon_ew:1, lon_d:8, lon_m:6, lon_s:6)
    static LatLon  extractLatLon(const uint8_t* buf, uint16_t start);

    // day(5)+hour(5)+min(6)=16 bit sub-field -> TimeFields (unix_time needs now_unix)
    static TimeFields extractDHM(const uint8_t* buf, uint16_t start, uint32_t now_unix);

    bool decodeDcx   (const uint8_t* bits, Message& out, uint32_t now_unix);
    bool decodeQzqsm (const uint8_t* bits, Message& out, uint32_t now_unix);

    // MT=43 JMA sub-decoders
    void decodeEEW      (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeHypocenter(const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeSeismic  (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeNankai   (const uint8_t* b, Message& out);
    void decodeTsunami  (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeNwPacTsu (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeVolcano  (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeAshFall  (const uint8_t* b, Message& out, uint32_t now_unix);
    void decodeWeather  (const uint8_t* b, Message& out);
    void decodeFlood    (const uint8_t* b, Message& out);
    void decodeMarine   (const uint8_t* b, Message& out);
    void decodeTyphoon  (const uint8_t* b, Message& out, uint32_t now_unix);
};

} // namespace internal
} // namespace azaraC
