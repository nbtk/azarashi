#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a6_hazard_onset_week
// Variable      : qzss_dcx_camf_a6_hazard_onset_week
// Entries       : 2
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_a6_hazard_onset_week_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Current";
        case 1: return "Next";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
