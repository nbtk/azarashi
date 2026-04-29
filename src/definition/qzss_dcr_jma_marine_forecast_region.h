#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_marine_forecast_region
// Variable      : qzss_dcr_jma_marine_forecast_region
// Entries       : 49
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCR_JMA_MARINE_FORECAST_REGION_Entry { uint16_t id; const char* label; };
inline constexpr QZSS_DCR_JMA_MARINE_FORECAST_REGION_Entry QZSS_DCR_JMA_MARINE_FORECAST_REGION_TABLE[] = {
    {1000u, "日本海北部及びオホーツク海南部"},

    {1010u, "サハリン東方海上"},

    {1020u, "サハリン西方海上"},

    {1030u, "網走沖"},

    {1040u, "宗谷海峡"},

    {1050u, "北海道西方海上"},

    {1100u, "北海道南方及び東方海上"},

    {1110u, "北海道東方海上"},

    {1120u, "釧路沖"},

    {1130u, "日高沖"},

    {1140u, "津軽海峡"},

    {1150u, "檜山津軽沖"},

    {2000u, "三陸沖"},

    {2010u, "三陸沖東部"},

    {2020u, "三陸沖西部"},

    {3000u, "関東海域"},

    {3010u, "関東海域北部"},

    {3020u, "関東海域南部"},

    {3100u, "日本海中部"},

    {3110u, "沿海州南部沖"},

    {3120u, "秋田沖"},

    {3130u, "佐渡沖"},

    {3140u, "能登沖"},

    {3200u, "東海海域"},

    {3210u, "東海海域東部"},

    {3220u, "東海海域西部"},

    {3230u, "東海海域南部"},

    {4000u, "四国沖及び瀬戸内海"},

    {4010u, "瀬戸内海"},

    {4020u, "四国沖北部"},

    {4030u, "四国沖南部"},

    {4100u, "日本海西部"},

    {4110u, "日本海北西部"},

    {4120u, "山陰沖東部及び若狭湾付近"},

    {4130u, "山陰沖西部"},

    {5000u, "対馬海峡"},

    {5100u, "九州西方海上"},

    {5110u, "済州島西海上"},

    {5120u, "長崎西海上"},

    {5130u, "女島南西海上"},

    {5200u, "九州南方海上及び日向灘"},

    {5210u, "日向灘"},

    {5220u, "鹿児島海域"},

    {5230u, "奄美海域"},

    {6000u, "沖縄海域"},

    {6010u, "東シナ海南部"},

    {6020u, "沖縄東方海上"},

    {6030u, "沖縄南方海上"},

    {10000u, "その他の地方海上予報区"},
};
inline constexpr const char* qzss_dcr_jma_marine_forecast_region_lookup(uint16_t id) {
    int lo = 0, hi = 49 - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (QZSS_DCR_JMA_MARINE_FORECAST_REGION_TABLE[mid].id == id) return QZSS_DCR_JMA_MARINE_FORECAST_REGION_TABLE[mid].label;
        if (QZSS_DCR_JMA_MARINE_FORECAST_REGION_TABLE[mid].id  < id) lo = mid + 1;
        else hi = mid - 1;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
