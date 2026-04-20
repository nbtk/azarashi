#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_tsunamigenic_potential
// Variable      : qzss_dcr_jma_tsunamigenic_potential_en
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcr_jma_tsunamigenic_potential_en_lookup(uint8_t id) {
    switch (id) {
        case 0: return "There is No Possibility of a Tsunami";
        case 1: return "There is a Possibility of a Destructive Ocean-Wide Tsunami";
        case 2: return "There is a Possibility of a Destructive Regional Tsunami";
        case 3: return "There is a Possibility of a Destructive Local Tsunami Near the Epicenter";
        case 4: return "There is a Very Small Possibility of a destructive Local Tsunami";
        case 7: return "There is Possibility of a Tsunami";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
