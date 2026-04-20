#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d7_hurricane_category
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_d7_hurricane_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Category 1/5 hurricane: Very dangerous winds will produce some damage. Winds range from 120 to 150 km/h. Falling debris could strike people, livestock and pets, and older mobile homes could be destroyed. Protected glass windows will generally make it through the hurricane without major damage. Frame homes, apartments and shopping centres may experience some damage, and snapped power lines could result in short-term power outages.";
        case 1: return "Category 2/5 hurricane: Extremely dangerous winds will cause extensive damage. Winds range between 150 and 180 km/h. There is a bigger risk of injury or death to people, livestock and pets from flying debris. Older mobile homes will likely be destroyed, and debris can ruin newer mobile homes, too. Frame homes, apartment buildings and shopping centres may see major roof and siding damage, and many trees will be uprooted. Residents should expect near total power loss after a Category 2 hurricane, with outages lasting anywhere from a few days to a few weeks.";
        case 2: return "Category 3/5 hurricane: Devastating damage will occur. In a Category 3 hurricane, winds range from 180 to 210 km/h. There is a high risk of injury or death to people, livestock and pets from flying and falling debris. Nearly all older mobile homes will be destroyed, and most new ones will experience significant damage. Even well-built frame homes, apartments and industrial buildings will likely experience major damage, and the storm will uproot many trees that may block roads. Electricity and water will likely be unavailable for several days to a few weeks after the storm.";
        case 3: return "Category 4/5 hurricane: Catastrophic damage will occur. During a Category 4 hurricane, winds range from 210 to 250 km/h. At these speeds, falling and flying debris poses a very high risk of injury or death to people, pets and livestock. Again, most mobile homes will be destroyed, even newer ones. Some frame homes may totally collapse, while well-built homes will likely see severe damage to their roofs, and apartment buildings can experience damage to upper floors. A Category 4 hurricane will blow out most windows on high-rise buildings, uproot most trees and will likely down many power lines.";
        case 4: return "Category 5/5 hurricane: Catastrophic damage will occur. In a Category 5 hurricane, the highest category hurricane, winds are 250 km/h or higher. People, livestock and pets can be in danger from flying debris, even indoors. Most mobile homes will be completely destroyed, and a high percentage of frame homes will be destroyed. Commercial buildings with wood roofs will experience severe damage, metal buildings may collapse and high-rise windows will nearly all be blown out. A Category 5 hurricane is likely to uproot most trees and ruin most power poles. People should expect long-term water shortages and power outages.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
