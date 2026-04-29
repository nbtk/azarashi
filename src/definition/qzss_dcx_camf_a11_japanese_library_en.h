#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a11_japanese_library
// Variable      : qzss_dcx_camf_a11_japanese_library_en
// Entries       : 38
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_Entry { uint16_t id; const char* label; };
inline constexpr QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_Entry QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_TABLE[] = {
    {0u, ""},

    {1u, "Take the best immediate action to save your life."},

    {126u, "This is a test message for DCX."},

    {127u, "Take the best immediate action to save your life."},

    {128u, "Missile launched, missile launched. It is believed that a missile was launched. Please take shelter inside buildings or underground."},

    {129u, "Missile passed, missile passed. It is believed that the previous missile has passed over the area. The call for evacuation will be canceled. If you find any suspicious object, please stay away from it and inform the police or the fire department immediately."},

    {130u, "It is believed that the previous missile has dropped in the sea. The call for evacuation will be canceled. If you find any suspicious object, please stay away from it and inform the police or the fire department immediately."},

    {131u, "It is believed that the previous missile will not come to Japan. The call for evacuation will be canceled."},

    {132u, "Take shelter immediately, take shelter immediately. Please take shelter inside buildings or underground. It is believed that a missile will drop around this area. Please take shelter immediately."},

    {133u, "The previous missile has been intercepted and destroyed. There is a possibility of pieces of the destroyed missile dropping. We will keep you informed. Please stay indoors for shelter."},

    {134u, "Missile dropped, missile dropped. It is believed that a missile has dropped around this area. We will keep you informed. Please stay indoors for shelter."},

    {135u, "It is believed that the previous missile will not drop in Japan. The call for evacuation will be canceled."},

    {136u, "This is a test message for J-Alert."},

    {255u, "Take immediate action to save your life."},

    {256u, "Stay."},

    {257u, "Stay. Under/inside a solid structure."},

    {258u, "Stay. 3rd floor or higher."},

    {259u, "Stay. Underground."},

    {260u, "Stay. Mountain."},

    {261u, "Stay. Water area."},

    {262u, "Stay. Building where chemicals are handled, such as a factory."},

    {263u, "Stay. Cliffs and areas at risk of collapse."},

    {512u, "Move to/toward"},

    {513u, "Move to/toward Under/inside a solid structure."},

    {514u, "Move to/toward 3rd floor or higher."},

    {515u, "Move to/toward Underground."},

    {516u, "Move to/toward Mountain."},

    {517u, "Move to/toward Water area."},

    {518u, "Move to/toward Building where chemicals are handled, such as a factory."},

    {519u, "Move to/toward Cliffs and areas at risk of collapse."},

    {768u, "Keep away from"},

    {769u, "Keep away from Under/inside a solid structure."},

    {770u, "Keep away from 3rd floor or higher."},

    {771u, "Keep away from Underground."},

    {772u, "Keep away from Mountain."},

    {773u, "Keep away from Water area."},

    {774u, "Keep away from Building where chemicals are handled, such as a factory."},

    {775u, "Keep away from Cliffs and areas at risk of collapse."},
};
inline constexpr const char* qzss_dcx_camf_a11_japanese_library_en_lookup(uint16_t id) {
    int lo = 0, hi = 38 - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_TABLE[mid].id == id) return QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_TABLE[mid].label;
        if (QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_EN_TABLE[mid].id  < id) lo = mid + 1;
        else hi = mid - 1;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
