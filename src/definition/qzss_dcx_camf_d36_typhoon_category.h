#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d36_typhoon_category
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_d36_typhoon_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Scale 1 and Intensity 1";
        case 1: return "Scale 1 and Intensity 2";
        case 2: return "Scale 1 and Intensity 3";
        case 3: return "Scale 2 and Intensity 1";
        case 4: return "Scale 2 and Intensity 2";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
