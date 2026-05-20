
// azaraC - src/internal/Decoder.cpp
// MT43 bit offsets: IS-QZSS-DCR-016, verified against azarashi 0.15.1 source.
// MT44 bit offsets: IS-QZSS-DCX-003.

#include "Decoder.h"
#include <cstring>

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
static void civil_from_days(uint32_t days_since_1970, uint32_t& y, uint32_t& m, uint32_t& d) {
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

static uint32_t days_from_civil(uint32_t y, uint32_t m, uint32_t d) {
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
TimeFields Decoder::extractDHM(const uint8_t* buf, uint16_t start, uint32_t now_unix) {
    uint8_t d = getBits(buf, start,      5);
    uint8_t h = getBits(buf, start +  5, 5);
    uint8_t m = getBits(buf, start + 10, 6);
    return resolveTime(0, d, h, m, now_unix);
}

TimeFields Decoder::resolveTime(uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint32_t now_unix) {
    TimeFields t{day, hour, minute, 0};
    // Basic sanity
    if (day < 1 || day > 31 || hour > 23 || minute > 59 || (month > 12)) {
        t.day = t.hour = t.minute = 0;
        return t;
    }

    if (now_unix == 0) {
        // Use a fixed baseline if now_unix is not provided (2024-01-01)
        now_unix = 1704067200u;
    }

    uint32_t current_days = now_unix / 86400u;
    uint32_t y, m, d;
    civil_from_days(current_days, y, m, d);

    if (month == 0) {
        // Month not provided (DHM only): resolve month/year from now_unix with day-wrap correction
        int32_t diff = (int32_t)day - (int32_t)d;
        if (diff > 15) {
            if (m == 1) { m = 12; y--; } else { m--; }
        } else if (diff < -15) {
            if (m == 12) { m = 1; y++; } else { m++; }
        }
    } else {
        // Month provided (MDHM): resolve year from now_unix with month-wrap correction
        uint32_t cur_m = m; // m already computed at line 112
        m = month;
        int32_t diff = (int32_t)month - (int32_t)cur_m;
        if      (diff >  6) y--;
        else if (diff < -6) y++;
    }

    // Normalize date (e.g. resolve Feb 29 to Mar 1 in non-leap years)
    uint32_t resolved_days = days_from_civil(y, m, day);
    civil_from_days(resolved_days, y, m, d);

    t.unix_time = resolved_days * 86400u + (uint32_t)hour * 3600u + (uint32_t)minute * 60u;
    t.day = d; // update to normalized day
    return t;
}

// ---------------------------------------------------------------------------
// Arrival time: 12-bit field (day_offset:1, hour:5, min:6) -> TimeFields
// ---------------------------------------------------------------------------
TimeFields Decoder::resolveArrivalTime(uint16_t raw, uint32_t base_unix) {
    TimeFields t{};
    if (raw == 0 || base_unix == 0) return t;

    uint8_t next = (raw >> 11) & 1;
    uint8_t hour = (raw >>  6) & 0x1F;
    uint8_t min  = raw & 0x3F;

    if (hour > 23 || min > 59) return t;

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
bool Decoder::decode(const Frame& frame, Message& out, uint32_t now_unix) {
    const uint8_t* bits = frame.bits;

    // L1S subframe: CRC-24Q covers bits [0..225], CRC stored at [226..249]
    uint32_t calc = crc24q(bits, 226);
    uint32_t recv = getBits(bits, 226, 24);
    if (calc != recv) return false;

    out         = {};
    out.svid    = frame.svid;
    out.crc24   = recv;
    out.valid   = false;

    uint8_t preamble = getBits(bits, 0, 8);
    if (preamble != 0x53 && preamble != 0x9A && preamble != 0xC6) return false;  // IS-QZSS-L1S §3.2.4

    uint8_t mt = getBits(bits, 8, 6);
    out.msg_type = mt;

    if      (mt == 44) return decodeDcx(bits, out, now_unix);
    else if (mt == 43) return decodeQzqsm(bits, out, now_unix);
    return false;
}

// ---------------------------------------------------------------------------
// MT=44 DCX / CAMF  (IS-QZSS-DCX-003)
// ---------------------------------------------------------------------------
bool Decoder::decodeDcx(const uint8_t* bits, Message& out, uint32_t now_unix) {
    out.service_kind = Mt44ServiceKind::Unknown;
    out.is_null_message = false;
    out.ex_kind = ExtendedKind::None;

    // SD (Satellite Designation)
    out.sd.sdmt = getBits(bits, 14, 1);
    out.sd.sdm  = getBits(bits, 15, 9);

    // CAMF (A1 - A18)
    out.camf.a1  = getBits(bits, 24, 2);
    out.camf.a2  = getBits(bits, 26, 9);
    out.camf.a3  = getBits(bits, 35, 5);
    out.camf.a4  = getBits(bits, 40, 7);
    out.camf.a5  = getBits(bits, 47, 2);
    out.camf.a6  = getBits(bits, 49, 1);
    out.camf.a7  = getBits(bits, 50, 14);
    out.camf.a8  = getBits(bits, 64, 2);
    out.camf.a9  = getBits(bits, 66, 1);
    out.camf.a10 = getBits(bits, 67, 3);
    out.camf.a11 = getBits(bits, 70, 10);
    out.camf.a12 = getSignedBits(bits, 80, 16);
    out.camf.a13 = getSignedBits(bits, 96, 17);
    out.camf.a14 = getBits(bits, 113, 5);
    out.camf.a15 = getBits(bits, 118, 5);
    out.camf.a16 = getBits(bits, 123, 6);
    out.camf.a17 = getBits(bits, 129, 2);
    out.camf.a18 = getBits(bits, 131, 15);

    // Null Message Check (IS-QZSS-DCX-003 §4.3)
    // All fields except PAB, MT, SD, Reserved, CRC must be 0
    if (out.camf.a1 == 0 && out.camf.a2 == 111 && out.camf.a3 == 0 &&
        out.camf.a4 == 0 && out.camf.a5 == 0 && out.camf.a6 == 0 &&
        out.camf.a7 == 0 && out.camf.a8 == 0 && out.camf.a9 == 0 &&
        out.camf.a10 == 0 && out.camf.a11 == 0 && out.camf.a12 == 0 &&
        out.camf.a13 == 0 && out.camf.a14 == 0 && out.camf.a15 == 0 &&
        out.camf.a16 == 0 && out.camf.a17 == 0 && out.camf.a18 == 0) {
        // Extended Message must also be all 0
        bool ex_all_zero = true;
        if (out.ex_kind == ExtendedKind::LAlertOrLocal) {
            ex_all_zero = (out.ex_lalert_local.ex1 == 0 && out.ex_lalert_local.ex2 == 0 &&
                          out.ex_lalert_local.ex3 == 0 && out.ex_lalert_local.ex4 == 0 &&
                          out.ex_lalert_local.ex5 == 0 && out.ex_lalert_local.ex6 == 0 &&
                          out.ex_lalert_local.ex7 == 0 && out.ex_lalert_local.vn == 0);
        }
        if (ex_all_zero) {
            out.is_null_message = true;
            out.service_kind = Mt44ServiceKind::NullMessage;
            out.ex_kind = ExtendedKind::None;
            out.valid = true;
            return true;
        }
    }

    // Resolve onset time from GPS week-mod-4 + minute-of-week
    if (out.camf.a7 > 0 && out.camf.a7 <= 10080 && now_unix > 315964800u) {
        // GPS epoch 1980-01-06 00:00:00 UTC, +18 leap seconds (post-2017)
        uint32_t gps  = now_unix - 315964800u + 18u;
        uint32_t week = gps / 604800u;
        int32_t diff = (int32_t)(out.camf.a6 & 3u) - (int32_t)(week & 3u);
        if (diff < -2) diff += 4;
        else if (diff > 1) diff -= 4;
        uint32_t base = week + diff;

        uint32_t gps_onset = base * 604800u + (uint32_t)(out.camf.a7 - 1u) * 60u;
        uint32_t unix = gps_onset + 315964800u - 18u;
        out.onset_time.unix_time = unix;

        uint32_t y, m, d;
        civil_from_days(unix / 86400u, y, m, d);
        out.onset_time.day    = d;
        out.onset_time.hour   = ((out.camf.a7 - 1u) % 1440u) / 60u;
        out.onset_time.minute = (out.camf.a7 - 1u) % 60u;
    }

    // Determine Service Kind based on A2 and A3
    if (out.camf.a2 != 111) { // 111 = 001101111 = Japan
        out.service_kind = Mt44ServiceKind::OutsideJapan;
        out.ex_kind = ExtendedKind::OutsideJapan;
    } else {
        if (out.camf.a3 == 1) {
            out.service_kind = Mt44ServiceKind::LAlert;
            out.ex_kind = ExtendedKind::LAlertOrLocal;
        } else if (out.camf.a3 == 2 || out.camf.a3 == 3) {
            out.service_kind = Mt44ServiceKind::JAlert;
            out.ex_kind = ExtendedKind::JAlert;
        } else if (out.camf.a3 == 4) {
            out.service_kind = Mt44ServiceKind::LocalGovernment;
            out.ex_kind = ExtendedKind::LAlertOrLocal;
        } else {
            // Discard message
            return false;
        }
    }

    // Parse Extended Message
    if (out.ex_kind == ExtendedKind::LAlertOrLocal) {
        out.ex_lalert_local.ex1 = getBits(bits, 146, 16);
        out.ex_lalert_local.ex2 = getBits(bits, 162, 1);
        out.ex_lalert_local.ex3 = getSignedBits(bits, 163, 17);
        out.ex_lalert_local.ex4 = getSignedBits(bits, 180, 17);
        out.ex_lalert_local.ex5 = getBits(bits, 197, 5);
        out.ex_lalert_local.ex6 = getBits(bits, 202, 5);
        out.ex_lalert_local.ex7 = getBits(bits, 207, 7);
        out.ex_lalert_local.vn  = getBits(bits, 214, 6);
    } else if (out.ex_kind == ExtendedKind::JAlert) {
        out.ex_jalert.ex8  = getBits(bits, 146, 1);
        uint32_t ex9_hi = getBits(bits, 147, 32);
        uint32_t ex9_lo = getBits(bits, 179, 32);
        out.ex_jalert.ex9  = ((uint64_t)ex9_hi << 32) | ex9_lo;
        out.ex_jalert.ex10 = getBits(bits, 211, 3);
        out.ex_jalert.vn   = getBits(bits, 214, 6);
    } else if (out.ex_kind == ExtendedKind::OutsideJapan) {
        for (int i = 0; i < 8; ++i) {
            out.ex_outside.ex11_raw[i] = getBits(bits, 146 + i * 8, 8);
        }
        out.ex_outside.ex11_raw[8] = getBits(bits, 210, 4) << 4; // remaining 4 bits
        out.ex_outside.vn = getBits(bits, 214, 6);
    }

    out.valid = true;
    return true;
}

// ---------------------------------------------------------------------------
// MT=43 QZQSM / DC Report  (IS-QZSS-DCR-016)
// Outer frame layout (all offsets 0-indexed from preamble):
//   [14..16]  report_classification (3b)
//   [17..20]  disaster_category     (4b)
//   [21..24]  report_time month     (4b)  — not stored, used only for DHM resolve
//   [25..29]  report_time day       (5b)
//   [30..34]  report_time hour      (5b)
//   [35..40]  report_time minute    (6b)
//   [41..42]  information_type      (2b)
//   [43..46]  reserved / sub-type start
//   [214..219] version (6b) — must be 1
// ---------------------------------------------------------------------------
bool Decoder::decodeQzqsm(const uint8_t* bits, Message& out, uint32_t now_unix) {
    uint8_t ver = getBits(bits, 214, 6);
    if (ver != 1) return false;  // unsupported version

    out.report_classification = getBits(bits, 14,  3);
    out.disaster_category     = getBits(bits, 17,  4);
    out.information_type      = getBits(bits, 41,  2);

    // report_time: month(4b)+day(5b)+hour(5b)+min(6b) at bit 21
    uint8_t  rt_month  = getBits(bits, 21, 4);
    uint8_t  rt_day    = getBits(bits, 25, 5);
    uint8_t  rt_hour   = getBits(bits, 30, 5);
    uint8_t  rt_minute = getBits(bits, 35, 6);

    out.event_time = resolveTime(rt_month, rt_day, rt_hour, rt_minute, now_unix);
    uint32_t report_unix = out.event_time.unix_time;

    // Use report_unix as sub_now if available to improve sub-decoder DHM resolution
    uint32_t sub_now = (report_unix > 0) ? report_unix : now_unix;

    switch (out.disaster_category) {
        case  1: decodeEEW       (bits, out, sub_now); break;
        case  2: decodeHypocenter(bits, out, sub_now); break;
        case  3: decodeSeismic   (bits, out, sub_now); break;
        case  4: decodeNankai    (bits, out);           break;
        case  5: decodeTsunami   (bits, out, sub_now); break;
        case  6: decodeNwPacTsu  (bits, out, sub_now); break;
        case  8: decodeVolcano   (bits, out, sub_now); break;
        case  9: decodeAshFall   (bits, out, sub_now); break;
        case 10: decodeWeather   (bits, out);           break;
        case 11: decodeFlood     (bits, out);           break;
        case 12: decodeTyphoon   (bits, out, sub_now); break;
        case 14: decodeMarine    (bits, out);           break;
        default: return false; // Unknown category, cannot decode full message
    }

    out.valid = true;
    return true;
}

// ---------------------------------------------------------------------------
// EEW  (disaster_category == 1)
// ---------------------------------------------------------------------------
void Decoder::decodeEEW(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.eew_long_period_lower = getBits(b, 47, 3);
    out.eew_long_period_upper = getBits(b, 50, 3);

    // notifications: 3 × 9 bits at [53..79]
    out.eew_notification_count = readNotifications(b, 53, out.eew_notification);

    out.eew_quake_time   = extractDHM(b, 80, now_unix);
    out.eew_depth        = getBits(b,  96, 9);
    out.eew_magnitude    = getBits(b, 105, 7);
    out.eew_epicenter    = getBits(b, 112, 10);
    out.eew_intensity_lower = getBits(b, 122, 4);
    out.eew_intensity_upper = getBits(b, 126, 4);

    // EEW forecast regions: 80-bit bitmask at [130..209], bit i set = region (i+1) alerted
    out.eew_region_count = 0;
    for (uint8_t i = 0; i < 80 && out.eew_region_count < 80; ++i) {
        if (getBits(b, 130 + i, 1)) {
            out.eew_regions[out.eew_region_count++] = i + 1;
        }
    }
}

// ---------------------------------------------------------------------------
// Hypocenter  (disaster_category == 2)
// ---------------------------------------------------------------------------
void Decoder::decodeHypocenter(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.hypo_notification_count = readNotifications(b, 53, out.hypo_notification);
    out.hypo_quake_time = extractDHM(b,  80, now_unix);
    out.hypo_depth      = getBits(b,  96, 9);
    out.hypo_magnitude  = getBits(b, 105, 7);
    out.hypo_epicenter  = getBits(b, 112, 10);
    out.hypo_coords     = extractLatLon(b, 122);  // 41 bits
}

// ---------------------------------------------------------------------------
// Seismic Intensity  (disaster_category == 3)
// ---------------------------------------------------------------------------
void Decoder::decodeSeismic(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.seis_quake_time = extractDHM(b, 53, now_unix);  // day(5)+hour(5)+min(6) at [53]
    out.seis_count = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        uint16_t off = 69 + i * 9;
        uint8_t es = getBits(b, off,     3);
        uint8_t pl = getBits(b, off + 3, 6);
        if (es == 0 && pl == 0) break;
        if (out.seis_count < 16) {
            out.seis_entries[out.seis_count].intensity_code  = es;
            out.seis_entries[out.seis_count].prefecture_code = pl;
            ++out.seis_count;
        }
    }
}

// ---------------------------------------------------------------------------
// Nankai Trough  (disaster_category == 4)
// ---------------------------------------------------------------------------
void Decoder::decodeNankai(const uint8_t* b, Message& out) {
    out.nankai_info_code   = getBits(b, 53, 4);
    out.nankai_page        = getBits(b, 201, 6);
    out.nankai_total_page  = getBits(b, 207, 6);
    // 18 bytes of text: bits [57..200] = 18×8 = 144 bits
    for (uint8_t i = 0; i < 18; ++i)
        out.nankai_text[i] = getBits(b, 57 + i * 8, 8);
}

// ---------------------------------------------------------------------------
// Tsunami  (disaster_category == 5)
// arrival time sub-field: nextday(1)+hour(5)+minute(6) = 12 bits
// ---------------------------------------------------------------------------
void Decoder::decodeTsunami(const uint8_t* b, Message& out, uint32_t /*now_unix*/) {
    out.tsunami_warning_code = getBits(b, 80, 4);
    out.tsunami_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 84 + i * 26;
        if (getBits(b, off, 26) == 0) break;
        TsunamiEntry& e = out.tsunamis[out.tsunami_count++];
        // region(10) + height(4) + arrival(12)
        e.region_code      = getBits(b, off,      10);
        e.height_code      = getBits(b, off + 10,  4);
        e.arrival_time_raw = getBits(b, off + 14, 12);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, out.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// NW Pacific Tsunami  (disaster_category == 6)
// ---------------------------------------------------------------------------
void Decoder::decodeNwPacTsu(const uint8_t* b, Message& out, uint32_t /*now_unix*/) {
    out.nw_pac_potential = getBits(b, 53, 3);
    out.nw_pac_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 56 + i * 28;
        if (getBits(b, off, 28) == 0) break;
        NwPacTsunamiEntry& e = out.nw_pac_tsunamis[out.nw_pac_count++];
        // region(7) + arrival(12) + height(9)
        e.region_code      = getBits(b, off,       7);
        e.arrival_time_raw = getBits(b, off +  7, 12);
        e.height_code      = getBits(b, off + 19,  9);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, out.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// Volcano  (disaster_category == 8)
// ---------------------------------------------------------------------------
void Decoder::decodeVolcano(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.vol_ambiguity      = getBits(b, 50, 3);
    out.vol_activity_time  = extractDHM(b, 53, now_unix);
    out.vol_warning_code   = getBits(b, 69, 7);
    out.vol_volcano_name   = getBits(b, 76, 12);
    out.vol_lg_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint32_t lg = getBits(b, 88 + i * 23, 23);
        if (lg == 0) break;
        out.vol_local_govs[out.vol_lg_count++] = lg;
    }
}

// ---------------------------------------------------------------------------
// Ash Fall  (disaster_category == 9)
// ---------------------------------------------------------------------------
void Decoder::decodeAshFall(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.ash_activity_time = extractDHM(b, 53, now_unix);
    out.ash_warning_type  = getBits(b, 69, 2);
    out.ash_volcano_name  = getBits(b, 71, 12);
    out.ash_count = 0;
    for (uint8_t i = 0; i < 4; ++i) {
        uint16_t off = 83 + i * 29;
        if (getBits(b, off, 29) == 0) break;
        out.ash_entries_time[out.ash_count] = getBits(b, off,      3);
        out.ash_entries_code[out.ash_count] = getBits(b, off +  3, 3);
        out.ash_entries_lg  [out.ash_count] = getBits(b, off +  6, 23);
        ++out.ash_count;
    }
}

// ---------------------------------------------------------------------------
// Weather  (disaster_category == 10)
// ---------------------------------------------------------------------------
void Decoder::decodeWeather(const uint8_t* b, Message& out) {
    out.wx_warning_state = getBits(b, 53, 3);
    out.wx_count = 0;
    for (uint8_t i = 0; i < 6; ++i) {
        uint16_t off = 56 + i * 24;
        if (getBits(b, off, 24) == 0) break;
        out.wx_entries[out.wx_count].sub_category = getBits(b, off,      5);
        out.wx_entries[out.wx_count].region_code  = getBits(b, off +  5, 19);
        ++out.wx_count;
    }
}

// ---------------------------------------------------------------------------
// Flood  (disaster_category == 11)
// ---------------------------------------------------------------------------
void Decoder::decodeFlood(const uint8_t* b, Message& out) {
    out.flood_count = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t off = 53 + i * 44;
        if (getBits(b, off, 44) == 0) break;
        out.flood_entries[out.flood_count].warning_level = getBits(b, off, 4);
        // 40-bit region code — read as two 20-bit halves
        uint64_t hi = getBits(b, off +  4, 20);
        uint64_t lo = getBits(b, off + 24, 20);
        out.flood_entries[out.flood_count].region_code = (hi << 20) | lo;
        ++out.flood_count;
    }
}

// ---------------------------------------------------------------------------
// Marine  (disaster_category == 14)
// ---------------------------------------------------------------------------
void Decoder::decodeMarine(const uint8_t* b, Message& out) {
    out.marine_count = 0;
    for (uint8_t i = 0; i < 8; ++i) {
        uint16_t off = 53 + i * 19;
        uint8_t  dw  = getBits(b, off,      5);
        uint16_t pl  = getBits(b, off +  5, 14);
        if (dw == 0 && pl == 0) break;
        out.marine_entries[out.marine_count].warning_code = dw;
        out.marine_entries[out.marine_count].region_code  = pl;
        ++out.marine_count;
    }
}

// ---------------------------------------------------------------------------
// Typhoon  (disaster_category == 12)
// ---------------------------------------------------------------------------
void Decoder::decodeTyphoon(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.typh_reference_time = extractDHM(b, 53, now_unix);
    out.typh_ref_type  = getBits(b,  69, 3);
    out.typh_elapsed   = getBits(b,  80, 7);
    out.typh_number    = getBits(b,  87, 7);
    out.typh_scale     = getBits(b,  94, 4);
    out.typh_intensity = getBits(b,  98, 4);

    // Centre position [102..121]: lat_sign(1)+lat_deg(8)+lon_sign(1)+lon_deg(9)
    // IS-QZSS-DCR-016: Typhoon position unit is 1 degree.
    // We store as lat_e1 (0.1 deg unit), so multiply by 10.
    out.typh_pos_count = 0;
    for (uint8_t i = 0; i < 3 && out.typh_pos_count < 3; ++i) {
        uint16_t off = 102 + i * 19;
        if (getBits(b, off, 19) == 0) break;
        extractSignedLatLon(b, off,
                            out.typh_positions[out.typh_pos_count].lat_e1,
                            out.typh_positions[out.typh_pos_count].lon_e1,
                            8, 9);
        ++out.typh_pos_count;
    }
}

} // namespace internal
} // namespace azaraC
