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

    // B1 (A17=00) - Improved Resolution of Main Ellipse (EWSS CAMF v1.1 §3.7.1)
    // A18 (15bit) = C1(3bit) + C2(3bit) + C3(3bit) + C4(3bit) + Reserved(3bit)
    bool     b1_present;    // true if A17 == 0 and any C1-C4 is non-zero
    uint8_t  b1_c1;         // 3 bits [0:2]   - latitude refinement (0-7)
    uint8_t  b1_c2;         // 3 bits [3:5]   - longitude refinement (0-7)
    uint8_t  b1_c3;         // 3 bits [6:8]   - semi-major axis interpolation factor (0-7)
    uint8_t  b1_c4;         // 3 bits [9:11]  - semi-minor axis interpolation factor (0-7)
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

    // B1 refinement values (EWSS CAMF v1.1 §3.7.1)
    // Valid when Mt44CamfRaw::b1_present is true
    double b1_lat_offset_deg;    // C1 × 180/(8×65535) - latitude refinement offset
    double b1_lon_offset_deg;    // C2 × 360/(8×131071) - longitude refinement offset
    double b1_major_factor;      // C3 / 8.0 - semi-major interpolation factor (0..0.875)
    double b1_minor_factor;      // C4 / 8.0 - semi-minor interpolation factor (0..0.875)
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

// ---- disaster_category specific structs ----------------------------------

struct EewData {
    uint8_t  long_period_lower;  // [47..49]  3 bits
    uint8_t  long_period_upper;  // [50..52]  3 bits
    uint16_t notification[3];    // [53..79]  3×9 bits (notification codes, 0=end)
    uint8_t  notification_count;
    TimeFields quake_time;       // [80..95]
    uint16_t depth;              // [96..104]  9 bits (×10 km; 800=深い, 900=不明)
    uint8_t  magnitude;          // [105..111] 7 bits (×0.1; 100=8.0以上)
    uint16_t epicenter;          // [112..121] 10 bits
    uint8_t  intensity_lower;    // [122..125] 4 bits
    uint8_t  intensity_upper;    // [126..129] 4 bits
    uint8_t  regions[80];        // [130..209] 80 bits (1 bit per region)
    uint8_t  region_count;
};

struct HypocenterData {
    uint16_t   notification[3];
    uint8_t    notification_count;
    TimeFields quake_time;       // [80..95]
    uint16_t   depth;            // [96..104] 9 bits
    uint8_t    magnitude;        // [105..111] 7 bits
    uint16_t   epicenter;        // [112..121] 10 bits
    LatLon     coords;           // [122..]
};

struct SeismicData {
    TimeFields   quake_time;     // [53..68]
    SeismicEntry entries[16];
    uint8_t      count;
};

struct NankaiData {
    uint8_t info_code;           // [53..56] 4 bits
    uint8_t text[18];            // [57..200] 18 bytes
    uint8_t page;                // [201..206] 6 bits
    uint8_t total_page;          // [207..212] 6 bits
};

struct TsunamiData {
    uint8_t      warning_code;   // [80..83]  4 bits
    TsunamiEntry entries[5];
    uint8_t      count;
};

struct NwPacTsunamiData {
    uint8_t            potential; // [53..55]  3 bits
    NwPacTsunamiEntry entries[5];
    uint8_t            count;
};

struct VolcanoData {
    uint8_t    ambiguity;        // [50..52]  3 bits
    TimeFields activity_time;    // [53..68]
    uint8_t    warning_code;     // [69..75]  7 bits
    uint16_t   volcano_name;     // [76..87] 12 bits
    uint32_t   local_govs[5];    // [88..] up to 5×23 bits
    uint8_t    lg_count;
};

struct AshFallData {
    TimeFields activity_time;    // [53..68]
    uint8_t    warning_type;     // [69..70]  2 bits (1=速報 2=詳細)
    uint16_t   volcano_name;     // [71..82] 12 bits
    uint8_t    entries_time[4];  // [83..] ×4: arrival_hour(3)
    uint8_t    entries_code[4];  // warning_code(3)
    uint32_t   entries_lg[4];    // local_government(23)
    uint8_t    count;
};

