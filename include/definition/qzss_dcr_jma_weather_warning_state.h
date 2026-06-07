#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_weather_warning_state
// Variable      : qzss_dcr_jma_weather_warning_state
// Entries       : 2
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_weather_warning_state_lookup(uint8_t id) {
    switch (id) {
        case 1: return "発表";
        case 2: return "解除";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
