#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a3_provider_identifier
// Variable      : qzss_dcx_camf_a3_provider_identifier_thailand
// Entries       : 13
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_TABLE[] = {
    "Department of Disaster Prevention and Mitigation",
    "Thai Meteorological Department",
    "National Disaster Warning Center",
    "Department of Mineral Resources",
    "Navy Hydrographic Department, Royal Thai Navy",
    "Department of Water Resources",
    "Royal Irrigation Department",
    "Department of Pollution Control",
    "Geo-Informatics and Space Technology Development Agency",
    "Electricity Generating Authority of Thailand",
    "Royal Forest Department",
    "Department of Parks, Wildlife and Plant Conservation",
    "Water Crisis Prevention Center"
};
static constexpr uint8_t QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_BASE = 1;
static constexpr uint8_t QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_SIZE = 13;
inline const char* qzss_dcx_camf_a3_provider_identifier_thailand_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_BASE || id >= QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_BASE + QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_SIZE) return nullptr;
    return QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_TABLE[id - QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER_THAILAND_BASE];
}

} // namespace def
} // namespace azaraC
