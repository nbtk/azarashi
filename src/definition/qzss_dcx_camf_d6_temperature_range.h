#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d6_temperature_range
// Entries       : 16
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_TABLE[] = {
    "T ≤ -30°C",
    "-30°C < T ≤ -25°C",
    "-25°C < T ≤ -20°C",
    "-20°C < T ≤ -15°C",
    "-15°C < T ≤ -10°C",
    "-10°C < T ≤ -5°C",
    "-5°C < T ≤ 0°C",
    "0°C < T ≤ 5°C",
    "5°C < T ≤ 10°C",
    "10°C < T ≤ 15°C",
    "15°C < T ≤ 20°C",
    "20°C < T ≤ 25°C",
    "25°C < T ≤ 30°C",
    "30°C < T ≤ 35°C",
    "35°C < T ≤ 45°C",
    "T > 45°C"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_SIZE = 16;
inline constexpr const char* qzss_dcx_camf_d6_temperature_range_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_BASE || id >= QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_BASE + QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_SIZE) return nullptr;
    return QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_TABLE[id - QZSS_DCX_CAMF_D6_TEMPERATURE_RANGE_BASE];
}

} // namespace def
} // namespace azaraC
