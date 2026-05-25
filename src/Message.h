#pragma once
// azaraC - src/Message.h
// Bit offsets derived from azarashi (IS-QZSS-DCR-016 / IS-QZSS-DCX-003)

#include <cstdint>

namespace azaraC {

// ---- shared sub-structs ------------------------------------------------

struct TimeFields {
    uint8_t  month;   // 1-12 (0 = unresolved)
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

enum class Mt44ServiceKind : uint8_t {
    NullMessage,
    LAlert,
    JAlert,
    LocalGovernment,
    OutsideJapan,
    Unknown
};

enum class ExtendedKind : uint8_t {
    None,
    LAlertOrLocal,
    JAlert,
    OutsideJapan
};

struct Mt44Sd {
    uint8_t  sdmt;   // 1 bit
    uint16_t sdm;    // 9 bits
};

struct Mt44CamfRaw {
    uint8_t  a1;    // 2
    uint16_t a2;    // 9
    uint8_t  a3;    // 5
    uint8_t  a4;    // 7
    uint8_t  a5;    // 2
    uint8_t  a6;    // 1
    uint16_t a7;    // 14
    uint8_t  a8;    // 2
    uint8_t  a9;    // 1
    uint8_t  a10;   // 3
    uint16_t a11;   // 10
    uint16_t a12;   // 16 (unsigned, latitude code)
    uint32_t a13;   // 17 (unsigned, longitude code)
    uint8_t  a14;   // 5
    uint8_t  a15;   // 5
    uint8_t  a16;   // 6
    uint8_t  a17;   // 2
    uint16_t a18;   // 15
};

struct Mt44ExLAlertOrLocal {
    uint16_t ex1;   // 16
    uint8_t  ex2;   // 1
    uint32_t ex3;   // 17 unsigned (IS-QZSS-DCX-003 §4.2.4.1.3)
    uint32_t ex4;   // 17 unsigned (IS-QZSS-DCX-003 §4.2.4.1.4)
    uint8_t  ex5;   // 5
    uint8_t  ex6;   // 5
    uint8_t  ex7;   // 7
    uint8_t  vn;    // 6
};

struct Mt44ExJAlert {
    uint8_t  ex8;   // 1
    uint64_t ex9;   // 64
    uint8_t  ex10;  // 3 reserved
    uint8_t  vn;    // 6
};

struct Mt44ExOutside {
    uint8_t ex11_raw[9]; // 68bit raw
    uint8_t vn;          // 6
};

// ---- MT=44 Decoded structures (IS-QZSS-DCX-003) --------------------------

// Decoded ellipse with WGS84 coordinates
struct DecodedEllipse {
    double lat_deg;         // WGS84 latitude in degrees
    double lon_deg;         // WGS84 longitude in degrees
    double semi_major_km;   // Semi-major axis in km
    double semi_minor_km;   // Semi-minor axis in km
    double azimuth_deg;     // Azimuth angle in degrees (-90..90)
};

// Decoded additional area (for local government messages)
struct DecodedAdditionalArea {
    bool present;                           // true if EX2-EX7 are not all zero
    bool head_to_area;                      // false=leave, true=head (EX2)
    DecodedEllipse ellipse;                 // Additional ellipse (EX3-EX7)
};

// Alert identity key for Update/All Clear matching (IS-QZSS-DCX-003 §4.2.3.1)
// L-Alert / Local Government: A2 + A3 + A4 + EX1
// J-Alert: A2 + A3 + A4
struct Mt44AlertIdentity {
    uint16_t a2;    // Country/Region Name (9 bits)
    uint8_t  a3;    // Provider Identifier (5 bits)
    uint8_t  a4;    // Hazard Category and Type (7 bits)
    uint16_t ex1;   // Target Area Code (16 bits) - only for L-Alert/Local

    bool operator==(const Mt44AlertIdentity& o) const {
        return a2 == o.a2 && a3 == o.a3 && a4 == o.a4 && ex1 == o.ex1;
    }
};

// Fully decoded MT44 message
struct Mt44Decoded {
    Mt44ServiceKind service_kind;
    bool is_null_message;

    // Decoded text labels
    const char* country_name;
    const char* provider_name;
    const char* hazard_name;
    const char* severity_name;
    const char* guidance_text;

    // Main ellipse (A12-A16) - decoded to WGS84
    // present if A12..A16 are not all zero
    bool main_ellipse_present;
    DecodedEllipse main_ellipse;

    // Target area code (EX1) - for L-Alert/Local Government
    // present if A12..A16 are all zero and EX1 is not zero
    bool target_area_code_present;
    uint16_t target_area_code;

    // J-Alert target area (EX8/EX9)
    bool jalert_prefecture_mode;  // true if EX8=0 (prefecture), false if EX8=1 (city)
    // Prefecture bit positions (1-47) - valid if jalert_prefecture_mode is true
    uint8_t prefecture_positions[47];
    uint8_t prefecture_count;
    // City/town/village codes - valid if jalert_prefecture_mode is false
    uint16_t city_codes[4];
    uint8_t city_code_count;

    // Additional area (local government only)
    DecodedAdditionalArea additional_area;

