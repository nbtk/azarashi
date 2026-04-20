#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_weather_warning_state
// Variable      : qzss_dcr_jma_weather_warning_state
// Entries       : 2
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcr_jma_weather_warning_state_lookup(uint8_t id) {
    switch (id) {
        case 1: return "発表";
        case 2: return "解除";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
