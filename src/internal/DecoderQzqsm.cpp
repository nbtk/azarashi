// azaraC - src/internal/DecoderQzqsm.cpp
// MT=43 QZQSM / DC Report decoder (IS-QZSS-DCR-016)

#include "Decoder.h"

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

    out.payload_type = MsgPayloadType::Mt43;
    Mt43Data& d = out.mt43;

    d.report_classification = getBits(bits, 14,  3);
    d.disaster_category     = getBits(bits, 17,  4);
    d.information_type      = getBits(bits, 41,  2);

    // report_time: month(4b)+day(5b)+hour(5b)+min(6b) at bit 21
    uint8_t  rt_month  = getBits(bits, 21, 4);
    uint8_t  rt_day    = getBits(bits, 25, 5);
    uint8_t  rt_hour   = getBits(bits, 30, 5);
    uint8_t  rt_minute = getBits(bits, 35, 6);

    // Resolve event_time using report_unix as baseline.
    // report_unix should be UNIX time from GPS module (recommended for Arduino/ESP32).
    d.event_time = resolveTime(rt_month, rt_day, rt_hour, rt_minute, report_unix);
    uint32_t event_unix = d.event_time.unix_time;

    // Use event_unix for sub-decoder DHM resolution (report_time baseline)
    uint32_t sub_base = (event_unix > 0) ? event_unix : report_unix;

    switch (d.disaster_category) {
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
    Mt43Data& d = out.mt43;
    d.eew.long_period_lower = getBits(b, 47, 3);
    d.eew.long_period_upper = getBits(b, 50, 3);

    // notifications: 3 × 9 bits at [53..79]
    d.eew.notification_count = readNotifications(b, 53, d.eew.notification);

    d.eew.quake_time   = extractDHM(b, 80, report_unix);
    d.eew.depth        = getBits(b,  96, 9);
    d.eew.magnitude    = getBits(b, 105, 7);
    d.eew.epicenter    = getBits(b, 112, 10);
    d.eew.intensity_lower = getBits(b, 122, 4);
    d.eew.intensity_upper = getBits(b, 126, 4);

    // EEW forecast regions: 80-bit bitmask at [130..209], bit i set = region (i+1) alerted
    d.eew.region_count = 0;
    for (uint8_t i = 0; i < 80 && d.eew.region_count < 80; ++i) {
        if (getBits(b, 130 + i, 1)) {
            d.eew.regions[d.eew.region_count++] = i + 1;
        }
    }
}

// ---------------------------------------------------------------------------
// Hypocenter  (disaster_category == 2)
// ---------------------------------------------------------------------------
void Decoder::decodeHypocenter(const uint8_t* b, Message& out, uint32_t report_unix) {
    Mt43Data& d = out.mt43;
    d.hypo.notification_count = readNotifications(b, 53, d.hypo.notification);
    d.hypo.quake_time = extractDHM(b,  80, report_unix);
    d.hypo.depth      = getBits(b,  96, 9);
    d.hypo.magnitude  = getBits(b, 105, 7);
    d.hypo.epicenter  = getBits(b, 112, 10);
    d.hypo.coords     = extractLatLon(b, 122);  // 41 bits
}

// ---------------------------------------------------------------------------
// Seismic Intensity  (disaster_category == 3)
// ---------------------------------------------------------------------------
void Decoder::decodeSeismic(const uint8_t* b, Message& out, uint32_t report_unix) {
    Mt43Data& d = out.mt43;
    d.seis.quake_time = extractDHM(b, 53, report_unix);  // day(5)+hour(5)+min(6) at [53]
    d.seis.count = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        uint16_t off = 69 + i * 9;
        uint8_t es = getBits(b, off,     3);
        uint8_t pl = getBits(b, off + 3, 6);
        if (es == 0 && pl == 0) break;
        if (d.seis.count < 16) {
            d.seis.entries[d.seis.count].intensity_code  = es;
            d.seis.entries[d.seis.count].prefecture_code = pl;
            ++d.seis.count;
        }
    }
}

