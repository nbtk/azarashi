#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d18_drought_level
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d18_drought_level_lookup(uint8_t id) {
    switch (id) {
        case 0: return "D1 – Moderate Drought – PDSI = -2.0 to -2.9. Some damage to crops, pastures. Streams, reservoirs, or wells low, some water shortages developing or imminent. Voluntary water-use restrictions requested.";
        case 1: return "D2 – Severe Drought – PDSI = -3.0 to -3.9. Crop or pasture losses likely. Water shortages common. Water restrictions imposed.";
        case 2: return "D3 – Extreme Drought – PDSI = -4.0 to -4.9. Major crop/pasture losses. Widespread water shortages or restrictions.";
        case 3: return "D4 – Exceptional Drought – PDSI = -5.0 or less. Exceptional and widespread crop/pasture losses. Shortages of water in reservoirs, streams, and wells creating water emergencies.";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
