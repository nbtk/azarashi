#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a3_provider_identifier
// Variable      : qzss_dcx_camf_a3_provider_identifier_australia
// Entries       : 12
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_TABLE[] = {
    "National Emergency Management Agency",
    "Bureau of Meteorology",
    "Australian Climate Service",
    "Geoscience Australia",
    "Commonwealth Scientific and Industrial Research Organisation",
    "Australian Bureau of Statistics",
    "Resilience New South Wales",
    "State Emergency Service New South Wales",
    "New South Wales Rural Fire Service",
    "Joint Australian Tsunami Warning Centre",
    "Flood Knowledge Centre",
    "Australian Broadcasting Corporation"
};
static constexpr uint8_t QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_BASE = 1;
static constexpr uint8_t QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_SIZE = 12;
inline const char* qzss_dcx_camf_a3_provider_identifier_australia_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_BASE || id >= QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_BASE + QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_SIZE) return nullptr;
    return QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_TABLE[id - QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_AUSTRALIA_BASE];
}

} // namespace def
} // namespace azaraC
