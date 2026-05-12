#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d15_flood_severity
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d15_flood_severity_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Minor Flooding - Minimal or no property damage, but possibly some public threat.";
        case 1: return "Moderate Flooding - Some inundation of structures and roads near stream. Some evacuations of people and/or transfer of property to higher elevations.";
        case 2: return "Major Flooding - Extensive inundation of structures and roads. Significant evacuations of people and/or transfer of property to higher elevations.";
        case 3: return "Record Flooding";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
