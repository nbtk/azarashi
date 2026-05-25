#pragma once
// azaraC - src/internal/Decoder.h

#include "Frame.h"
#include "../Message.h"

namespace azaraC {
namespace internal {

class Decoder {
public:
    bool decode(const Frame& frame, Message& out, uint32_t report_unix = 0);

protected:
    // CRC-24Q (IS-QZSS-L1S §3.2.8)
    static uint32_t crc24q(const uint8_t* data, uint16_t bit_len);

    // Date conversion helpers (civil date <-> days since 1970-01-01)
    static void civil_from_days(uint32_t days_since_1970, uint32_t& y, uint32_t& m, uint32_t& d);
    static uint32_t days_from_civil(uint32_t y, uint32_t m, uint32_t d);

    // Bit extraction helpers (MSB-first, 0-indexed from frame start)
    static uint32_t getBits(const uint8_t* buf, uint16_t start, uint8_t len);
    static uint64_t getBits64(const uint8_t* buf, uint16_t start, uint8_t len);

    // Signed bit extraction (two's complement, MSB-first)
    static int32_t getSignedBits(const uint8_t* buf, uint16_t start, uint8_t len);

    // Extract signed lat/lon pair from bitstream (sign:1, value:lat_bits, sign:1, value:lon_bits)
    static void extractSignedLatLon(const uint8_t* buf, uint16_t start, int16_t& lat_e1, int16_t& lon_e1,
                                     uint8_t lat_bits = 8, uint8_t lon_bits = 9);

    // LatLon from 41-bit field (lat_ns:1, lat_d:7, lat_m:6, lat_s:6, lon_ew:1, lon_d:8, lon_m:6, lon_s:6)
    static LatLon  extractLatLon(const uint8_t* buf, uint16_t start);

    // day(5)+hour(5)+min(6)=16 bit sub-field -> TimeFields
    // report_unix: UNIX time from GPS module (recommended) or SNTP, 0 = unresolved
    static TimeFields extractDHM(const uint8_t* buf, uint16_t start, uint32_t report_unix);

    // Resolve TimeFields from components using report_time as baseline.
    // report_unix: UNIX time from GPS module (recommended) or SNTP
    //   - If >= 2000-01-01: use as baseline for year/month resolution
    //   - If < 2000-01-01: return with unix_time = 0 (unresolved)
    static TimeFields resolveTime(uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint32_t report_unix);

    // Resolve 12-bit arrival time (day_offset:1, hour:5, min:6) into TimeFields
    static TimeFields resolveArrivalTime(uint16_t raw, uint32_t base_unix);

    // Read up to 3 notification codes (9 bits each) starting at bit offset
    static uint8_t readNotifications(const uint8_t* b, uint16_t start, uint16_t* notification);

    bool decodeDcx   (const uint8_t* bits, Message& out, uint32_t report_unix);
    bool decodeQzqsm (const uint8_t* bits, Message& out, uint32_t report_unix);

    // MT=43 JMA sub-decoders
    // report_unix: UNIX time from GPS module for DHM resolution
    void decodeEEW      (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeHypocenter(const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeSeismic  (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeNankai   (const uint8_t* b, Message& out);
    void decodeTsunami  (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeNwPacTsu (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeVolcano  (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeAshFall  (const uint8_t* b, Message& out, uint32_t report_unix);
    void decodeWeather  (const uint8_t* b, Message& out);
    void decodeFlood    (const uint8_t* b, Message& out);
    void decodeMarine   (const uint8_t* b, Message& out);
    void decodeTyphoon  (const uint8_t* b, Message& out, uint32_t report_unix);
};

} // namespace internal
} // namespace azaraC
