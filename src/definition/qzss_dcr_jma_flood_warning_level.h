#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_flood_warning_level
// Variable      : qzss_dcr_jma_flood_warning_level
// Entries       : 5
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_flood_warning_level_lookup(uint8_t id) {
    switch (id) {
        case 1: return "警報解除";
        case 2: return "氾濫警戒情報";
        case 3: return "氾濫危険情報";
        case 4: return "氾濫発生情報";
        case 15: return "その他の警戒レベル";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