// ---------------------------------------------------------------------------
// Nankai Trough  (disaster_category == 4)
// ---------------------------------------------------------------------------
void Decoder::decodeNankai(const uint8_t* b, Message& out) {
    Mt43Data& d = out.mt43;
    d.nankai.info_code   = getBits(b, 53, 4);
    d.nankai.page        = getBits(b, 201, 6);
    d.nankai.total_page  = getBits(b, 207, 6);
    // 18 bytes of text: bits [57..200] = 18×8 = 144 bits
    for (uint8_t i = 0; i < 18; ++i)
        d.nankai.text[i] = getBits(b, 57 + i * 8, 8);
}

// ---------------------------------------------------------------------------
// Tsunami  (disaster_category == 5)
// arrival time sub-field: nextday(1)+hour(5)+minute(6) = 12 bits
// ---------------------------------------------------------------------------
void Decoder::decodeTsunami(const uint8_t* b, Message& out, uint32_t report_unix) {
    (void)report_unix; // Used indirectly via d.event_time.unix_time
    Mt43Data& d = out.mt43;
    d.tsunami.warning_code = getBits(b, 80, 4);
    d.tsunami.count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 84 + i * 26;
        // Terminal decision by region_code only (IS-QZSS-DCR-016: region_code=0 means end)
        uint16_t region = getBits(b, off, 10);
        if (region == 0) break;
        TsunamiEntry& e = d.tsunami.entries[d.tsunami.count++];
        // region(10) + height(4) + arrival(12)
        e.region_code      = region;
        e.height_code      = getBits(b, off + 10,  4);
        e.arrival_time_raw = getBits(b, off + 14, 12);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, d.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// NW Pacific Tsunami  (disaster_category == 6)
// ---------------------------------------------------------------------------
void Decoder::decodeNwPacTsu(const uint8_t* b, Message& out, uint32_t report_unix) {
    (void)report_unix; // Used indirectly via d.event_time.unix_time
    Mt43Data& d = out.mt43;
    d.nw_pac.potential = getBits(b, 53, 3);
    d.nw_pac.count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint16_t off = 56 + i * 28;
        // Terminal decision by region_code only (IS-QZSS-DCR-016: region_code=0 means end)
        uint16_t region = getBits(b, off, 7);
        if (region == 0) break;
        NwPacTsunamiEntry& e = d.nw_pac.entries[d.nw_pac.count++];
        // region(7) + arrival(12) + height(9)
        e.region_code      = region;
        e.arrival_time_raw = getBits(b, off +  7, 12);
        e.height_code      = getBits(b, off + 19,  9);
        e.arrival_time     = resolveArrivalTime(e.arrival_time_raw, d.event_time.unix_time);
    }
}

// ---------------------------------------------------------------------------
// Volcano  (disaster_category == 8)
// ---------------------------------------------------------------------------
void Decoder::decodeVolcano(const uint8_t* b, Message& out, uint32_t report_unix) {
    Mt43Data& d = out.mt43;
    d.vol.ambiguity      = getBits(b, 50, 3);
    d.vol.activity_time  = extractDHM(b, 53, report_unix);
    d.vol.warning_code   = getBits(b, 69, 7);
    d.vol.volcano_name   = getBits(b, 76, 12);
    d.vol.lg_count = 0;
    for (uint8_t i = 0; i < 5; ++i) {
        uint32_t lg = getBits(b, 88 + i * 23, 23);
        if (lg == 0) break;
        d.vol.local_govs[d.vol.lg_count++] = lg;
    }
}

