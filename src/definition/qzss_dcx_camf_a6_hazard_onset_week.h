#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a6_hazard_onset_week
// Variable      : qzss_dcx_camf_a6_hazard_onset_week
// Entries       : 2
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a6_hazard_onset_week_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Current";
        case 1: return "Next";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
