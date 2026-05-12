#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_a8_hazard_duration
// Variable      : qzss_dcx_camf_a8_hazard_duration
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_a8_hazard_duration_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Unknown";
        case 1: return "Duration < 6H";
        case 2: return "6H <= Duration < 12H";
        case 3: return "12H <= Duration < 24H";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
