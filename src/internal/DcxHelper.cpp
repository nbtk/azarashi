// azaraC - src/internal/DcxHelper.cpp
// DCX MT44 decode helpers
// Based on IS-QZSS-DCX-003 / EWSS CAMF v1.1

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
// A18 bit layout: bit[14]=MSB (first bit of field = spec bit 131), bit[0]=LSB (last bit = spec bit 145)
// getBits() reads MSB-first, so a18 bit 14 = spec bit 131
// C1: spec bits 131-133 → a18[14:12] → shift=12, mask=0x07
// C2: spec bits 134-136 → a18[11:9]  → shift=9,  mask=0x07
// C3: spec bits 137-139 → a18[8:6]   → shift=6,  mask=0x07
// C4: spec bits 140-142 → a18[5:3]   → shift=3,  mask=0x07
// Reserved: spec bits 143-145 → a18[2:0]

B1Refinement decodeB1Refinement(uint16_t a18) {
    B1Refinement b1;
    b1.c1 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
    b1.c2 = (a18 >> 9)  & 0x07;  // spec[134:136] → a18[11:9]
    b1.c3 = (a18 >> 6)  & 0x07;  // spec[137:139] → a18[8:6]
    b1.c4 = (a18 >> 3)  & 0x07;  // spec[140:142] → a18[5:3]
    // a18[2:0] reserved (spec bits 143-145)
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

// ---------------------------------------------------------------------------
// B2 (A17=01) - Position of the Centre of the Hazard (EWSS CAMF v1.1 §3.7.2)
// ---------------------------------------------------------------------------

B2HazardCenter decodeB2HazardCenter(uint8_t c5, uint8_t c6) {
    B2HazardCenter r{};
    r.present = true;
    r.c5 = c5;
    r.c6 = c6;
    // delta = -10 + (20/128) * code  (if code <= 63)
    // delta = -10 + (20/128) * (code+1)  (if code >= 64)
    // Step = 20/128 = 0.15625 degrees
    double step = 20.0 / 128.0;
    if (c5 <= 63) r.delta_lat_deg = -10.0 + step * c5;
    else          r.delta_lat_deg = -10.0 + step * (c5 + 1);
    if (c6 <= 63) r.delta_lon_deg = -10.0 + step * c6;
    else          r.delta_lon_deg = -10.0 + step * (c6 + 1);
    return r;
}

// ---------------------------------------------------------------------------
// B3 (A17=10) - Secondary Ellipse Definition (EWSS CAMF v1.1 §3.7.3)
// ---------------------------------------------------------------------------

B3SecondaryEllipse decodeB3SecondaryEllipse(uint8_t c7, uint8_t c8, uint8_t c9, uint8_t c10, double semi_major_km) {
    B3SecondaryEllipse r{};
    r.present = true;
    r.c7 = c7;
    r.c8 = c8;
    r.c9 = c9;
    r.c10 = c10;
    // Shift: C7 * semi-major axis length
    r.shift_km = static_cast<double>(c7) * semi_major_km;
    // Homothetic factor: 0.25 * (C8 + 1) → 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00
    r.homothetic_factor = 0.25 * static_cast<double>(c8 + 1);
    // Bearing angle: C9 * 11.25 degrees (0-348.75, step 11.25)
    r.bearing_deg = static_cast<double>(c9) * 11.25;
    return r;
}

// ---------------------------------------------------------------------------
// B4 (A17=11) - Quantitative and Detailed Information (EWSS CAMF v1.1 §3.7.4)
// ---------------------------------------------------------------------------
// A18 bit layout: bit[14]=MSB (first bit of field = spec bit 131), bit[0]=LSB (last bit = spec bit 145)
// getBits() reads MSB-first, so a18 bit 14 = spec bit 131
// To extract spec bits[N:M]: shift = 14 - M, mask = (1 << (M-N+1)) - 1
// D1[131:134]: shift=14-134=11, mask=0x0F
// D2[135:137]: shift=14-137=8,  mask=0x07
// D3[138:141]: shift=14-141=4,  mask=0x0F
// D4[142:145]: shift=14-145=0,  mask=0x0F

B4DetailedInfo decodeB4DetailedInfo(uint16_t a18, uint8_t a4_code) {
    B4DetailedInfo r{};
    r.present = true;
    r.a4_code = a4_code;

    switch (a4_code) {
        case 36: // Earthquake: D1[131:134](4b) D2[135:137](3b) D3[138:141](4b) D4[142:145](4b)
            r.d1  = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            r.d2  = (a18 >> 8)  & 0x07;  // spec[135:137] → a18[10:8]
            r.d3  = (a18 >> 4)  & 0x0F;  // spec[138:141] → a18[7:4]
            r.d4  = (a18 >> 0)  & 0x0F;  // spec[142:145] → a18[3:0]
            break;
        case 43: // Tsunami: D5[131:133](3b)
        case 44: // Tidal wave
            r.d5 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 63: // Cold wave: D6[131:134](4b)
        case 71: // Heat wave
            r.d6 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 80: // Hurricane: D7[131:133](3b) D8[134:137](4b) D9[138:140](3b)
            r.d7 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            r.d8 = (a18 >> 8)  & 0x0F;  // spec[134:137] → a18[10:7]  (14-137=7, but 4 bits → 10:7)
            r.d9 = (a18 >> 5)  & 0x07;  // spec[138:140] → a18[7:5]   (14-140=5, 3 bits → 7:5)
            break;
        case 82: // Typhoon: D36[131:133](3b) D8[134:137](4b) D9[138:140](3b)
            r.d36 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            r.d8  = (a18 >> 8)  & 0x0F;  // spec[134:137] → a18[10:7]
            r.d9  = (a18 >> 5)  & 0x07;  // spec[138:140] → a18[7:5]
            break;
        case 79: // Tornado: D8[131:134](4b) D9[135:137](3b) D11[138:140](3b)
            r.d8  = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            r.d9  = (a18 >> 8)  & 0x07;  // spec[135:137] → a18[10:8]
            r.d11 = (a18 >> 5)  & 0x07;  // spec[138:140] → a18[7:5]
            break;
        case 77: // Storm/Thunderstorm: D8[131:134](4b) D9[135:137](3b) D10[138:140](3b) D16[141:143](3b)
            r.d8  = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            r.d9  = (a18 >> 8)  & 0x07;  // spec[135:137] → a18[10:8]
            r.d10 = (a18 >> 5)  & 0x07;  // spec[138:140] → a18[7:5]
            r.d16 = (a18 >> 2)  & 0x07;  // spec[141:143] → a18[4:2]  (14-143=2, 3 bits → 4:2)
            break;
        case 70: // Hail: D12[131:134](4b)
            r.d12 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 74: // Rainfall: D9[131:133](3b) D13[134:137](4b)
            r.d9  = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            r.d13 = (a18 >> 8)  & 0x0F;  // spec[134:137] → a18[10:7]  (4 bits)
            break;
        case 76: // Snowfall: D14[131:135](5b) D13[136:139](4b)
            r.d14 = (a18 >> 10) & 0x1F;  // spec[131:135] → a18[14:10] (5 bits)
            r.d13 = (a18 >> 5)  & 0x0F;  // spec[136:139] → a18[8:5]
            break;
        case 68: // Flood: D15[131:132](2b)
            r.d15 = (a18 >> 13) & 0x03;  // spec[131:132] → a18[14:13]
            break;
        case 72: // Lightning: D16[131:133](3b)
            r.d16 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 81: // Wind chill/Frost: D8[131:134](4b) D6[135:138](4b)
            r.d8 = (a18 >> 11) & 0x0F;   // spec[131:134] → a18[14:11]
            r.d6 = (a18 >> 6)  & 0x0F;   // spec[135:138] → a18[9:6]
            break;
        case 64: // Derecho: D8[131:134](4b) D9[135:137](3b) D16[138:140](3b) D11[141:143](3b)
            r.d8  = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            r.d9  = (a18 >> 8)  & 0x07;  // spec[135:137] → a18[10:8]
            r.d16 = (a18 >> 5)  & 0x07;  // spec[138:140] → a18[7:5]
            r.d11 = (a18 >> 2)  & 0x07;  // spec[141:143] → a18[4:2]
            break;
        case 69: // Fog: D17[131:133](3b) D13[134:137](4b)
            r.d17 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            r.d13 = (a18 >> 8)  & 0x0F;  // spec[134:137] → a18[10:7]  (4 bits)
            break;
        case 75: // Snow storm/Blizzard: D13[131:134](4b) D8[135:138](4b)
            r.d13 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            r.d8  = (a18 >> 6)  & 0x0F;  // spec[135:138] → a18[9:6]
            break;
        case 65: // Drought: D18[131:132](2b)
            r.d18 = (a18 >> 13) & 0x03;  // spec[131:132] → a18[14:13]
            break;
        case 33: // Avalanche: D19[131:133](3b)
            r.d19 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 32: // Ash fall: D20[131:133](3b)
            r.d20 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 47: // Wind/wave/storm surge: D8[131:134](4b) D5[135:137](3b)
            r.d8 = (a18 >> 11) & 0x0F;   // spec[131:134] → a18[14:11]
            r.d5 = (a18 >> 8)  & 0x07;   // spec[135:137] → a18[10:8]
            break;
        case 37: // Geomagnetic: D21[131:133](3b)
            r.d21 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 103: // Terrorism: D22[131:133](3b)
            r.d22 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 27: // Forest fire: D23[131:133](3b)
        case 30: // Risk of fire
            r.d23 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 16: // Contaminated drinking water: D24[131:133](3b)
        case 18: // Marine pollution
        case 21: // River pollution
            r.d24 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 23: // UV radiation: D25[131:134](4b)
            r.d25 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 53: // Risk of infection: D26[131:135](5b) D35[136:141](6b)
        case 51: // Pandemic
            r.d26 = (a18 >> 10) & 0x1F;  // spec[131:135] → a18[14:10] (5 bits)
            r.d35 = (a18 >> 3)  & 0x3F;  // spec[136:141] → a18[8:3]
            break;
        case 19: // Noise pollution: D27[131:134](4b)
            r.d27 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 15: // Air pollution: D28[131:133](3b)
            r.d28 = (a18 >> 12) & 0x07;  // spec[131:133] → a18[14:12]
            break;
        case 56: // Gas supply outage: D29[131:135](5b)
        case 57: // Outage of IT system
        case 58: // Power outage
        case 55: // Emergency number outage
        case 60: // Telephone line outage
            r.d29 = (a18 >> 10) & 0x1F;  // spec[131:135] → a18[14:10] (5 bits)
            break;
        case 9: // Radiological hazard: D30[131:134](4b)
        case 10: // Nuclear hazard
        case 11: // Nuclear power station accident
            r.d30 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 5: // Chemical hazard: D31[131:134](4b)
            r.d31 = (a18 >> 11) & 0x0F;  // spec[131:134] → a18[14:11]
            break;
        case 4: // Biological hazard: D32[131:132](2b) D33[133:134](2b)
            r.d32 = (a18 >> 13) & 0x03;  // spec[131:132] → a18[14:13]
            r.d33 = (a18 >> 11) & 0x03;  // spec[133:134] → a18[12:11]  (14-134=11, 2 bits → 12:11)
            break;
        case 6: // Explosive hazard: D34[131:132](2b)
            r.d34 = (a18 >> 13) & 0x03;  // spec[131:132] → a18[14:13]
            break;
        default:
            break;
    }

    return r;
}

} // namespace internal
} // namespace azaraC