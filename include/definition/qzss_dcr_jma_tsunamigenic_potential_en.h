#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_tsunamigenic_potential
// Variable      : qzss_dcr_jma_tsunamigenic_potential_en
// Entries       : 6
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_tsunamigenic_potential_en_lookup(uint8_t id) {
    switch (id) {
        case 0: return "There is No Possibility of a Tsunami";
        case 1: return "There is a Possibility of a Destructive Ocean-Wide Tsunami";
        case 2: return "There is a Possibility of a Destructive Regional Tsunami";
        case 3: return "There is a Possibility of a Destructive Local Tsunami Near the Epicenter";
        case 4: return "There is a Very Small Possibility of a Destructive Local Tsunami";
        case 7: return "There is a Possibility of a Tsunami";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
