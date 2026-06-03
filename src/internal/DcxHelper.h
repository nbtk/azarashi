#pragma once
// azaraC - src/internal/DcxHelper.h
// DCX MT44 decode helpers
// Based on IS-QZSS-DCX-003

#include <cstdint>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// Decode helpers
// ---------------------------------------------------------------------------

// Decode latitude from 16-bit code (A12)
// Latitude = -90 + (180 / (2^16 - 1)) * code
double decodeLatitude16(uint16_t code);

// Decode longitude from 17-bit code (A13)
// Longitude = -180 + (360 / (2^17 - 1)) * code
double decodeLongitude17(uint32_t code);

// Decode additional ellipse latitude from 17-bit code (EX3)
// Same formula as A12 but with 17 bits
double decodeLatitude17(uint32_t code);

// Decode additional ellipse longitude from 17-bit code (EX4)
// Longitude = 45 + (180 / (2^17 - 1)) * code
double decodeLongitude17_45_225(uint32_t code);

// Decode radius from 5-bit code (A14/A15/EX5/EX6)
// Uses logarithmic table from IS-QZSS-DCX-003 Table 4.2-17
double decodeRadiusCode(uint8_t code);

// Decode azimuth from 6-bit code (A16)
// Azimuth = -90 + (180 / 2^6) * code
double decodeAzimuth6(uint8_t code);

// Decode azimuth from 7-bit code (EX7)
// Azimuth = -90 + (180 / 2^7) * code
double decodeAzimuth7(uint8_t code);

// ---------------------------------------------------------------------------
// J-Alert EX9 decoding
// ---------------------------------------------------------------------------

// Decode EX9 as prefecture bitmask (EX8=0)
// EX9 64-bit field: [47-bit prefecture][17-bit reserved]
// The 47-bit prefecture field is in ex9[63:17] (shift right by 17 to extract).
// Bit 0 (LSB) of the 47-bit integer = Hokkaido (JIS code 1)
// Bit 46 (MSB) of the 47-bit integer = Okinawa (JIS code 47)
// Fills out_positions array (must be at least 47 bytes) and returns the number of written positions.
uint8_t decodePrefectureBitmask(uint64_t ex9, uint8_t* out_positions);

// Decode EX9 as city/town/village code list (EX8=1)
// Fills out_codes array (must be at least 4 elements) and returns the number of written codes.
uint8_t decodeCityCodeList(uint64_t ex9, uint16_t* out_codes);

// ---------------------------------------------------------------------------
// B1 (A17=00) - Improved Resolution of Main Ellipse (EWSS CAMF v1.1 §3.7.1)
// ---------------------------------------------------------------------------

// Decode B1 refinement from A18 (15-bit field)
// A18 = C1(3bit)[0:2] + C2(3bit)[3:5] + C3(3bit)[6:8] + C4(3bit)[9:11] + Reserved(3bit)[12:14]
struct B1Refinement {
    uint8_t c1; // 3 bits - latitude refinement (0-7)
    uint8_t c2; // 3 bits - longitude refinement (0-7)
    uint8_t c3; // 3 bits - semi-major axis interpolation factor (0-7)
    uint8_t c4; // 3 bits - semi-minor axis interpolation factor (0-7)
};

B1Refinement decodeB1Refinement(uint16_t a18);

// Calculate latitude refinement offset (degrees)
// delta = C1 × 180 / (8 × 65535)
double b1RefinedLatitudeOffset(uint8_t c1);

// Calculate longitude refinement offset (degrees)
// delta = C2 × 360 / (8 × 131071)
double b1RefinedLongitudeOffset(uint8_t c2);

// Calculate interpolation factor for C3/C4
// factor = code / 8.0 → 0, 0.125, 0.250, ..., 0.875
double b1InterpolationFactor(uint8_t code);

// ---------------------------------------------------------------------------
// B2 (A17=01) - Position of the Centre of the Hazard (EWSS CAMF v1.1 §3.7.2)
// ---------------------------------------------------------------------------

