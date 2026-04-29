#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d13_visibility
// Entries       : 10
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d13_visibility_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Dense fog: visibility < 20m";
        case 1: return "Thick fog: 20m < visibility < 200m";
        case 2: return "Moderate fog: 200m < visibility < 500m";
        case 3: return "Light fog: 500m < visibility < 1000m";
        case 4: return "Thin fog: 1km < visibility < 2km";
        case 5: return "Haze: 2km < visibility < 4km";
        case 6: return "Light haze: 4km < visibility < 10km";
        case 7: return "Clear: 10km < visibility < 20km";
        case 8: return "Very clear: 20km < visibility < 50km";
        case 9: return "Exceptionally clear: visibility > 50km";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
