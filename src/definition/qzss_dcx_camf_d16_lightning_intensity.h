#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d16_lightning_intensity
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_d16_lightning_intensity_lookup(uint8_t id) {
    switch (id) {
        case 0: return "LAL 1 - No thunderstorms";
        case 1: return "LAL 2 - Isolated thunderstorms. Light rain will occasionally reach the ground. Lightning is very infrequent, 1 to 5 cloud to ground strikes in a 5-minute period.";
        case 2: return "LAL 3 - Widely scattered thunderstorms. Light to moderate rain will reach the ground. Lightning is infrequent, 6 to 10 cloud to ground strikes in a 5-minute period.";
        case 3: return "LAL 4 - Scattered thunderstorms. Moderate rain is commonly produced Lightning is frequent, 11 to 15 cloud to ground strikes in a 5-minute period.";
        case 4: return "LAL 5 - Numerous thunderstorms. Rainfall is moderate to heavy. Lightning is frequent and intense, greater than 15 cloud to ground strikes in a 5-minute period.";
        case 5: return "LAL 6 - Dry lightning (same as LAL 3 but without rain). This type of lightning has the potential for extreme fire activity and is normally.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
