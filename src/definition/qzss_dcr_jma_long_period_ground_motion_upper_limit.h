#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_long_period_ground_motion_upper_limit
// Variable      : qzss_dcr_jma_long_period_ground_motion_upper_limit
// Entries       : 8
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_long_period_ground_motion_upper_limit_lookup(uint8_t id) {
    switch (id) {
        case 0: return "None";
        case 1: return "長周期地震動階級1未満";
        case 2: return "長周期地震動階級1";
        case 3: return "長周期地震動階級2";
        case 4: return "長周期地震動階級3";
        case 5: return "長周期地震動階級4";
        case 6: return "〜程度以上";
        case 7: return "不明";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
