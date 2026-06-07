#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a3_provider_identifier
// Variable      : qzss_dcx_camf_a3_provider_identifier_japan
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a3_provider_identifier_japan_lookup(uint8_t id) {
    switch (id) {
        case 1: return "Foundation for MultiMedia Communications";
        case 2: return "Fire and Disaster Management Agency";
        case 3: return "Related Ministries";
        case 4: return "Local Government";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
