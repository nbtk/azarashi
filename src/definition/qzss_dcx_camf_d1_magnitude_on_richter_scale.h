#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d1_magnitude_on_richter_scale
// Entries       : 9
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_d1_magnitude_on_richter_scale_lookup(uint8_t id) {
    switch (id) {
        case 0: return "1.0-1.9 - Micro";
        case 1: return "2.0-2.9 - Minor";
        case 2: return "3.0-3.9 - Minor";
        case 3: return "4.0-4.9 - Light";
        case 4: return "5.0-5.9 - Moderate";
        case 5: return "6.0-6.9 - Strong";
        case 6: return "7.0-7.9 - Major";
        case 7: return "8.0-8.9 - Great";
        case 8: return "9.0 and greater - Great";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
