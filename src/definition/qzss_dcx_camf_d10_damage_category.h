#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d10_damage_category
// Entries       : 6
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d10_damage_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Category 1 - Very dangerous winds will produce some damage. Scale 1 and Intensity 1";
        case 1: return "Category 2 - Extremely dangerous winds will cause extensive damage. Scale 1 and Intensity 2";
        case 2: return "Category 3 - Devastating damage will occur. Scale 1 and Intensity 3";
        case 3: return "Category 4 - Catastrophic damage will occur. Scale 2 and Intensity 1";
        case 4: return "Category 5 - Catastrophic damage will occur. Scale 2 and Intensity 2";
        case 5: return "Category 5 - Catastrophic damage will occur. Scale 3 and Intensity 3";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
