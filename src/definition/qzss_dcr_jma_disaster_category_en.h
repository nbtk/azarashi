#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_disaster_category
// Variable      : qzss_dcr_jma_disaster_category_en
// Entries       : 12
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCR_JMA_DISASTER_CATEGORY_EN_TABLE[] = {
    "Earthquake Early Warning",
    "Hypocenter",
    "Seismic Intensity",
    "Nankai Trough Earthquake",
    "Tsunami",
    "Northwest Pacific Tsunami",
    nullptr,
    "Volcano",
    "Ash Fall",
    "Weather",
    "Flood",
    "Typhoon",
    nullptr,
    "Marine"
};
static constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE = 1;
static constexpr uint8_t QZSS_DCR_JMA_DISASTER_CATEGORY_EN_SIZE = 14;
inline const char* qzss_dcr_jma_disaster_category_en_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE || id >= QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE + QZSS_DCR_JMA_DISASTER_CATEGORY_EN_SIZE) return nullptr;
    return QZSS_DCR_JMA_DISASTER_CATEGORY_EN_TABLE[id - QZSS_DCR_JMA_DISASTER_CATEGORY_EN_BASE];
}

} // namespace def
} // namespace azaraC
