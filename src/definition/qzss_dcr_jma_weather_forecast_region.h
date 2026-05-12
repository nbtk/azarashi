#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcr_jma_weather_forecast_region
// Variable      : qzss_dcr_jma_weather_forecast_region
// Entries       : 75
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCR_JMA_WEATHER_FORECAST_REGION_Entry { uint32_t id; const char* label; };
inline constexpr QZSS_DCR_JMA_WEATHER_FORECAST_REGION_Entry QZSS_DCR_JMA_WEATHER_FORECAST_REGION_TABLE[] = {
    {11000u, "宗谷地方"},

    {12000u, "上川・留萌地方"},

    {12010u, "上川地方"},

    {12020u, "留萌地方"},

    {13000u, "網走・北見・紋別地方"},

    {14010u, "根室地方"},

    {14020u, "釧路地方"},

    {14030u, "十勝地方"},

    {14100u, "釧路・根室地方"},

    {15000u, "胆振・日高地方"},

    {15010u, "胆振地方"},

    {15020u, "日高地方"},

    {16000u, "石狩・空知・後志地方"},

    {16010u, "石狩地方"},

    {16020u, "空知地方"},

    {16030u, "後志地方"},

    {16100u, "石狩・空知地方"},

    {17000u, "渡島・檜山地方"},

    {17010u, "渡島地方"},

    {17020u, "檜山地方"},

    {20000u, "青森県"},

    {30000u, "岩手県"},

    {40000u, "宮城県"},

    {50000u, "秋田県"},

    {60000u, "山形県"},

    {70000u, "福島県"},

    {80000u, "茨城県"},

    {90000u, "栃木県"},

    {100000u, "群馬県"},

    {110000u, "埼玉県"},

    {120000u, "千葉県"},

    {130000u, "東京都"},

    {130010u, "東京地方"},

    {130020u, "伊豆諸島北部"},

    {130030u, "伊豆諸島南部"},

    {140000u, "神奈川県"},

    {150000u, "新潟県"},

    {160000u, "富山県"},

    {170000u, "石川県"},

    {180000u, "福井県"},

    {190000u, "山梨県"},

    {200000u, "長野県"},

    {210000u, "岐阜県"},

    {220000u, "静岡県"},

    {230000u, "愛知県"},

    {240000u, "三重県"},

    {250000u, "滋賀県"},

    {260000u, "京都府"},

    {270000u, "大阪府"},

    {280000u, "兵庫県"},

    {290000u, "奈良県"},

    {300000u, "和歌山県"},

    {310000u, "鳥取県"},

    {320000u, "島根県"},

    {330000u, "岡山県"},

    {340000u, "広島県"},

    {350000u, "山口県"},

    {360000u, "徳島県"},

    {370000u, "香川県"},

    {380000u, "愛媛県"},

    {390000u, "高知県"},

    {400000u, "福岡県"},

    {410000u, "佐賀県"},

    {420000u, "長崎県"},

    {430000u, "熊本県"},

    {440000u, "大分県"},

    {450000u, "宮崎県"},

    {460000u, "鹿児島県"},

    {460040u, "奄美地方"},

    {460100u, "鹿児島県(奄美地方除く)"},

    {471000u, "沖縄本島地方"},

    {472000u, "大東島地方"},

    {473000u, "宮古島地方"},

    {474000u, "八重山地方"},

    {500000u, "その他の府県予報区"},
};
inline constexpr const char* qzss_dcr_jma_weather_forecast_region_lookup(uint32_t id) {
    uint8_t lo = 0, hi = 75;
    while (lo < hi) {
        uint8_t mid = lo + (hi - lo) / 2;
        if (QZSS_DCR_JMA_WEATHER_FORECAST_REGION_TABLE[mid].id == id) return QZSS_DCR_JMA_WEATHER_FORECAST_REGION_TABLE[mid].label;
        if (QZSS_DCR_JMA_WEATHER_FORECAST_REGION_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