    // Alert identity key
    Mt44AlertIdentity alert_identity;
};

// ---- MT=43 JMA disaster_category mapping (IS-QZSS-DCR-016 Table 5.1.2-1)
//  0=undefined  1=EEW  2=Hypocenter  3=Seismic intensity  4=Nankai trough
//  5=Tsunami  6=NW Pacific Tsunami  8=Volcano  9=Ash fall
//  10=Weather  11=Flood  12=Typhoon  14=Marine

// ---- repeating record structs (up to 8 each) ---------------------------

struct TsunamiEntry {
    uint16_t   arrival_time_raw; // nextday(1)+hour(5)+minute(6)=12bit packed; 0=unspecified
    TimeFields arrival_time;     // resolved
    uint8_t    height_code;      // qzss_dcr_jma_tsunami_height
    uint16_t   region_code;      // qzss_dcr_jma_tsunami_forecast_region
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

struct FloodEntry {
    uint8_t  warning_level; // qzss_dcr_jma_flood_warning_level
    uint64_t region_code;   // qzss_dcr_jma_flood_forecast_region (40 bits)
};

struct MarineEntry {
    uint8_t  warning_code;  // qzss_dcr_jma_marine_warning_code
    uint16_t region_code;   // qzss_dcr_jma_marine_forecast_region
};

struct NwPacTsunamiEntry {
    uint16_t   arrival_time_raw; // nextday(1)+hour(5)+minute(6)=12bit packed; 0=unspecified
    TimeFields arrival_time;     // resolved
    uint16_t   height_code;    // qzss_dcr_jma_northwest_pacific_tsunami_height_en (9 bits)
    uint8_t    region_code;    // qzss_dcr_jma_coastal_region_en (7 bits)
};

// ---- MT=43 Data (QZQSM / DC Report) ------------------------------------

struct Mt43Data {
    // ---- MT=43 outer frame (IS-QZSS-DCR-016 §5.1) -----------------------
    uint8_t  report_classification;  // bits [14..16]  3 bits
    uint8_t  disaster_category;      // bits [17..20]  4 bits
    uint8_t  information_type;       // bits [41..42]  2 bits
    TimeFields event_time;           // bits [25..40]: day(5)+hour(5)+min(6)

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
    uint8_t  eew_regions[80];        // [130..209] 80 bits (1 bit per region)
    uint8_t  eew_region_count;

    // ---- Hypocenter  (disaster_category == 2) ---------------------------
    uint16_t         hypo_notification[3];
    uint8_t          hypo_notification_count;
    TimeFields       hypo_quake_time;         // [80..95]
    uint16_t         hypo_depth;              // [96..104] 9 bits
    uint8_t          hypo_magnitude;          // [105..111] 7 bits
    uint16_t         hypo_epicenter;          // [112..121] 10 bits
    LatLon           hypo_coords;             // [122..]

    // ---- Seismic Intensity  (disaster_category == 3) --------------------
    TimeFields       seis_quake_time;         // [53..68]
    SeismicEntry     seis_entries[16];
    uint8_t          seis_count;

    // ---- Nankai Trough  (disaster_category == 4) ------------------------
    uint8_t          nankai_info_code;        // [53..56] 4 bits
    uint8_t          nankai_text[18];         // [57..200] 18 bytes
    uint8_t          nankai_page;             // [201..206] 6 bits
    uint8_t          nankai_total_page;       // [207..212] 6 bits

    // ---- Tsunami  (disaster_category == 5) ------------------------------
    uint8_t          tsunami_warning_code;    // [80..83]  4 bits
    TsunamiEntry     tsunamis[5];
    uint8_t          tsunami_count;

    // ---- NW Pacific Tsunami  (disaster_category == 6) -------------------
    uint8_t          nw_pac_potential;        // [53..55]  3 bits
    NwPacTsunamiEntry nw_pac_tsunamis[5];
    uint8_t          nw_pac_count;

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

    // ---- Typhoon  (disaster_category == 12) -----------------------------
    // IS-QZSS-DCR-016 Table 4.1.2-47
    TimeFields       typh_reference_time;     // [53..68]  day(5)+hour(5)+min(6)
    uint8_t          typh_ref_type;           // [69..71]  3 bits (1:Analysis 2:Estimate 3:Forecast)
    uint8_t          typh_elapsed;            // [80..86]  7 bits (hours)
    uint8_t          typh_number;             // [87..93]  7 bits
    uint8_t          typh_scale;              // [94..97]  4 bits
    uint8_t          typh_intensity;          // [98..101] 4 bits
    LatLon           typh_coords;             // [102..142] 41 bits (lat_ns+lat_deg+lat_min+lat_sec+lon_ew+lon_deg+lon_min+lon_sec)
    uint16_t         typh_pressure;           // [143..153] 11 bits (hPa)
    uint8_t          typh_max_wind;           // [154..160] 7 bits (m/s)
    uint8_t          typh_max_gust;           // [161..167] 7 bits (m/s)

    // ---- Marine  (disaster_category == 14) ------------------------------
    MarineEntry      marine_entries[8];
    uint8_t          marine_count;
};

// ---- MT=44 Data (DCX / CAMF) -------------------------------------------

struct Mt44Data {
    Mt44ServiceKind service_kind;
    bool            is_null_message;

    Mt44Sd          sd;
    Mt44CamfRaw     camf;
    TimeFields      onset_time;

    ExtendedKind        ex_kind;
    Mt44ExLAlertOrLocal ex_lalert_local;
    Mt44ExJAlert        ex_jalert;
    Mt44ExOutside       ex_outside;

    Mt44Decoded      mt44_decoded;
};

// ---- Message payload type tag ------------------------------------------

enum class MsgPayloadType : uint8_t {
    Empty,
    Mt43,
    Mt44
};

// ---- main message struct (Tagged Union) --------------------------------

struct Message {
    // ---- common --------------------------------------------------------
    uint8_t  svid;
    uint8_t  msg_type;    // 43=QZQSM/MT43  44=DCX/MT44
    uint32_t crc24;
    bool     valid;

    // ---- payload (tagged union) ---------------------------------------
    // IMPORTANT: Always set payload_type before accessing union members
    MsgPayloadType payload_type;
    union {
        Mt43Data mt43;
        Mt44Data mt44;
    };
};
} // namespace azaraC
