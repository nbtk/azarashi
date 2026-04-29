#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d23_fire_risk_level
// Entries       : 5
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d23_fire_risk_level_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Danger level 1/5 (low or none danger). Small fires cannot be entirely ruled out, but require a high energy input. Lightning hardly ever causes a fire. Rate of spread: Generally slow. Characteristics: Surface or crawling fires, crowns of trees are not affected, topsoil does not burn. Fire-fighting: Forest fire is easy to extinguish. Behaviour: Do not carelessly discard cigarettes, tobacco products or lighters.";
        case 1: return "Danger level 2/5 (moderate danger). Local fires can start spontaneously. Lightning only rarely causes a conflagration. Rate of spread: Slow to medium. Characteristics: Surface or crawling fires, crowns of trees are rarely affected, topsoil is burnt a little or not at all. Fire-fighting: Forest fire is ordinarily easy to extinguish. Behaviour: Do not carelessly discard cigarettes, tobacco products or lighters. Always watch barbecue fires and immediately extinguish stray sparks.";
        case 2: return "Danger level 3/5 (considerable danger): Burning matches and flying sparks from barbecue fires can ignite a fire. Lightning can also trigger widespread fires. Rate of spread: High in open terrain, medium in the forest. Characteristics. Topsoil is partly burnt; individual crown fires are possible. Fire-fighting: Forest fire can be extinguished only by experts using modern equipment. Behaviour: Light barbecue fires only in existing fire places. Always watch the fire and immediately extinguish stray sparks.";
        case 3: return "Danger level 4/5 (high danger). Burning matches, flying sparks from barbecue fires and lightning will very probably ignite a fire. Rate of spread: High, including in forests. Characteristics: Intense surface fires can ignite the crowns of individual trees, spotting is possible, burning topsoil. Fire-fighting: Forest fire is difficult to extinguish and commands extensive resources. Behaviour: As a general rule, do not make any fires outdoors. Permanent fire places (concreted base) in locations designated by the authorities can be used with the utmost caution. Do not make fires in strong winds.";
        case 4: return "Danger level 5/5 (very high danger). Fires can start at any time. Rate of spread: Very high over a long period. Characteristics: Very intense burning, extensive crown fires, long-distance spotting. Fire-fighting: Forest fire is virtually impossible to extinguish. Behaviour: Do not make any fires outdoors. Follow the instructions and observe the fire bans imposed by the local authorities.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
