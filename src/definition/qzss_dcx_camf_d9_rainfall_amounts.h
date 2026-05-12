#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d9_rainfall_amounts
// Entries       : 8
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d9_rainfall_amounts_lookup(uint8_t id) {
    switch (id) {
        case 0: return "p ≤ 2.5mm/h";
        case 1: return "2.5mm/h < p ≤ 7.5mm/h";
        case 2: return "7.5mm/h < p ≤ 10mm/h";
        case 3: return "10mm/h < p ≤ 20mm/h";
        case 4: return "20mm/h < p ≤ 30mm/h";
        case 5: return "30mm/h < p ≤ 50mm/h";
        case 6: return "50mm/h < p ≤ 80mm/h";
        case 7: return "80mm/h < p";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
