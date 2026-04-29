#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d19_avalanche_warning_level
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d19_avalanche_warning_level_lookup(uint8_t id) {
    switch (id) {
        case 0: return "1 – Low. Generally stable conditions. Triggering is generally possible only from high additional loads in isolated areas of very steep, extreme terrain. Only small and medium natural avalanches are possible.";
        case 1: return "2 – Moderate. Heightened avalanche conditions on specific terrain features. Triggering is possible, primarily from high additional loads, particularly on the indicated steep slopes. Very large natural avalanches are unlikely.";
        case 2: return "3 – Considerable. Dangerous avalanche conditions Triggering is possible, even from low additional loads, particularly on the indicated steep slopes. In certain situations, some large, and in isolated cases very large natural avalanches are possible.";
        case 3: return "4 – High. Very dangerous avalanche conditions. Triggering is likely, even from low additional loads, on many steep slopes. In some cases, numerous large and often very large natural avalanches can be expected.";
        case 4: return "5 – Very high. Extraordinary avalanche conditions. Numerous very large and often extremely large natural avalanches can be expected, even in moderately steep terrain.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
