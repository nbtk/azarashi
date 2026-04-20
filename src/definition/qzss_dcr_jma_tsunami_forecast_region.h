#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_tsunami_forecast_region
// Variable      : qzss_dcr_jma_tsunami_forecast_region
// Entries       : 99
// Strategy      : binary_search

#include <cstdint>

namespace azaraC {
namespace def {

struct QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_Entry { uint16_t id; const char* label; };
static constexpr QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_Entry QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_TABLE[] = {
    {100u, "北海道太平洋沿岸東部"},

    {101u, "北海道太平洋沿岸中部"},

    {102u, "北海道太平洋沿岸西部"},

    {110u, "北海道日本海沿岸北部"},

    {111u, "北海道日本海沿岸南部"},

    {120u, "オホーツク海沿岸"},

    {191u, "北海道太平洋沿岸"},

    {192u, "北海道日本海沿岸"},

    {200u, "青森県日本海沿岸"},

    {201u, "青森県太平洋沿岸"},

    {202u, "陸奥湾"},

    {210u, "岩手県"},

    {220u, "宮城県"},

    {230u, "秋田県"},

    {240u, "山形県"},

    {250u, "福島県"},

    {281u, "青森県"},

    {291u, "東北地方太平洋沿岸"},

    {292u, "東北地方日本海沿岸"},

    {300u, "茨城県"},

    {310u, "千葉県九十九里・外房"},

    {311u, "千葉県内房"},

    {312u, "東京湾内湾"},

    {320u, "伊豆諸島"},

    {321u, "小笠原諸島"},

    {330u, "相模湾・三浦半島"},

    {340u, "新潟県上中下越"},

    {341u, "佐渡"},

    {350u, "富山県"},

    {360u, "石川県能登"},

    {361u, "石川県加賀"},

    {370u, "福井県"},

    {380u, "静岡県"},

    {390u, "愛知県外海"},

    {391u, "伊勢・三河湾"},

    {400u, "三重県南部"},

    {481u, "千葉県"},

    {482u, "神奈川県"},

    {483u, "新潟県"},

    {484u, "石川県"},

    {485u, "愛知県"},

    {486u, "三重県"},

    {491u, "関東地方"},

    {492u, "伊豆・小笠原諸島"},

    {493u, "北陸地方"},

    {494u, "東海地方"},

    {500u, "京都府"},

    {510u, "大阪府"},

    {520u, "兵庫県北部"},

    {521u, "兵庫県瀬戸内海沿岸"},

    {522u, "淡路島南部"},

    {530u, "和歌山県"},

    {540u, "鳥取県"},

    {550u, "島根県出雲・石見"},

    {551u, "隠岐"},

    {560u, "岡山県"},

    {570u, "広島県"},

    {580u, "徳島県"},

    {590u, "香川県"},

    {600u, "愛媛県宇和海沿岸"},

    {601u, "愛媛県瀬戸内海沿岸"},

    {610u, "高知県"},

    {681u, "兵庫県"},

    {682u, "島根県"},

    {683u, "愛媛県"},

    {691u, "近畿四国太平洋沿岸"},

    {692u, "近畿中国日本海沿岸"},

    {693u, "瀬戸内海沿岸"},

    {700u, "山口県日本海沿岸"},

    {701u, "山口県瀬戸内海沿岸"},

    {710u, "福岡県瀬戸内海沿岸"},

    {711u, "福岡県日本海沿岸"},

    {712u, "有明・八代海"},

    {720u, "佐賀県北部"},

    {730u, "長崎県西方"},

    {731u, "壱岐・対馬"},

    {740u, "熊本県天草灘沿岸"},

    {750u, "大分県瀬戸内海沿岸"},

    {751u, "大分県豊後水道沿岸"},

    {760u, "宮崎県"},

    {770u, "鹿児島県東部"},

    {771u, "種子島・屋久島地方"},

    {772u, "奄美群島・トカラ列島"},

    {773u, "鹿児島県西部"},

    {781u, "山口県"},

    {782u, "福岡県"},

    {783u, "佐賀県"},

    {784u, "長崎県"},

    {785u, "熊本県"},

    {786u, "大分県"},

    {787u, "鹿児島県"},

    {791u, "九州地方東部"},

    {792u, "九州地方西部"},

    {793u, "薩南諸島"},

    {800u, "沖縄本島地方"},

    {801u, "大東島地方"},

    {802u, "宮古島・八重山地方"},

    {891u, "沖縄県地方"},

    {1000u, "その他の津波予報区"},
};
inline const char* qzss_dcr_jma_tsunami_forecast_region_lookup(uint16_t id) {
    int lo = 0, hi = 99 - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_TABLE[mid].id == id) return QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_TABLE[mid].label;
        if (QZSS_DCR_JMA_TSUNAMI_FORECAST_REGION_TABLE[mid].id  < id) lo = mid + 1;
        else hi = mid - 1;
    }
    return nullptr;
}

} // namespace def
} // namespace azaraC
