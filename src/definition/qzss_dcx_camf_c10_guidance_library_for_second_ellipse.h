#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_c10_guidance_library_for_second_ellipse
// Variable      : qzss_dcx_camf_c10_guidance_library_for_second_ellipse
// Entries       : 19
// Strategy      : binary_search

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_Entry { uint8_t id; std::string_view label; };
inline constexpr QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_Entry QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_TABLE[] = {
    {0u, ""},

    {1u, "Prepare for evacuation. Take only the essentials with you, especially ID cards, passport, credit cards and cash. Evacuate only after the instruction of the emergency authorities."},

    {2u, "Prepare emergency food and relief material: Check and restock your equipment and supplies of water, food, medicine, cash and batteries."},

    {3u, "Be prepared to protect yourself and your property. Flooding of properties and transport networks is expected. Disruption to power, communications and water supplies are possible. Evacuation may be required. Dangerous driving conditions due to reduced visibility and aquaplaning."},

    {4u, "Have iodine tablets ready. DO NOT take the iodine tablets now. If this becomes necessary, we will inform you in good time."},

    {5u, "Keep your smartphone charged to be able to receive further instructions and information."},

    {6u, "Avoid using lifts."},

    {7u, "Avoid the danger area."},

    {8u, "Avoid driving."},

    {9u, "Rescue operation under process by security forces and emergency services. Avoid moving to facilitate security and emergency actions."},

    {10u, "Check with the weather services and local authorities for additional information."},

    {11u, "Find out the location of the information points set up by the authorities on official channels (radio, internet, TV, social networks...)."},

    {12u, "Sensitive or vulnerable people should not go out unless they must."},

    {13u, "Protect the most vulnerable and hear from your loved ones. Be aware of their special needs and support, as required. If you notice distressed or vulnerable persons, contact the emergency services. Provide first aid if necessary but do not put yourself in any danger."},

    {14u, "Pay attention to announcements made by the police, fire brigade and by officials."},

    {15u, "Stay aware, keep listening to official instructions broadcast on the radio, television, websites and social networks pages."},

    {16u, "Only make phone calls in serious emergencies to avoid overloading the mobile network."},

    {30u, "This is only a test. You do not have to take any action or to adopt any particular sheltering behaviour."},

    {31u, "Conditions have improved and are no longer expected to meet alert criteria."},
};
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_c10_guidance_library_for_second_ellipse_lookup(uint8_t id) {
    uint8_t lo = 0, hi = 19;
    while (lo < hi) {
        uint8_t mid = static_cast<uint8_t>(lo + (hi - lo) / 2);
        if (QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_TABLE[mid].id == id) return QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_TABLE[mid].label;
        if (QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return std::nullopt;
}

} // namespace def
} // namespace azaraC
