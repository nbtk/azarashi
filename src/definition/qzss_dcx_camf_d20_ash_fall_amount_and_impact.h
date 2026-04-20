#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d20_ash_fall_amount_and_impact
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_d20_ash_fall_amount_and_impact_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Less than 1 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Possible minor damage to vehicles, houses and equipment caused by fine abrasive ash. Possible contamination of water supplies, particularly roof-fed tank supplies. Dust may affect road visibility and traction for an extended period.";
        case 1: return "1-5 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Minor damage to vehicles, houses and equipment caused by fine abrasive ash. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Dust may affect road visibility and traction for an extended period. Roads may need to be cleared to reduce the dust nuisance and prevent storm-water systems from becoming blocked. Possible crop damage. Some livestock may be affected.";
        case 2: return "5-100 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Most buildings will support the ash load but weaker roof structures may collapse at 100 mm ash thickness, particularly if the ash is wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road transport may be halted due to the build-up of ash on roads. Cars still working may soon stop due to clogging of air-filters. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Likely crop damage. Most pastures will be killed by over 50 mm of ash. Some livestock may be affected.";
        case 3: return "100-300 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Buildings that are not cleared of ash will run the risk of roof collapse, especially large flat roofed structures and if ash becomes wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road transport may be halted due to the build-up of ash on roads. Cars still working may soon stop due to clogging of air-filters. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Likely crop damage. Most pastures will be killed by over 50 mm of ash. Some livestock may be affected.";
        case 4: return "> 300 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Buildings that are not cleared of ash will run the risk of roof collapse, especially large flat roofed structures and if ash becomes wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road unusable until cleared. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Heavy kill of vegetation. Livestock and other animals killed or heavily distressed.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
