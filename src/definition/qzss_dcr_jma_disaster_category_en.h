#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_disaster_category
// Variable      : qzss_dcr_jma_disaster_category_en
// Entries       : 12
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCR_JMA_DISASTER_CATEGORY_EN_TABLE[] = {
    "Earthquake Early Warning",
    "Hypocenter",
    "Seismic Intensity",
    "Nankai Trough Earthquake",
    "Tsunami",
    "Northwest Pacific Tsunami",
    std::nullopt,
    "Volcano",
    "Ash Fall",
    "Weather",
    "Flood",
    "Typhoon",
    std::nullopt,
    "Marine"
};
inline constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE = 1;
inline constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_EN_SIZE = 14;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_disaster_category_en_lookup(uint8_t id) {
#if AZARAC_LANG_EN
    if (id < QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE || id >= QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE + QZSS_DCR_JMA_DISASTER_CATEGORY_EN_SIZE) return std::nullopt;
    return QZSS_DCR_JMA_DISASTER_CATEGORY_EN_TABLE[id - QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE];
#else
    (void)id;
    return std::nullopt;
#endif
}

} // namespace def
} // namespace azaraC
