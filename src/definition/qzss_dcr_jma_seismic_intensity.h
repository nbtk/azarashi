#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_seismic_intensity
// Variable      : qzss_dcr_jma_seismic_intensity
// Entries       : 7
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_seismic_intensity_lookup(uint8_t id) {
    switch (id) {
        case 1: return "4未満";
        case 2: return "4";
        case 3: return "5弱";
        case 4: return "5強";
        case 5: return "6弱";
        case 6: return "6強";
        case 7: return "7";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
