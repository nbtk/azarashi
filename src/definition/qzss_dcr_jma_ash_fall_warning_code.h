#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_ash_fall_warning_code
// Variable      : qzss_dcr_jma_ash_fall_warning_code
// Entries       : 5
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_ash_fall_warning_code_lookup(uint8_t id) {
    switch (id) {
        case 1: return "少量の降灰";
        case 2: return "やや多量の降灰";
        case 3: return "多量の降灰";
        case 4: return "小さな噴石の落下";
        case 7: return "その他の防災気象情報要素2";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