struct B2HazardCenter {
    bool    present;
    uint8_t c5;              // 7 bits - delta latitude raw
    uint8_t c6;              // 7 bits - delta longitude raw
    double  delta_lat_deg;   // Delta latitude in degrees (-10..+10)
    double  delta_lon_deg;   // Delta longitude in degrees (-10..+10)
};

B2HazardCenter decodeB2HazardCenter(uint8_t c5, uint8_t c6);

// ---------------------------------------------------------------------------
// B3 (A17=10) - Secondary Ellipse Definition (EWSS CAMF v1.1 §3.7.3)
// ---------------------------------------------------------------------------

struct B3SecondaryEllipse {
    bool     present;
    uint8_t  c7;                // 2 bits - shift factor (0-3)
    uint8_t  c8;                // 3 bits - homothetic factor index
    uint8_t  c9;                // 5 bits - bearing angle index
    uint8_t  c10;               // 5 bits - guidance library code
    double   shift_km;          // Shift distance in km
    double   homothetic_factor; // Homothetic factor (0.25-2.0)
    double   bearing_deg;       // Bearing angle in degrees
};

B3SecondaryEllipse decodeB3SecondaryEllipse(uint8_t c7, uint8_t c8, uint8_t c9, uint8_t c10, double semi_major_km);

// ---------------------------------------------------------------------------
// B4 (A17=11) - Quantitative and Detailed Information (EWSS CAMF v1.1 §3.7.4)
// ---------------------------------------------------------------------------

struct B4DetailedInfo {
    bool     present;
    uint8_t  a4_code;           // Hazard category/type (raw)
    // Raw D-series values (only valid fields depend on A4)
    uint8_t  d1;   // 4 bits - Magnitude on Richter scale
    uint8_t  d2;   // 3 bits - Seismic coefficient
    uint8_t  d3;   // 4 bits - Azimuth from ellipse center to epicenter
    uint8_t  d4;   // 4 bits - Vector length between ellipse center and epicenter
    uint8_t  d5;   // 3 bits - Wave height
    uint8_t  d6;   // 4 bits - Temperature range
    uint8_t  d7;   // 3 bits - Hurricane category
    uint8_t  d8;   // 4 bits - Wind speed
    uint8_t  d9;   // 3 bits - Rainfall amounts
    uint8_t  d10;  // 3 bits - Damage category
    uint8_t  d11;  // 3 bits - Tornado probability
    uint8_t  d12;  // 4 bits - Hail scale
    uint8_t  d13;  // 4 bits - Visibility
    uint8_t  d14;  // 5 bits - Snow depth
    uint8_t  d15;  // 2 bits - Flood severity
    uint8_t  d16;  // 3 bits - Lightning intensity
    uint8_t  d17;  // 3 bits - Fog level
    uint8_t  d18;  // 2 bits - Drought level
    uint8_t  d19;  // 3 bits - Avalanche warning level
    uint8_t  d20;  // 3 bits - Ash fall amount and impact
    uint8_t  d21;  // 3 bits - Geomagnetic scale
    uint8_t  d22;  // 3 bits - Terrorism threat level
    uint8_t  d23;  // 3 bits - Fire risk level
    uint8_t  d24;  // 3 bits - Water quality
    uint8_t  d25;  // 4 bits - UV index
    uint8_t  d26;  // 5 bits - Number of cases per 100000 inhabitants
    uint8_t  d27;  // 4 bits - Noise range
    uint8_t  d28;  // 3 bits - Air quality index
    uint8_t  d29;  // 5 bits - Outage estimated duration
    uint8_t  d30;  // 4 bits - Nuclear event scale
    uint8_t  d31;  // 4 bits - Chemical hazard type
    uint8_t  d32;  // 2 bits - Biohazard level
    uint8_t  d33;  // 2 bits - Biohazard type
    uint8_t  d34;  // 2 bits - Explosive hazard type
    uint8_t  d35;  // 6 bits - Infection type
    uint8_t  d36;  // 3 bits - Typhoon category
};

B4DetailedInfo decodeB4DetailedInfo(uint16_t a18, uint8_t a4_code);

} // namespace internal
} // namespace azaraC
