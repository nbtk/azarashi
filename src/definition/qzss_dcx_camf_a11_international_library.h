#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a11_international_library
// Variable      : qzss_dcx_camf_a11_international_library
// Entries       : 32
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_TABLE[] = {
    "",
    "You are in the danger zone, leave the area immediately. Listen to radio or media for directions and information.",
    "You are in the danger zone, leave the area immediately and reach the evacuation point indicated by the area plotted in yellow. Listen to radio or media for directions and information.",
    "Seek shelter in a building immediately. Stay under cover and stay informed.",
    "Seek out a cellar or interior rooms on lower floors.",
    "If you are in an alpine terrain, start descending immediately and seek for shelter.",
    "Quickly move into interior rooms. If you are in a vehicle: Stop driving immediately on the edge of the road. If a building is nearby, seek shelter in that building.",
    "If you are in open terrain and you cannot find shelter, lie face-down on the ground and protect your head and neck with your hands, in a hollow where possible.",
    "Prepare for evacuation. Take only the essentials with you, especially ID cards, passport, credit cards and cash. Evacuate only after the instruction of the emergency authorities.",
    "Prepare emergency food and relief material: Check and restock your equipment and supplies of water, food, medicine, cash and batteries.",
    "Stay away from glass surfaces such as windows and glass doors. There is a risk of injury from glass splinters.",
    "Reduce your power consumption to a minimum.",
    "Reduce your water consumption to a minimum.",
    "Boil water before drinking it or using it in the kitchen.",
    "Keep at least one metre away from any conversation partners. Avoid physical contact with other people such as kissing and shaking hands. Wash your hands regularly and thoroughly.",
    "Do not drink any tap water. Avoid any skin contact with tap water. Only drink mineral water from a bottle. Turn off the water supply to your house.",
    "Watch out for escaping gas. This can be indicated by hissing noises or a typical gas odour. Do not use matches, lighters or the like: naked flames in combination with leaking gas can lead to explosions and fires.",
    "Do not go outside and do not use your car.",
    "Do not touch any objects that seem suspicious to you. Debris can cause additional hazards such as fires and explosions. Inform the emergency services about damage and debris.",
    "Do not enter smoke-filled rooms. Deadly gases can form there.",
    "Do not enter cellars or underground car parks.",
    "Do not leave pets or livestock outside.",
    "Do not touch any dead animals. Report any findings of dead wild animals to the authorities.",
    "Avoid driving.",
    "Avoid all items with metal parts such as umbrellas and bicycles. Do not bathe or shower during a thunderstorm. Bathing and showering can be life-threatening.",
    "Avoid rooms directly underneath the roof truss. Avoid very large rooms, such as halls, in which the ceiling is not supported by pillars.",
    "Avoid going outdoors. Keep away from trees, towers and masts. Keep at least 20 m away from power lines. Watch out for flying objects and falling objects.",
    "Avoid the danger area.",
    "Avoid going out when it is not necessary.",
    "This is only a test. You do not have to take any action or to adopt any particular sheltering behaviour.",
    "This replaces the warning previously in effect for this area.",
    "Conditions have improved and are no longer expected to meet alert criteria."
};
static constexpr uint8_t QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_BASE = 0;
static constexpr uint8_t QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_SIZE = 32;
inline const char* qzss_dcx_camf_a11_international_library_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_BASE || id >= QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_BASE + QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_SIZE) return nullptr;
    return QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_TABLE[id - QZSS_DCX_CAMF_A11_INTERNATIONAL_LIBRARY_BASE];
}

} // namespace def
} // namespace azaraC
