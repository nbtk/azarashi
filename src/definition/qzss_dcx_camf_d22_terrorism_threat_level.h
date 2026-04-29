#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d22_terrorism_threat_level
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d22_terrorism_threat_level_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Very low threat level. A violent act of terrorism is highly unlikely. Measures are in place to keep the population safe.";
        case 1: return "Low threat level. A violent act of terrorism is possible but unlikely. Measures are in place to keep the population safe.";
        case 2: return "Medium threat level. A violent act of terrorism could occur. Additional measures are in place to keep the population safe.";
        case 3: return "High threat level. A violent act of terrorism is likely. Heightened measures are in place to keep the population safe.";
        case 4: return "Critical threat level. A violent act of terrorism is highly likely and could occur imminently. Exceptional measures are in place to keep the population safe.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
