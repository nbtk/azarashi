#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcr_jma_disaster_category
// Variable      : qzss_dcr_jma_disaster_category
// Entries       : 12
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCR_JMA_DISASTER_CATEGORY_TABLE[] = {
    "緊急地震速報",
    "震源",
    "震度",
    "南海トラフ地震",
    "津波",
    "北西太平洋津波",
    nullptr,
    "火山",
    "降灰",
    "気象",
    "洪水",
    "台風",
    nullptr,
    "海上"
};
inline constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_BASE = 1;
inline constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_SIZE = 14;
inline constexpr const char* qzss_dcr_jma_disaster_category_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_DISASTER_CATEGORY_BASE || id >= QZSS_DCR_JMA_DISASTER_CATEGORY_BASE + QZSS_DCR_JMA_DISASTER_CATEGORY_SIZE) return nullptr;
    return QZSS_DCR_JMA_DISASTER_CATEGORY_TABLE[id - QZSS_DCR_JMA_DISASTER_CATEGORY_BASE];
}

} // namespace def
} // namespace azaraC
