#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_seismic_intensity_lower_limit
// Variable      : qzss_dcr_jma_seismic_intensity_lower_limit
// Entries       : 12
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_TABLE[] = {
    "震度0",
    "震度1",
    "震度2",
    "震度3",
    "震度4",
    "震度5弱",
    "震度5強",
    "震度6弱",
    "震度6強",
    "震度7",
    nullptr,
    nullptr,
    nullptr,
    "なし",
    "不明"
};
static constexpr uint8_t QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_BASE = 1;
static constexpr uint8_t QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_SIZE = 15;
inline const char* qzss_dcr_jma_seismic_intensity_lower_limit_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_BASE || id >= QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_BASE + QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_SIZE) return nullptr;
    return QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_TABLE[id - QZSS_DCR_JMA_SEISMIC_INTENSITY_LOWER_LIMIT_BASE];
}

} // namespace def
} // namespace azaraC
