#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_marine_warning_code
// Variable      : qzss_dcr_jma_marine_warning_code
// Entries       : 9
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_marine_warning_code_lookup(uint8_t id) {
    switch (id) {
        case 0: return "海上警報解除";
        case 10: return "海上着氷警報";
        case 11: return "海上濃霧警報";
        case 12: return "海上うねり警報";
        case 20: return "海上風警報";
        case 21: return "海上強風警報";
        case 22: return "海上暴風警報";
        case 23: return "海上台風警報";
        case 31: return "その他の警報等情報要素 海上警報";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
