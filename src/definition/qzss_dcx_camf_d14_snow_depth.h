#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d14_snow_depth
// Entries       : 31
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCX_CAMF_D14_SNOW_DEPTH_TABLE[] = {
    "0cm < daily snow depth ≤ 20cm",
    "20cm < daily snow depth ≤ 40cm",
    "40cm < daily snow depth ≤ 60cm",
    "60cm < daily snow depth ≤ 80cm",
    "80cm < daily snow depth ≤ 100cm",
    "100cm < daily snow depth ≤ 120cm",
    "120cm < daily snow depth ≤ 140cm",
    "140cm < daily snow depth ≤ 160cm",
    "160cm < daily snow depth ≤ 180cm",
    "180cm < daily snow depth ≤ 200cm",
    "200cm < daily snow depth ≤ 220cm",
    "220cm < daily snow depth ≤ 240cm",
    "240cm < daily snow depth ≤ 260cm",
    "260cm < daily snow depth ≤ 280cm",
    "280cm < daily snow depth ≤ 300cm",
    "300cm < daily snow depth ≤ 320cm",
    "320cm < daily snow depth ≤ 340cm",
    "340cm < daily snow depth ≤ 360cm",
    "360cm < daily snow depth ≤ 380cm",
    "380cm < daily snow depth ≤ 400cm",
    "400cm < daily snow depth ≤ 420cm",
    "420cm < daily snow depth ≤ 440cm",
    "440cm < daily snow depth ≤ 460cm",
    "460cm < daily snow depth ≤ 480cm",
    "480cm < daily snow depth ≤ 500cm",
    "500cm < daily snow depth ≤ 520cm",
    "520cm < daily snow depth ≤ 540cm",
    "540cm < daily snow depth ≤ 560cm",
    "560cm < daily snow depth ≤ 580cm",
    "580cm < daily snow depth ≤ 600cm",
    "daily snow depth > 600cm"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D14_SNOW_DEPTH_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D14_SNOW_DEPTH_SIZE = 31;
inline constexpr const char* qzss_dcx_camf_d14_snow_depth_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D14_SNOW_DEPTH_BASE || id >= QZSS_DCX_CAMF_D14_SNOW_DEPTH_BASE + QZSS_DCX_CAMF_D14_SNOW_DEPTH_SIZE) return nullptr;
    return QZSS_DCX_CAMF_D14_SNOW_DEPTH_TABLE[id - QZSS_DCX_CAMF_D14_SNOW_DEPTH_BASE];
}

} // namespace def
} // namespace azaraC
