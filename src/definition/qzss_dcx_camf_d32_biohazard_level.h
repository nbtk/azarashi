#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d32_biohazard_level
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d32_biohazard_level_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Biohazard Level 1/4: Often pertains to agents that include viruses and bacteria, this biosafety level requires minimal precaution, such as wearing face masks and maintaining no close contact. The biological hazard examples in the first level include E. coli and other non-infectious bacteria.";
        case 1: return "Biohazard Level 2/4: Usually causing severe diseases to humans, the second level classifies agents that can be transmitted through direct contact with infected materials. HIV and hepatitis B are some biological hazard examples that pose moderate risks to humans.";
        case 2: return "Biohazard Level 3/4: Mainly through respiratory transmission, pathogens that are highly likely to become airborne can cause serious or lethal diseases to humans. Mycobacterium tuberculosis, the bacteria that causes tuberculosis, is an example of a level-3 biohazard.";
        case 3: return "Biohazard Level 4/4: Extremely dangerous pathogens that expose humans to life-threatening diseases, the fourth and last level requires workers to utilise maximum protection and containment. Some biological hazard examples are the Ebola virus and the Lassa virus.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
