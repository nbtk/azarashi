#pragma once
// azaraC - src/Message.h
// Bit offsets derived from azarashi (IS-QZSS-DCR-010 / IS-QZSS-DCX-005)

#include <cstdint>

namespace azaraC {

// ---- shared sub-structs ------------------------------------------------

struct TimeFields {
    uint8_t  day;     // 1-31 (0 = unresolved)
    uint8_t  hour;    // 0-23
    uint8_t  minute;  // 0-59
    uint32_t unix_time; // 0 = not resolved
};

struct LatLon {
    uint8_t  lat_ns;   // 0=N 1=S
    uint8_t  lat_deg;  // 0-89
    uint8_t  lat_min;  // 0-59
    uint8_t  lat_sec;  // 0-59
    uint8_t  lon_ew;   // 0=E 1=W
    uint16_t lon_deg;  // 0-179
    uint8_t  lon_min;  // 0-59
    uint8_t  lon_sec;  // 0-59
};

// ---- MT=44 DCX type ----------------------------------------------------

enum class DcxType : uint8_t {
    NULL_MSG      = 0,
    L_ALERT       = 1,
    J_ALERT       = 2,
    LOCAL_GOV     = 3,
    OUTSIDE_JAPAN = 4,
    UNKNOWN       = 0xFF,
};

// ---- MT=43 JMA disaster_category mapping (IS-QZSS-DCR-010 Table 5.1.2-1)
//  0=undefined  1=EEW  2=Tsunami  3=TSU(NW Pacific)  4=Hypocenter
//  5=Seismic intensity  6=Nankai trough  8=Volcano  9=Ash fall
//  10=Weather  11=Flood  12=Marine  14=Typhoon
//  (Stored in Message::disaster_category)

// ---- repeating record structs (up to 8 each) ---------------------------

struct TsunamiEntry {
    uint16_t arrival_time_raw; // nextday(1)+hour(5)+minute(6)=12bit packed; 0=unspecified
    uint8_t  height_code;      // qzss_dcr_jma_tsunami_height
    uint16_t region_code;      // qzss_dcr_jma_tsunami_forecast_region
};

struct SeismicEntry {
    uint8_t intensity_code; // qzss_dcr_jma_seismic_intensity
    uint8_t prefecture_code;
};

struct VolcanoLocalGov {
    uint32_t lg_code; // qzss_dcr_jma_local_government (23 bits)
};

struct WeatherEntry {
    uint8_t  sub_category;  // qzss_dcr_jma_weather_related_disaster_sub_category
    uint32_t region_code;   // qzss_dcr_jma_weather_forecast_region (19 bits)
};

struct TyphoonPos {
    int16_t lat_e1;   // ×0.1 deg signed
    int16_t lon_e1;
};

struct FloodEntry {
    uint8_t  warning_level; // qzss_dcr_jma_flood_warning_level
    uint64_t region_code;   // qzss_dcr_jma_flood_forecast_region (40 bits)
};

struct MarineEntry {
    uint8_t  warning_code;  // qzss_dcr_jma_marine_warning_code
    uint16_t region_code;   // qzss_dcr_jma_marine_forecast_region
};

struct NwPacTsunamiEntry {
    uint16_t arrival_time_raw; // nextday(1)+hour(5)+minute(6)=12bit packed; 0=unspecified
    uint16_t height_code;    // qzss_dcr_jma_northwest_pacific_tsunami_height_en (9 bits)
    uint8_t  region_code;    // qzss_dcr_jma_coastal_region_en (7 bits)
};

// ---- main message struct -----------------------------------------------

struct Message {
    // ---- common --------------------------------------------------------
    uint8_t  svid;
    uint8_t  msg_type;    // 43=QZQSM/MT43  44=DCX/MT44
    uint32_t crc24;
    bool     valid;

    // ---- MT=44 DCX / CAMF (IS-QZSS-DCX-005) ----------------------------
    DcxType  dcx_type;
    uint8_t  a1_message_type;
    uint16_t a2_country_code;
    uint8_t  a3_provider;
    uint8_t  a4_hazard;
    uint8_t  a5_severity;
    uint8_t  a6_onset_week;
    uint16_t a7_onset_minute;  // 1-10080  (0 = unspecified)
    uint8_t  a8_duration;
    int16_t  a12_lat_e2;       // ×0.01 deg signed
    int16_t  a13_lon_e2;
    TimeFields onset_time;

    // ---- MT=43 outer frame (IS-QZSS-DCR-010 §5.1) -----------------------
    uint8_t  report_classification;  // bits [14..16]  3 bits
    uint8_t  disaster_category;      // bits [17..20]  4 bits
    uint8_t  information_type;       // bits [41..42]  2 bits
    TimeFields event_time;           // bits [25..40]: day(5)+hour(5)+min(6)
    // version bits [214..219] = 1 (checked by decoder)

