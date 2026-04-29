#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_volcanic_warning_code
// Variable      : qzss_dcr_jma_volcanic_warning_code
// Entries       : 15
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_Entry { uint8_t id; const char* label; };
inline constexpr QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_Entry QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_TABLE[] = {
    {11u, "レベル1(活火山であることに留意)"},

    {12u, "レベル2(火口周辺規制)"},

    {13u, "レベル3(入山規制)"},

    {14u, "レベル4(高齢者等避難)"},

    {15u, "レベル5(避難)"},

    {21u, "活火山であることに留意"},

    {22u, "火口周辺危険"},

    {23u, "入山危険"},

    {24u, "山麓厳重警戒"},

    {25u, "居住地域厳重警戒"},

    {35u, "活火山であることに留意(海底火山)"},

    {36u, "周辺海域警戒"},

    {52u, "噴火"},

    {62u, "噴火したもよう"},

    {127u, "その他の防災気象情報要素"},
};
inline constexpr const char* qzss_dcr_jma_volcanic_warning_code_lookup(uint8_t id) {
    int lo = 0, hi = 15 - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_TABLE[mid].id == id) return QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_TABLE[mid].label;
        if (QZSS_DCR_JMA_VOLCANIC_WARNING_CODE_TABLE[mid].id  < id) lo = mid + 1;
        else hi = mid - 1;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
