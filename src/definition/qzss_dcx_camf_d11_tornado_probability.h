#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d11_tornado_probability
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d11_tornado_probability_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Non-Threatening - Threat: No discernible threat to life and property. Minimum Action: Listen for forecast changes; review tornado safety rules. Potential Impact: None expected; strong wind gusts may still occur.";
        case 1: return "Very Low - Threat: A very low threat to life and property. Minimum Action: Preparations should be made for a very low likelihood (or a 2 to 4% probability) of tornadoes; isolated tornadoes of F0 to F1 intensity possible. Potential Impact: The potential for isolated locations to experience minor to moderate tornado damage.";
        case 2: return "Low - Threat: A low threat to life and property. Minimum Action: Preparations should be made for a low likelihood (or a 5 to 14% probability) of tornadoes; scattered tornadoes of F0 to F1 intensity possible. Potential Impact: The potential for scattered locations to experience minor to moderate tornado damage.";
        case 3: return "Moderate - Threat: A moderate threat to life and property. Minimum Action: Preparations should be made for a moderate likelihood (or a 15 to 29% probability) of tornadoes; many tornadoes (even families) of F0 to F1 intensity possible. Potential Impact: The potential for many locations to experience minor to moderate tornado damage (see below). Some tornadoes may have longer damage tracks.";
        case 4: return "High - Threat: A high threat to life and property. Minimum Action: Preparations should be made for a high likelihood (or a 30 to 44% probability) of tornadoes; scattered tornadoes possible with isolated tornadoes of F2 to F5 intensity also possible. Potential Impact: The potential for isolated locations to experience major tornado damage (see below), among scattered locations of minor to moderate tornado damage. Some tornadoes may have longer damage tracks.";
        case 5: return "Extreme - Threat: An extreme threat to life and property. Minimum Action: Preparations should be made for a very high likelihood (or a 45% probability or greater) of tornadoes; many tornadoes (even families) possible with scattered tornadoes of F2 to F5 intensity also possible. Potential Impact: The potential for scattered locations to experience major tornado damage (see below), among many locations of minor to moderate tornado damage. Some tornadoes may have longer damage tracks";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