    // ---- EEW  (disaster_category == 1) ----------------------------------
    uint8_t  eew_long_period_lower;  // [47..49]  3 bits
    uint8_t  eew_long_period_upper;  // [50..52]  3 bits
    uint16_t eew_notification[3];    // [53..79]  3×9 bits (notification codes, 0=end)
    uint8_t  eew_notification_count;
    TimeFields eew_quake_time;       // [80..95]
    uint16_t eew_depth;              // [96..104]  9 bits (×10 km; 800=深い, 900=不明)
    uint8_t  eew_magnitude;          // [105..111] 7 bits (×0.1; 100=8.0以上)
    uint16_t eew_epicenter;          // [112..121] 10 bits
    uint8_t  eew_intensity_lower;    // [122..125] 4 bits
    uint8_t  eew_intensity_upper;    // [126..129] 4 bits
    uint16_t eew_regions[16];        // [130..169] up to 5×8 bits
    uint8_t  eew_region_count;

    // ---- Tsunami  (disaster_category == 2) ------------------------------
    uint8_t          tsunami_warning_code;    // [80..83]  4 bits
    TsunamiEntry     tsunamis[5];
    uint8_t          tsunami_count;

    // ---- NW Pacific Tsunami  (disaster_category == 3) -------------------
    uint8_t          nw_pac_potential;        // [53..55]  3 bits
    NwPacTsunamiEntry nw_pac_tsunamis[5];
    uint8_t          nw_pac_count;

    // ---- Hypocenter  (disaster_category == 4) ---------------------------
    uint16_t         hypo_notification[3];
    uint8_t          hypo_notification_count;
    TimeFields       hypo_quake_time;         // [80..95]
    uint16_t         hypo_depth;              // [96..104] 9 bits
    uint8_t          hypo_magnitude;          // [105..111] 7 bits
    uint16_t         hypo_epicenter;          // [112..121] 10 bits
    LatLon           hypo_coords;             // [122..]

    // ---- Seismic Intensity  (disaster_category == 5) --------------------
    TimeFields       seis_quake_time;         // [53..68]
    SeismicEntry     seis_entries[16];
    uint8_t          seis_count;

    // ---- Nankai Trough  (disaster_category == 6) ------------------------
    uint8_t          nankai_info_code;        // [53..56] 4 bits
    uint8_t          nankai_text[18];         // [57..200] 18 bytes
    uint8_t          nankai_page;             // [201..206] 6 bits
    uint8_t          nankai_total_page;       // [207..212] 6 bits

    // ---- Volcano  (disaster_category == 8) ------------------------------
    uint8_t          vol_ambiguity;           // [50..52]  3 bits
    TimeFields       vol_activity_time;       // [53..68]
    uint8_t          vol_warning_code;        // [69..75]  7 bits
    uint16_t         vol_volcano_name;        // [76..87] 12 bits
    uint32_t         vol_local_govs[5];       // [88..] up to 5×23 bits
    uint8_t          vol_lg_count;

    // ---- Ash Fall  (disaster_category == 9) -----------------------------
    TimeFields       ash_activity_time;       // [53..68]
    uint8_t          ash_warning_type;        // [69..70]  2 bits (1=速報 2=詳細)
    uint16_t         ash_volcano_name;        // [71..82] 12 bits
    uint8_t          ash_entries_time[4];     // [83..] ×4: arrival_hour(3)
    uint8_t          ash_entries_code[4];     // warning_code(3)
    uint32_t         ash_entries_lg[4];       // local_government(23)
    uint8_t          ash_count;

    // ---- Weather  (disaster_category == 10) ------------------------------
    uint8_t          wx_warning_state;        // [53..55]  3 bits
    WeatherEntry     wx_entries[6];
    uint8_t          wx_count;

    // ---- Flood  (disaster_category == 11) -------------------------------
    FloodEntry       flood_entries[3];
    uint8_t          flood_count;

    // ---- Marine  (disaster_category == 12) ------------------------------
    MarineEntry      marine_entries[8];
    uint8_t          marine_count;

    // ---- Typhoon  (disaster_category == 14) -----------------------------
    TimeFields       typh_reference_time;     // [53..68]
    uint8_t          typh_ref_type;           // [69..71]  3 bits
    uint8_t          typh_elapsed;            // [80..86]  7 bits
    uint8_t          typh_number;             // [87..93]  7 bits
    uint8_t          typh_scale;              // [94..97]  4 bits
    uint8_t          typh_intensity;          // [98..101] 4 bits
    TyphoonPos       typh_positions[3];       // center + forecast ×2
    uint8_t          typh_pos_count;
};

} // namespace azaraC
