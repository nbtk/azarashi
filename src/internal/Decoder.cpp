
// azaraC - src/internal/Decoder.cpp
// MT43 bit offsets: IS-QZSS-DCR-010, verified against azarashi 0.15.1 source.
// MT44 bit offsets: IS-QZSS-DCX-005.

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
// MT=44 DCX / CAMF  (IS-QZSS-DCX-005)
// ---------------------------------------------------------------------------
bool Decoder::decodeDcx(const uint8_t* bits, Message& out, uint32_t now_unix) {
    out.dcx_type        = static_cast<DcxType>(getBits(bits, 14, 3));
    out.a1_message_type = getBits(bits, 17, 4);
    out.a2_country_code = getBits(bits, 21, 10);
    out.a3_provider     = getBits(bits, 31,  4);
    out.a4_hazard       = getBits(bits, 35,  7);
    out.a5_severity     = getBits(bits, 42,  2);
    out.a6_onset_week   = getBits(bits, 44,  2);
    out.a7_onset_minute = getBits(bits, 46, 14);
    out.a8_duration     = getBits(bits, 60,  4);

    // Resolve onset time from GPS week-mod-4 + minute-of-week
    if (out.a7_onset_minute > 0 && out.a7_onset_minute <= 10080 && now_unix > 315964800u) {
        // GPS epoch 1980-01-06 00:00:00 UTC, +18 leap seconds (post-2017)
        uint32_t gps  = now_unix - 315964800u + 18u;
        uint32_t week = gps / 604800u;
        int32_t diff = (int32_t)(out.a6_onset_week & 3u) - (int32_t)(week & 3u);
        if (diff < -2) diff += 4;
        else if (diff > 1) diff -= 4;
        uint32_t base = week + diff;

        uint32_t gps_onset = base * 604800u + (uint32_t)(out.a7_onset_minute - 1u) * 60u;
        uint32_t unix = gps_onset + 315964800u - 18u;
        out.onset_time.unix_time = unix;

        uint32_t y, m, d;
        civil_from_days(unix / 86400u, y, m, d);
        out.onset_time.day    = d;
        out.onset_time.hour   = ((out.a7_onset_minute - 1u) % 1440u) / 60u;
        out.onset_time.minute = (out.a7_onset_minute - 1u) % 60u;
    }

    // Ellipse centre for L-Alert / J-Alert
    if (out.dcx_type == DcxType::L_ALERT || out.dcx_type == DcxType::J_ALERT) {
        // A11 library (14 bits) at [67], A12 lat at [81] (14-bit signed), A13 lon at [95] (15-bit signed)
        uint32_t raw12 = getBits(bits, 81, 14);
        if (raw12 & 0x2000u) raw12 |= 0xFFFFC000u;
        out.a12_lat_e2 = (int16_t)raw12;

        uint32_t raw13 = getBits(bits, 95, 15);
        if (raw13 & 0x4000u) raw13 |= 0xFFFF8000u;
        out.a13_lon_e2 = (int16_t)raw13;
    }

    out.valid = true;
    return true;
}

// ---------------------------------------------------------------------------
// MT=43 QZQSM / DC Report  (IS-QZSS-DCR-010)
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
    out.eew_notification_count = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t co = getBits(b, 53 + i * 9, 9);
        if (co == 0) break;
        if (out.eew_notification_count < 3)
            out.eew_notification[out.eew_notification_count++] = co;
    }

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
// Hypocenter  (disaster_category == 4)
// ---------------------------------------------------------------------------
void Decoder::decodeHypocenter(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.hypo_notification_count = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t co = getBits(b, 53 + i * 9, 9);
        if (co == 0) break;
        out.hypo_notification[out.hypo_notification_count++] = co;
    }
    out.hypo_quake_time = extractDHM(b,  80, now_unix);
    out.hypo_depth      = getBits(b,  96, 9);
    out.hypo_magnitude  = getBits(b, 105, 7);
    out.hypo_epicenter  = getBits(b, 112, 10);
    out.hypo_coords     = extractLatLon(b, 122);  // 41 bits
}

// ---------------------------------------------------------------------------
// Seismic Intensity  (disaster_category == 5)
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
// Nankai Trough  (disaster_category == 6)
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
// Tsunami  (disaster_category == 2)
// arrival time sub-field: nextday(1)+hour(5)+minute(6) = 12 bits
// ---------------------------------------------------------------------------
void Decoder::decodeTsunami(const uint8_t* b, Message& out, uint32_t now_unix) {
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

        if (e.arrival_time_raw != 0 && out.event_time.day != 0) {
            uint8_t next = (e.arrival_time_raw >> 11) & 1;
            uint8_t hour = (e.arrival_time_raw >> 6) & 0x1F;
            uint8_t min  = e.arrival_time_raw & 0x3F;
            e.arrival_time = resolveTime(0, out.event_time.day + next, hour, min, now_unix);
        }
    }
}

// ---------------------------------------------------------------------------
// NW Pacific Tsunami  (disaster_category == 3)
// ---------------------------------------------------------------------------
void Decoder::decodeNwPacTsu(const uint8_t* b, Message& out, uint32_t now_unix) {
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

        if (e.arrival_time_raw != 0 && out.event_time.day != 0) {
            uint8_t next = (e.arrival_time_raw >> 11) & 1;
            uint8_t hour = (e.arrival_time_raw >> 6) & 0x1F;
            uint8_t min  = e.arrival_time_raw & 0x3F;
            e.arrival_time = resolveTime(0, out.event_time.day + next, hour, min, now_unix);
        }
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
// Marine  (disaster_category == 12)
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
// Typhoon  (disaster_category == 14)
// ---------------------------------------------------------------------------
void Decoder::decodeTyphoon(const uint8_t* b, Message& out, uint32_t now_unix) {
    out.typh_reference_time = extractDHM(b, 53, now_unix);
    out.typh_ref_type  = getBits(b,  69, 3);
    out.typh_elapsed   = getBits(b,  80, 7);
    out.typh_number    = getBits(b,  87, 7);
    out.typh_scale     = getBits(b,  94, 4);
    out.typh_intensity = getBits(b,  98, 4);

    // Centre position [102..121]: lat_sign(1)+lat_deg(8)+lon_sign(1)+lon_deg(9)
    // IS-QZSS-DCR-010: Typhoon position unit is 1 degree.
    // We store as lat_e1 (0.1 deg unit), so multiply by 10.
    out.typh_pos_count = 0;
    for (uint8_t i = 0; i < 3 && out.typh_pos_count < 3; ++i) {
        uint16_t off = 102 + i * 19;
        if (getBits(b, off, 19) == 0) break;
        uint8_t  lat_s = getBits(b, off,      1);
        uint16_t lat_v = getBits(b, off +  1, 8);  // 1 deg unit
        uint8_t  lon_s = getBits(b, off +  9, 1);
        uint16_t lon_v = getBits(b, off + 10, 9);
        out.typh_positions[out.typh_pos_count].lat_e1 = (lat_s ? -(int16_t)lat_v : (int16_t)lat_v) * 10;
        out.typh_positions[out.typh_pos_count].lon_e1 = (lon_s ? -(int16_t)lon_v : (int16_t)lon_v) * 10;
        ++out.typh_pos_count;
    }
}

} // namespace internal
} // namespace azaraC