// ---------------------------------------------------------------------------
// Ash Fall  (disaster_category == 9)
// ---------------------------------------------------------------------------
void Decoder::decodeAshFall(const uint8_t* b, Message& out, uint32_t report_unix) {
    Mt43Data& d = out.mt43;
    d.ash.activity_time = extractDHM(b, 53, report_unix);
    d.ash.warning_type  = getBits(b, 69, 2);
    d.ash.volcano_name  = getBits(b, 71, 12);
    d.ash.count = 0;
    for (uint8_t i = 0; i < 4; ++i) {
        uint16_t off = 83 + i * 29;
        if (getBits(b, off, 29) == 0) break;
        d.ash.entries_time[d.ash.count] = getBits(b, off,      3);
        d.ash.entries_code[d.ash.count] = getBits(b, off +  3, 3);
        d.ash.entries_lg  [d.ash.count] = getBits(b, off +  6, 23);
        ++d.ash.count;
    }
}

// ---------------------------------------------------------------------------
// Weather  (disaster_category == 10)
// ---------------------------------------------------------------------------
void Decoder::decodeWeather(const uint8_t* b, Message& out) {
    Mt43Data& d = out.mt43;
    d.wx.warning_state = getBits(b, 53, 3);
    d.wx.count = 0;
    for (uint8_t i = 0; i < 6; ++i) {
        uint16_t off = 56 + i * 24;
        if (getBits(b, off, 24) == 0) break;
        d.wx.entries[d.wx.count].sub_category = getBits(b, off,      5);
        d.wx.entries[d.wx.count].region_code  = getBits(b, off +  5, 19);
        ++d.wx.count;
    }
}

// ---------------------------------------------------------------------------
// Flood  (disaster_category == 11)
// ---------------------------------------------------------------------------
void Decoder::decodeFlood(const uint8_t* b, Message& out) {
    Mt43Data& d = out.mt43;
    d.flood.count = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        uint16_t off = 53 + i * 44;
        // IS-QZSS-DCR-016: If no object, corresponding Lv and Pl are "0".
        // Region 1 Lv Effective Range is 1-15 (0=unused), so 44-bit zero means no entry.
        // Use getBits64 to safely read all 44 bits (getBits only returns uint32_t).
        if (getBits64(b, off, 44) == 0) break;
        d.flood.entries[d.flood.count].warning_level = getBits(b, off, 4);
        // 40-bit region code — read as two 20-bit halves
        uint64_t hi = getBits(b, off +  4, 20);
        uint64_t lo = getBits(b, off + 24, 20);
        d.flood.entries[d.flood.count].region_code = (hi << 20) | lo;
        ++d.flood.count;
    }
}

// ---------------------------------------------------------------------------
// Marine  (disaster_category == 14)
// ---------------------------------------------------------------------------
void Decoder::decodeMarine(const uint8_t* b, Message& out) {
    Mt43Data& d = out.mt43;
    d.marine.count = 0;
    for (uint8_t i = 0; i < 8; ++i) {
        uint16_t off = 53 + i * 19;
        uint8_t  dw  = getBits(b, off,      5);
        uint16_t pl  = getBits(b, off +  5, 14);
        if (dw == 0 && pl == 0) break;
        d.marine.entries[d.marine.count].warning_code = dw;
        d.marine.entries[d.marine.count].region_code  = pl;
        ++d.marine.count;
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
    Mt43Data& d = out.mt43;
    d.typh.reference_time = extractDHM(b, 53, report_unix);
    d.typh.ref_type  = getBits(b,  69, 3);
    // Skip Spare2 [72..79] (8 bits)
    d.typh.elapsed   = getBits(b,  80, 7);
    d.typh.number    = getBits(b,  87, 7);
    d.typh.scale     = getBits(b,  94, 4);
    d.typh.intensity = getBits(b,  98, 4);

    // LatLon: 41 bits at [102..142]
    d.typh.coords = extractLatLon(b, 102);

    // Central Pressure: 11 bits at [143..153]
    d.typh.pressure = getBits(b, 143, 11);

    // Maximum wind speed: 7 bits at [154..160]
    d.typh.max_wind = getBits(b, 154, 7);

    // Maximum wind gust speed: 7 bits at [161..167]
    d.typh.max_gust = getBits(b, 161, 7);
}

} // namespace internal
} // namespace azaraC
