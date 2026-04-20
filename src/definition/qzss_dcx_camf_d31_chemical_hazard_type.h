#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d31_chemical_hazard_type
// Entries       : 16
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_TABLE[] = {
    "Explosives",
    "Flammable gases",
    "Flammable aerosols and aerosols",
    "Oxidizing gases",
    "Gases under pressure",
    "Flammable liquids",
    "Flammable solids",
    "Self-reactive substance/mixture",
    "Pyrophoric liquids. Pyrophoric materials are often water-reactive as well and will ignite when they contact water or humid air.",
    "Pyrophoric solids. Pyrophoric materials are often water-reactive as well and will ignite when they contact water or humid air.",
    "Self-heating substance/mixture",
    "Water-reactive - emits flammable gases",
    "Oxidising liquids",
    "Oxidising solids",
    "Organic peroxides",
    "Corrosive to metals"
};
static constexpr uint8_t QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_BASE = 0;
static constexpr uint8_t QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_SIZE = 16;
inline const char* qzss_dcx_camf_d31_chemical_hazard_type_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_BASE || id >= QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_BASE + QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_SIZE) return nullptr;
    return QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_TABLE[id - QZSS_DCX_CAMF_D31_CHEMICAL_HAZARD_TYPE_BASE];
}

} // namespace def
} // namespace azaraC
