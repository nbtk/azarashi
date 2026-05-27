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

} // namespace internal
} // namespace azaraC

