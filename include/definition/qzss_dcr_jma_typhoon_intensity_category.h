#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_typhoon_intensity_category
// Variable      : qzss_dcr_jma_typhoon_intensity_category
// Entries       : 5
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_typhoon_intensity_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "なし";
        case 1: return "強い";
        case 2: return "非常に強い";
        case 3: return "猛烈な";
        case 15: return "その他の強さ階級分類";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
