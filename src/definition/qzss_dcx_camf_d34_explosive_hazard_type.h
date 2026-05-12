#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d34_explosive_hazard_type
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d34_explosive_hazard_type_lookup(uint8_t id) {
    switch (id) {
        case 0: return "PE1 - Mass explosion hazard in which the entire body of explosives explodes as one.";
        case 1: return "PE2 - Serious projectile hazard but does not have a mass explosion hazard.";
        case 2: return "PE3 - Fire hazard and either a minor blast hazard or a minor projection hazard, or both, but does not have a mass explosion hazard. Explosives which give rise to considerable radiant heat or which burn to produce a minor blast or projection hazard.";
        case 3: return "PE4 - Fire or slight explosion hazard, or both, with only local effect. Explosives which present only a low hazard in the event of ignition or initiation, where no significant blast or projection of fragments of appreciable size or range is expected.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
