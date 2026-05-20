#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_northwest_pacific_tsunami_height
// Variable      : qzss_dcr_jma_northwest_pacific_tsunami_height_en
// Entries       : 8
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_northwest_pacific_tsunami_height_en_lookup(uint16_t id) {
    switch (id) {
        case 1: return "0.3m~1m";
        case 2: return "1m~3m";
        case 3: return "3m~5m";
        case 4: return "5m~10m";
        case 508: return "More than 10m";
        case 509: return "Huge";
        case 510: return "High";
        case 511: return "Unknown";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
