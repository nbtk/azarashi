#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d28_air_quality_index
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d28_air_quality_index_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Index value 0 - 50. Good. Green. Advisory: None.";
        case 1: return "Index value 51 - 100. Moderate. Yellow. Unusually sensitive individuals should consider limiting prolonged outdoor exertion.";
        case 2: return "Index 101 - 150. Unhealthy for sensitive groups. Orange. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion";
        case 3: return "Index 151 - 200. Unhealthy. Red. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion. Everyone else should limit prolonged outdoor exertion.";
        case 4: return "Index 201 - 300. Very unhealthy. Purple. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion. Everyone else should limit outdoor exertion.";
        case 5: return "Index 301 - 500. Hazardous.Brown.Everyone should avoid all physical activity outdoor.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
