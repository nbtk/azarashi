// azaraC - src/internal/Decoder.cpp
// Common decoder utilities (CRC, bit extraction, time resolution)

#include "Decoder.h"

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// CRC-24Q  (generator 0x1864CFB, GPS/QZSS standard)
// ---------------------------------------------------------------------------
static constexpr uint32_t CRC24Q_POLY = 0x1864CFBu;

uint32_t Decoder::crc24q(const uint8_t* data, uint16_t bit_len) {
    uint32_t crc = 0;
    uint16_t bytes = (bit_len + 7u) / 8u;
    for (uint16_t i = 0; i < bytes; ++i) {
        uint8_t byte = data[i];
        uint8_t bits_to_process = 8;
        if (i == bytes - 1u && (bit_len & 7u)) {
            byte &= 0xFFu << (8u - (bit_len & 7u));
            bits_to_process = bit_len & 7u;
        }
        crc ^= (uint32_t)byte << 16;
        for (uint8_t j = 0; j < bits_to_process; ++j) {
            crc <<= 1;
            if (crc & 0x1000000u) crc ^= CRC24Q_POLY;
        }
    }
    return crc & 0xFFFFFFu;
}

// ---------------------------------------------------------------------------
// Bit extraction (MSB-first, 0-indexed)
// ---------------------------------------------------------------------------
uint32_t Decoder::getBits(const uint8_t* buf, uint16_t start, uint8_t len) {
    uint32_t val = 0;
    for (uint8_t i = 0; i < len; ++i) {
        uint16_t pos = start + i;
        val = (val << 1) | ((buf[pos >> 3] >> (7u - (pos & 7u))) & 1u);
    }
    return val;
}

// ---------------------------------------------------------------------------
// 64-bit bit extraction (MSB-first, 0-indexed) — for fields > 32 bits
// ---------------------------------------------------------------------------
uint64_t Decoder::getBits64(const uint8_t* buf, uint16_t start, uint8_t len) {
    uint64_t val = 0;
    for (uint8_t i = 0; i < len; ++i) {
        uint16_t pos = start + i;
        val = (val << 1) | ((buf[pos >> 3] >> (7u - (pos & 7u))) & 1u);
    }
    return val;
}

// ---------------------------------------------------------------------------
// Signed bit extraction (two's complement, MSB-first)
// ---------------------------------------------------------------------------
int32_t Decoder::getSignedBits(const uint8_t* buf, uint16_t start, uint8_t len) {
    uint32_t val = getBits(buf, start, len);
    if (val & (1u << (len - 1))) {
        val |= 0xFFFFFFFFu << len;  // 符号拡張
    }
    return (int32_t)val;
}

// ---------------------------------------------------------------------------
// Extract signed lat/lon pair from bitstream
// Layout: lat_sign(1) lat_value(lat_bits) lon_sign(1) lon_value(lon_bits)
// Result is in 0.1-degree units (multiply by 10)
// ---------------------------------------------------------------------------
void Decoder::extractSignedLatLon(const uint8_t* buf, uint16_t start, int16_t& lat_e1, int16_t& lon_e1,
                                     uint8_t lat_bits, uint8_t lon_bits) {
    uint8_t  lat_s = getBits(buf, start, 1);
    uint16_t lat_v = getBits(buf, start + 1, lat_bits);
    uint8_t  lon_s = getBits(buf, start + 1 + lat_bits, 1);
    uint16_t lon_v = getBits(buf, start + 2 + lat_bits, lon_bits);
    lat_e1 = (lat_s ? -(int16_t)lat_v : (int16_t)lat_v) * 10;
    lon_e1 = (lon_s ? -(int16_t)lon_v : (int16_t)lon_v) * 10;
}

// Simple civil date to days since 1970-01-01
void Decoder::civil_from_days(uint32_t days_since_1970, uint32_t& y, uint32_t& m, uint32_t& d) {
    uint32_t z = days_since_1970 + 719468u;
    uint32_t era = z / 146097u;
    uint32_t doe = z - era * 146097u;
    uint32_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    y = yoe + era * 400;
    uint32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    uint32_t mp = (5 * doy + 2) / 153;
    d = doy - (153 * mp + 2) / 5 + 1;
    m = mp + (mp < 10 ? 3 : -9);
    y += (m <= 2);
}

uint32_t Decoder::days_from_civil(uint32_t y, uint32_t m, uint32_t d) {
    y -= (m <= 2);
    uint32_t era = y / 400;
    uint32_t yoe = y - era * 400;
    uint32_t doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + doe - 719468;
}

// ---------------------------------------------------------------------------
// LatLon — 41 bits: lat_ns(1) lat_d(7) lat_m(6) lat_s(6) lon_ew(1) lon_d(8) lon_m(6) lon_s(6)
// ---------------------------------------------------------------------------
LatLon Decoder::extractLatLon(const uint8_t* buf, uint16_t start) {
    LatLon ll{};
    ll.lat_ns  = getBits(buf, start,      1);
    ll.lat_deg = getBits(buf, start +  1, 7);
    ll.lat_min = getBits(buf, start +  8, 6);
    ll.lat_sec = getBits(buf, start + 14, 6);
    ll.lon_ew  = getBits(buf, start + 20, 1);
    ll.lon_deg = getBits(buf, start + 21, 8);
    ll.lon_min = getBits(buf, start + 29, 6);
    ll.lon_sec = getBits(buf, start + 35, 6);
    return ll;
}

