#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d29_outage_estimated_duration
// Entries       : 13
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_TABLE[] = {
    "0 < duration < 30 min",
    "30 min ≤ duration < 45 min",
    "45 min ≤ duration < 1 h",
    "1 h ≤ duration < 1h 30min",
    "1h 30min ≤ duration < 2 h",
    "2 h ≤ duration < 3 h",
    "3 h ≤ duration < 4 h",
    "4 h ≤ duration < 5 h",
    "5 h ≤ duration < 10 h",
    "10 h ≤ duration < 24 h",
    "24 h ≤ duration < 2 days",
    "2 days ≤ duration < 7 days",
    "7 days ≤ duration"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_SIZE = 13;
inline constexpr const char* qzss_dcx_camf_d29_outage_estimated_duration_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_BASE || id >= QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_BASE + QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_SIZE) return nullptr;
    return QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_TABLE[id - QZSS_DCX_CAMF_D29_OUTAGE_ESTIMATED_DURATION_BASE];
}

} // namespace def
} // namespace azaraC
