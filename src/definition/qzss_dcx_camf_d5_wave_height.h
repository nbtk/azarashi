#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d5_wave_height
// Entries       : 8
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d5_wave_height_lookup(uint8_t id) {
    switch (id) {
        case 0: return "H ≤ 0.5m";
        case 1: return "0.5m < H ≤ 1.0m";
        case 2: return "1.0m < H ≤ 1.5m";
        case 3: return "1.5m < H ≤ 2.0m";
        case 4: return "2.0m < H ≤ 3.0m";
        case 5: return "3.0m < H ≤ 5.0m";
        case 6: return "5.0m < H ≤ 10.0m";
        case 7: return "H > 10.0m";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
