#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_a5_severity
// Variable      : qzss_dcx_camf_a5_severity
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_a5_severity_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Unknown";
        case 1: return "Moderate - Possible threat to life or property";
        case 2: return "Severe - Significant threat to life or property";
        case 3: return "Extreme - Extraordinary threat to life or property";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
