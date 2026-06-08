#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_typhoon_scale_category
// Variable      : qzss_dcr_jma_typhoon_scale_category
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_typhoon_scale_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "なし";
        case 1: return "大型";
        case 2: return "超大型";
        case 15: return "その他の大きさ階級分類";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
