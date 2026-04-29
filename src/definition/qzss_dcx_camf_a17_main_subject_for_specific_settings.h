#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a17_main_subject_for_specific_settings
// Variable      : qzss_dcx_camf_a17_main_subject_for_specific_settings
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_a17_main_subject_for_specific_settings_lookup(uint8_t id) {
    switch (id) {
        case 0: return "B1 - Improved Resolution of Main Ellipse";
        case 1: return "B2 - Position of the Centre of the Hazard";
        case 2: return "B3 - Secondary Ellipse Definition";
        case 3: return "B4 - Quantitative and detailed information about the Hazard";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
