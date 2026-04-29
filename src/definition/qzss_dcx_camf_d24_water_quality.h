#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d24_water_quality
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d24_water_quality_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Excellent water quality";
        case 1: return "Good water quality";
        case 2: return "Poor water quality";
        case 3: return "Very poor water quality";
        case 4: return "Suitable for drinking purposes";
        case 5: return "Unsuitable for drinking purpose";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