struct WeatherData {
    uint8_t      warning_state;  // [53..55]  3 bits
    WeatherEntry entries[6];
    uint8_t      count;
};

struct FloodData {
    FloodEntry entries[3];
    uint8_t    count;
};

struct TyphoonData {
    TimeFields reference_time;   // [53..68]  day(5)+hour(5)+min(6)
    uint8_t    ref_type;         // [69..71]  3 bits (1:Analysis 2:Estimate 3:Forecast)
    uint8_t    elapsed;          // [80..86]  7 bits (hours)
    uint8_t    number;           // [87..93]  7 bits
    uint8_t    scale;            // [94..97]  4 bits
    uint8_t    intensity;        // [98..101] 4 bits
    LatLon     coords;           // [102..142] 41 bits
    uint16_t   pressure;         // [143..153] 11 bits (hPa)
    uint8_t    max_wind;         // [154..160] 7 bits (m/s)
    uint8_t    max_gust;         // [161..167] 7 bits (m/s)
};

struct MarineData {
    MarineEntry entries[8];
    uint8_t     count;
};

struct Mt43Data {
    // ---- MT=43 outer frame (IS-QZSS-DCR-016 §5.1) -----------------------
    uint8_t  report_classification;  // bits [14..16]  3 bits
    uint8_t  disaster_category;      // bits [17..20]  4 bits
    uint8_t  information_type;       // bits [41..42]  2 bits
    TimeFields event_time;           // bits [25..40]: day(5)+hour(5)+min(6)

    // ---- disaster_category specific data (tagged union) ------------------
    // Access the member matching disaster_category
    union {
        EewData          eew;        // disaster_category == 1
        HypocenterData   hypo;       // disaster_category == 2
        SeismicData      seis;       // disaster_category == 3
        NankaiData       nankai;     // disaster_category == 4
        TsunamiData      tsunami;    // disaster_category == 5
        NwPacTsunamiData nw_pac;     // disaster_category == 6
        VolcanoData      vol;        // disaster_category == 8
        AshFallData      ash;        // disaster_category == 9
        WeatherData      wx;         // disaster_category == 10
        FloodData        flood;      // disaster_category == 11
        TyphoonData      typh;       // disaster_category == 12
        MarineData       marine;     // disaster_category == 14
    };
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
    uint8_t  svid = 0;
    uint8_t  msg_type = 0;    // 43=QZQSM/MT43  44=DCX/MT44
    uint32_t crc24 = 0;
    bool     valid = false;

    // ---- payload (tagged union) ---------------------------------------
    // IMPORTANT: Always set payload_type before accessing union members
    MsgPayloadType payload_type = MsgPayloadType::Empty;
    union {
        Mt43Data mt43;
        Mt44Data mt44;
    };

    // ---- default constructor ------------------------------------------
    // Initializes payload_type to Empty and constructs a safe active union member
    Message() : payload_type(MsgPayloadType::Empty) {
        // Union is left uninitialized (POD types). Access only after setting payload_type.
    }

    // ---- safe accessors -----------------------------------------------
    // Returns pointer to mt43 if payload_type == Mt43, nullptr otherwise
    Mt43Data* getMt43() {
        return (payload_type == MsgPayloadType::Mt43) ? &mt43 : nullptr;
    }

    // Returns pointer to mt44 if payload_type == Mt44, nullptr otherwise
    Mt44Data* getMt44() {
        return (payload_type == MsgPayloadType::Mt44) ? &mt44 : nullptr;
    }

    // Const overloads
    const Mt43Data* getMt43() const {
        return (payload_type == MsgPayloadType::Mt43) ? &mt43 : nullptr;
    }

    const Mt44Data* getMt44() const {
        return (payload_type == MsgPayloadType::Mt44) ? &mt44 : nullptr;
    }
};
} // namespace azaraC
