#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a11_international_library
// Variable      : qzss_dcx_camf_a11_international_library_code
// Entries       : 32
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_TABLE[] = {
    "IC-A-01",
    "IC-A-02",
    "IC-A-03",
    "IC-A-04",
    "IC-A-05",
    "IC-A-06",
    "IC-A-07",
    "IC-A-08",
    "IC-A-09",
    "IC-A-10",
    "IC-A-11",
    "IC-A-12",
    "IC-A-13",
    "IC-A-14",
    "IC-A-15",
    "IC-A-16",
    "IC-A-17",
    "IC-A-18",
    "IC-A-19",
    "IC-A-20",
    "IC-A-21",
    "IC-A-22",
    "IC-A-23",
    "IC-A-24",
    "IC-A-25",
    "IC-A-26",
    "IC-A-27",
    "IC-A-28",
    "IC-A-29",
    "IC-A-30",
    "IC-A-31",
    "IC-A-32"
};
inline constexpr uint8_t QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_SIZE = 32;
inline constexpr const char* qzss_dcx_camf_a11_international_library_code_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_BASE || id >= QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_BASE + QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_SIZE) return nullptr;
    return QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_TABLE[id - QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_CODE_BASE];
}

} // namespace def
} // namespace azaraC
