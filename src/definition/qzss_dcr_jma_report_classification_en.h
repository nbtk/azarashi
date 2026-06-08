#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_report_classification
// Variable      : qzss_dcr_jma_report_classification_en
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_report_classification_en_lookup(uint8_t id) {
#if AZARAC_LANG_EN
    switch (id) {
        case 1: return "Maximum Priority";
        case 2: return "Priority";
        case 3: return "Regular";
        case 7: return "Training/Test";
        default: return std::nullopt;
    }
#else
    (void)id;
    return std::nullopt;
#endif
}

} // namespace def
} // namespace azaraC