// ---------------------------------------------------------------------------
// day(5)+hour(5)+min(6) = 16 bits -> TimeFields
// ---------------------------------------------------------------------------
TimeFields Decoder::extractDHM(const uint8_t* buf, uint16_t start, uint32_t report_unix) {
    uint8_t d = getBits(buf, start,      5);
    uint8_t h = getBits(buf, start +  5, 5);
    uint8_t m = getBits(buf, start + 10, 6);
    return resolveTime(0, d, h, m, report_unix);
}

// Resolve time using report_time as baseline.
// report_unix: UNIX time from GPS module (recommended) or SNTP
//   - If >= 2000-01-01 (946684800): use as baseline for year/month resolution
//   - If < 2000-01-01: return with unix_time = 0 (unresolved)
// GPS time is preferred for Arduino/ESP32 targets where internal RTC is unreliable.
TimeFields Decoder::resolveTime(uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint32_t report_unix) {
    TimeFields t{month, day, hour, minute, 0};
    // Basic sanity
    if (day < 1 || day > 31 || hour > 23 || minute > 59 || (month > 12 && month != 0)) {
        t.day = t.hour = t.minute = 0;
        return t;
    }

    // Skip year resolution if baseline is invalid or uninitialized (e.g. before 2000-01-01)
    if (report_unix < 946684800u) {
        return t; // unix_time remains 0
    }

    uint32_t base_unix = report_unix;

    uint32_t base_days = base_unix / 86400u;
    uint32_t y, m, d;
    civil_from_days(base_days, y, m, d);

    if (month == 0) {
        // Month not provided (DHM only): resolve month/year from base with day-wrap correction
        int32_t diff = (int32_t)day - (int32_t)d;
        if (diff > 15) {
            if (m == 1) { m = 12; y--; } else { m--; }
        } else if (diff < -15) {
            if (m == 12) { m = 1; y++; } else { m++; }
        }
    } else {
        // Month provided (MDHM): resolve year from base with month-wrap correction
        uint32_t cur_m = m;
        m = month;
        int32_t diff = (int32_t)month - (int32_t)cur_m;
        if      (diff >  6) y--;
        else if (diff < -6) y++;
    }

    // Normalize date (e.g. resolve Feb 29 to Mar 1 in non-leap years)
    uint32_t resolved_days = days_from_civil(y, m, day);
    civil_from_days(resolved_days, y, m, d);

    t.unix_time = resolved_days * 86400u + (uint32_t)hour * 3600u + (uint32_t)minute * 60u;
    t.day = d;   // update to normalized day
    t.month = m; // update to normalized month
    return t;
}

// ---------------------------------------------------------------------------
// Arrival time: 12-bit field (day_offset:1, hour:5, min:6) -> TimeFields
// ---------------------------------------------------------------------------
TimeFields Decoder::resolveArrivalTime(uint16_t raw, uint32_t base_unix) {
    TimeFields t{};
    if (raw == 0) return t;

    uint8_t next = (raw >> 11) & 1;
    uint8_t hour = (raw >>  6) & 0x1F;
    uint8_t min  = raw & 0x3F;

    if (hour > 23 || min > 59) return t;

    // Skip year/month resolution if base_unix is invalid (e.g. before 2000-01-01)
    if (base_unix < 946684800u) {
        t.hour = hour;
        t.minute = min;
        return t; // unix_time, month, day remain 0 (unresolved)
    }

    uint32_t base_days = base_unix / 86400u;
    uint32_t arrival_days = base_days + next;
    uint32_t y, m, d;
    civil_from_days(arrival_days, y, m, d);

    t.day = d;
    t.hour = hour;
    t.minute = min;
    t.unix_time = arrival_days * 86400u + (uint32_t)hour * 3600u + (uint32_t)min * 60u;
    return t;
}

// ---------------------------------------------------------------------------
// Read up to 3 notification codes (9 bits each) starting at bit offset
// Returns count of valid codes read
// ---------------------------------------------------------------------------
uint8_t Decoder::readNotifications(const uint8_t* b, uint16_t start, uint16_t* notification) {
    uint8_t count = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t co = getBits(b, start + i * 9, 9);
        if (co == 0) break;
        notification[count++] = co;
    }
    return count;
}

// ---------------------------------------------------------------------------
// Main decode entry
// ---------------------------------------------------------------------------
bool Decoder::decode(const Frame& frame, Message& out, uint32_t report_unix) {
    const uint8_t* bits = frame.bits;

    // L1S subframe: CRC-24Q covers bits [0..225], CRC stored at [226..249]
    uint32_t calc = crc24q(bits, 226);
    uint32_t recv = getBits(bits, 226, 24);
    if (calc != recv) return false;

    out         = {};
    out.svid    = frame.svid;
    out.crc24   = recv;
    out.valid   = false;
    out.payload_type = MsgPayloadType::Empty;

    uint8_t preamble = getBits(bits, 0, 8);
    if (preamble != 0x53 && preamble != 0x9A && preamble != 0xC6) return false;  // IS-QZSS-L1S §3.2.4

    uint8_t mt = getBits(bits, 8, 6);
    out.msg_type = mt;

    if      (mt == 44) return decodeDcx(bits, out, report_unix);
    else if (mt == 43) return decodeQzqsm(bits, out, report_unix);
    return false;
}

} // namespace internal
} // namespace azaraC
