#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a3_provider_identifier
// Variable      : qzss_dcx_camf_a3_provider_identifier_fiji
// Entries       : 5
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a3_provider_identifier_fiji_lookup(uint8_t id) {
    switch (id) {
        case 1: return "National Disaster Management Office";
        case 2: return "Fiji Meteorological Service";
        case 3: return "Hydrology Section, Fiji Water Authority";
        case 4: return "Mineral Resources Department";
        case 5: return "Fiji Broadcasting Corporation";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
