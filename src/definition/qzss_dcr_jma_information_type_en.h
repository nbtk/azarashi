#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_information_type
// Variable      : qzss_dcr_jma_information_type_en
// Entries       : 3
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_information_type_en_lookup(uint8_t id) {
#if AZARAC_LANG_EN
    switch (id) {
        case 0: return "Issue";
        case 1: return "Correction";
        case 2: return "Cancellation";
        default: return std::nullopt;
    }
#else
    (void)id;
    return std::nullopt;
#endif
}

} // namespace def
} // namespace azaraC
