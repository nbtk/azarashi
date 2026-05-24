// azaraC - src/internal/DecoderQzqsm.cpp
// MT=43 QZQSM / DC Report decoder (IS-QZSS-DCR-016)

#include "Decoder.h"
#include <cstring>
#include <cmath>

namespace azaraC {
namespace internal {

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
bool Decoder::decodeQzqsm(const uint8_t* bits, Message& out, uint32_t report_unix) {
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

    // Resolve event_time using report_unix as baseline (azarashi-compatible)
    // If report_unix > 0, use it; otherwise fallback to fixed baseline in resolveTime
    out.event_time = resolveTime(rt_month, rt_day, rt_hour, rt_minute, report_unix);
    uint32_t event_unix = out.event_time.unix_time;

    // Use event_unix for sub-decoder DHM resolution (report_time baseline)
    uint32_t sub_base = (event_unix > 0) ? event_unix : report_unix;

    switch (out.disaster_category) {
        case  1: decodeEEW       (bits, out, sub_base); break;
        case  2: decodeHypocenter(bits, out, sub_base); break;
        case  3: decodeSeismic   (bits, out, sub_base); break;
        case  4: decodeNankai    (bits, out);            break;
        case  5: decodeTsunami   (bits, out, sub_base); break;
        case  6: decodeNwPacTsu  (bits, out, sub_base); break;
        case  8: decodeVolcano   (bits, out, sub_base); break;
        case  9: decodeAshFall   (bits, out, sub_base); break;
        case 10: decodeWeather   (bits, out);            break;
        case 11: decodeFlood     (bits, out);            break;
        case 12: decodeTyphoon   (bits, out, sub_base); break;
        case 14: decodeMarine    (bits, out);            break;
        default: return false; // Unknown category, cannot decode full message
    }

    out.valid = true;
    return true;
}

// ---------------------------------------------------------------------------
// EEW  (disaster_category == 1)
// ---------------------------------------------------------------------------
void Decoder::decodeEEW(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.eew_long_period_lower = getBits(b, 47, 3);
    out.eew_long_period_upper = getBits(b, 50, 3);

    // notifications: 3 × 9 bits at [53..79]
    out.eew_notification_count = readNotifications(b, 53, out.eew_notification);

    out.eew_quake_time   = extractDHM(b, 80, report_unix);
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
void Decoder::decodeHypocenter(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.hypo_notification_count = readNotifications(b, 53, out.hypo_notification);
    out.hypo_quake_time = extractDHM(b,  80, report_unix);
    out.hypo_depth      = getBits(b,  96, 9);
    out.hypo_magnitude  = getBits(b, 105, 7);
    out.hypo_epicenter  = getBits(b, 112, 10);
    out.hypo_coords     = extractLatLon(b, 122);  // 41 bits
}

// ---------------------------------------------------------------------------
// Seismic Intensity  (disaster_category == 3)
// ---------------------------------------------------------------------------
void Decoder::decodeSeismic(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.seis_quake_time = extractDHM(b, 53, report_unix);  // day(5)+hour(5)+min(6) at [53]
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
void Decoder::decodeTsunami(const uint8_t* b, Message& out, uint32_t report_unix) {
    (void)report_unix; // Used indirectly via out.event_time.unix_time
    out.tsunami_warning_code = getBits(b, 80, 4);
    out.tsunami_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 84 + i * 26;
        // Terminal decision by region_code only (IS-QZSS-DCR-016: region_code=0 means end)
        uint16_t region = getBits(b, off, 10);
        if (region == 0) break;
        TsunamiEntry& e = out.tsunamis[out.tsunami_count++];
        // region(10) + height(4) + arrival(12)
        e.region_code      = region;
        e.height_code      = getBits(b, off + 10,  4);
        e.arrival_time_raw = getBits(b, off + 14, 12);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, out.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// NW Pacific Tsunami  (disaster_category == 6)
// ---------------------------------------------------------------------------
void Decoder::decodeNwPacTsu(const uint8_t* b, Message& out, uint32_t report_unix) {
    (void)report_unix; // Used indirectly via out.event_time.unix_time
    out.nw_pac_potential = getBits(b, 53, 3);
    out.nw_pac_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 56 + i * 28;
        // Terminal decision by region_code only (IS-QZSS-DCR-016: region_code=0 means end)
        uint16_t region = getBits(b, off, 7);
        if (region == 0) break;
        NwPacTsunamiEntry& e = out.nw_pac_tsunamis[out.nw_pac_count++];
        // region(7) + arrival(12) + height(9)
        e.region_code      = region;
        e.arrival_time_raw = getBits(b, off +  7, 12);
        e.height_code      = getBits(b, off + 19,  9);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, out.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// Volcano  (disaster_category == 8)
// ---------------------------------------------------------------------------
void Decoder::decodeVolcano(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.vol_ambiguity      = getBits(b, 50, 3);
    out.vol_activity_time  = extractDHM(b, 53, report_unix);
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
void Decoder::decodeAshFall(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.ash_activity_time = extractDHM(b, 53, report_unix);
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
        // IS-QZSS-DCR-016: If no object, corresponding Lv and Pl are "0".
        // Region 1 Lv Effective Range is 1-15 (0=unused), so 44-bit zero means no entry.
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
// IS-QZSS-DCR-016 Table 4.1.2-47
// Bit layout (from preamble):
//   [53..68]  Bt  Reference Time (day(5)+hour(5)+min(6))
//   [69..71]  Dt  Type of Reference Time (3 bits)
//   [72..79]  Spare2 (8 bits)
//   [80..86]  Du  Elapsed Time (7 bits)
//   [87..93]  Tn  Typhoon Number (7 bits)
//   [94..97]  Sr  Scale Category (4 bits)
//   [98..101] Ic  Intensity Category (4 bits)
//   [102..142] LatLon (41 bits): lat_ns(1)+lat_deg(7)+lat_min(6)+lat_sec(6)+lon_ew(1)+lon_deg(8)+lon_min(6)+lon_sec(6)
//   [143..153] Pr  Central Pressure (11 bits, hPa)
//   [154..160] W1  Maximum wind speed (7 bits, m/s)
//   [161..167] W2  Maximum wind gust speed (7 bits, m/s)
//   [168..213] Spare3 (46 bits)
//   [214..219] Vn  Version Number (6 bits)
// ---------------------------------------------------------------------------
void Decoder::decodeTyphoon(const uint8_t* b, Message& out, uint32_t report_unix) {
    out.typh_reference_time = extractDHM(b, 53, report_unix);
    out.typh_ref_type  = getBits(b,  69, 3);
    // Skip Spare2 [72..79] (8 bits)
    out.typh_elapsed   = getBits(b,  80, 7);
    out.typh_number    = getBits(b,  87, 7);
    out.typh_scale     = getBits(b,  94, 4);
    out.typh_intensity = getBits(b,  98, 4);

    // LatLon: 41 bits at [102..142]
    out.typh_coords = extractLatLon(b, 102);

    // Central Pressure: 11 bits at [143..153]
    out.typh_pressure = getBits(b, 143, 11);

    // Maximum wind speed: 7 bits at [154..160]
    out.typh_max_wind = getBits(b, 154, 7);

    // Maximum wind gust speed: 7 bits at [161..167]
    out.typh_max_gust = getBits(b, 161, 7);
}

} // namespace internal
} // namespace azaraC
