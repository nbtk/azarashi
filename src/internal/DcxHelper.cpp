// azaraC - src/internal/DcxHelper.cpp
// DCX MT44 decode helpers
// Based on IS-QZSS-DCX-003

#include "DcxHelper.h"

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// Latitude/Longitude decoding
// ---------------------------------------------------------------------------

double decodeLatitude16(uint16_t code) {
    // Latitude = -90 + (180 / (2^16 - 1)) * code
    return -90.0 + (180.0 / 65535.0) * static_cast<double>(code);
}

double decodeLongitude17(uint32_t code) {
    // Longitude = -180 + (360 / (2^17 - 1)) * code
    return -180.0 + (360.0 / 131071.0) * static_cast<double>(code);
}

double decodeLatitude17(uint32_t code) {
    // Latitude = -90 + (180 / (2^17 - 1)) * code
    return -90.0 + (180.0 / 131071.0) * static_cast<double>(code);
}

double decodeLongitude17_45_225(uint32_t code) {
    // Longitude = 45 + (180 / (2^17 - 1)) * code
    return 45.0 + (180.0 / 131071.0) * static_cast<double>(code);
}

// ---------------------------------------------------------------------------
// Radius decoding (5-bit code)
// IS-QZSS-DCX-003 Table 4.2-17 / 4.2-18
// Radius[m] = 10^(log10(MinRadius) + a * (log10(MaxRadius) - log10(MinRadius)) / Max_a)
// MinRadius = 216.20, MaxRadius = 2500000, Max_a = 31
// ---------------------------------------------------------------------------

double decodeRadiusCode(uint8_t code) {
    // Pre-computed table from IS-QZSS-DCX-003 Table 4.2-17
    // Index 0..31, values in km
    static const double radius_table[32] = {
        0.216,   // 0
        0.292,   // 1
        0.395,   // 2
        0.535,   // 3
        0.723,   // 4
        0.978,   // 5
        1.322,   // 6
        1.788,   // 7
        2.418,   // 8
        3.269,   // 9
        4.421,   // 10
        5.979,   // 11
        8.085,   // 12
        10.933,  // 13
        14.784,  // 14
        19.992,  // 15
        27.035,  // 16
        36.559,  // 17
        49.439,  // 18
        66.855,  // 19
        90.407,  // 20
        122.255, // 21
        165.324, // 22
        223.564, // 23
        302.322, // 24
        408.824, // 25
        552.846, // 26
        747.603, // 27
        1010.970,// 28
        1367.116,// 29
        1848.727,// 30
        2500.000 // 31
    };

    if (code < 32) {
        return radius_table[code];
    }
    return 0.0; // Invalid code
}

// ---------------------------------------------------------------------------
// Azimuth decoding
// ---------------------------------------------------------------------------

double decodeAzimuth6(uint8_t code) {
    // Azimuth = -90 + (180 / 2^6) * code
    return -90.0 + (180.0 / 64.0) * static_cast<double>(code);
}

double decodeAzimuth7(uint8_t code) {
    // Azimuth = -90 + (180 / 2^7) * code
    return -90.0 + (180.0 / 128.0) * static_cast<double>(code);
}

// ---------------------------------------------------------------------------
// J-Alert EX9 decoding
// ---------------------------------------------------------------------------

uint8_t decodePrefectureBitmask(uint64_t ex9, uint8_t* out_positions) {
    uint8_t count = 0;

    // EX9 bit layout for prefecture (EX8=0):
    // EX9 64-bit field: [47-bit prefecture][17-bit reserved]
    // Stream bit 147 → ex9 bit 63 (MSB of 47-bit field)
    // Stream bit 193 → ex9 bit 17 (LSB of 47-bit field)
    // Stream bits 194..210 → ex9 bits 16..0 (reserved)
    //
    // 47-bit prefecture integer: bit 0 (LSB) = Hokkaido (JIS 1), bit 46 (MSB) = Okinawa (JIS 47)
    // In EX9, this maps to ex9[63:17], so we shift right by 17 to align.

    uint64_t pref = ex9 >> 17;  // Extract 47-bit prefecture field

    for (uint8_t i = 0; i < 47; ++i) {
        if (pref & (1ULL << i)) {
            // i=0 (LSB) = Hokkaido = JIS code 1
            // i=46 (MSB) = Okinawa = JIS code 47
            out_positions[count++] = i + 1;
        }
    }

    return count;
}

uint8_t decodeCityCodeList(uint64_t ex9, uint16_t* out_codes) {
    uint8_t count = 0;

    // EX9 bit layout for cities/towns/villages (EX8=1):
    // Four 16-bit city/town/village codes
    // Code 1: bits [0..15]
    // Code 2: bits [16..31]
    // Code 3: bits [32..47]
    // Code 4: bits [48..63]

    for (uint8_t i = 0; i < 4; ++i) {
        uint16_t code = static_cast<uint16_t>((ex9 >> (i * 16)) & 0xFFFF);
        if (code != 0) {
            out_codes[count++] = code;
        }
    }

    return count;
}

// ---------------------------------------------------------------------------
// B1 (A17=00) - Improved Resolution of Main Ellipse (EWSS CAMF v1.1 §3.7.1)
// ---------------------------------------------------------------------------

B1Refinement decodeB1Refinement(uint16_t a18) {
    B1Refinement b1;
    b1.c1 = a18 & 0x07;          // bits [0:2]   (3 bits)
    b1.c2 = (a18 >> 3) & 0x07;  // bits [3:5]   (3 bits)
    b1.c3 = (a18 >> 6) & 0x07;  // bits [6:8]   (3 bits)
    b1.c4 = (a18 >> 9) & 0x07;  // bits [9:11]  (3 bits)
    // bits [12:14] reserved
    return b1;
}

double b1RefinedLatitudeOffset(uint8_t c1) {
    // C1: 緯度補正 = C1 × 180 / (8 × 65535)
    // Grid interval = 180 / 65535 ≈ 0.002747°
    // Step = interval / 8 ≈ 0.000343°
    return static_cast<double>(c1) * (180.0 / (8.0 * 65535.0));
}

double b1RefinedLongitudeOffset(uint8_t c2) {
    // C2: 経度補正 = C2 × 360 / (8 × 131071)
    // Grid interval = 360 / 131071 ≈ 0.002747°
    // Step = interval / 8 ≈ 0.000343°
    return static_cast<double>(c2) * (360.0 / (8.0 * 131071.0));
}

double b1InterpolationFactor(uint8_t code) {
    // C3/C4: 補間係数 = code / 8.0
    // 0 → 0.000, 1 → 0.125, 2 → 0.250, ..., 7 → 0.875
    return static_cast<double>(code) / 8.0;
}


} // namespace internal
} // namespace azaraC
