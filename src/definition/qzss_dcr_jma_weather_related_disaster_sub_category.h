#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_weather_related_disaster_sub_category
// Variable      : qzss_dcr_jma_weather_related_disaster_sub_category
// Entries       : 11
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_Entry { uint8_t id; const char* label; };
inline constexpr QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_Entry QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_TABLE[] = {
    {1u, "暴風雪特別警報"},

    {2u, "大雨特別警報"},

    {3u, "暴風特別警報"},

    {4u, "大雪特別警報"},

    {5u, "波浪特別警報"},

    {6u, "高潮特別警報"},

    {7u, "全ての気象特別警報"},

    {21u, "記録的短時間大雨情報"},

    {22u, "竜巻注意情報"},

    {23u, "土砂災害警戒情報"},

    {31u, "その他の警報等情報要素"},
};
inline constexpr const char* qzss_dcr_jma_weather_related_disaster_sub_category_lookup(uint8_t id) {
    int lo = 0, hi = 11 - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_TABLE[mid].id == id) return QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_TABLE[mid].label;
        if (QZSS_DCR_JMA_WEATHER_RELATED_DISASTER_SUB_CATEGORY_TABLE[mid].id  < id) lo = mid + 1;
        else hi = mid - 1;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
