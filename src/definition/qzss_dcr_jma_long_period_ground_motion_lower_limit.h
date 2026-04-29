#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_long_period_ground_motion_lower_limit
// Variable      : qzss_dcr_jma_long_period_ground_motion_lower_limit
// Entries       : 7
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_long_period_ground_motion_lower_limit_lookup(uint8_t id) {
    switch (id) {
        case 0: return "None";
        case 1: return "長周期地震動階級1未満";
        case 2: return "長周期地震動階級1";
        case 3: return "長周期地震動階級2";
        case 4: return "長周期地震動階級3";
        case 5: return "長周期地震動階級4";
        case 7: return "不明";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
