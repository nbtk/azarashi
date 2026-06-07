#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d2_seismic_coefficient
// Entries       : 8
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d2_seismic_coefficient_lookup(uint8_t id) {
    switch (id) {
        case 0: return "2";
        case 1: return "3";
        case 2: return "4";
        case 3: return "5 weak";
        case 4: return "5 strong";
        case 5: return "6 weak";
        case 6: return "6 strong";
        case 7: return "7";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
