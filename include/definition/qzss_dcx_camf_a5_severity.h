#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a5_severity
// Variable      : qzss_dcx_camf_a5_severity
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a5_severity_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Unknown";
        case 1: return "Moderate - Possible threat to life or property";
        case 2: return "Severe - Significant threat to life or property";
        case 3: return "Extreme - Extraordinary threat to life or property";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
