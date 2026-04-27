#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_eew_forecast_region
// Variable      : qzss_dcr_jma_eew_forecast_region
// Entries       : 71
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCR_JMA_EEW_FORECAST_REGION_TABLE[] = {
    "北海道道央",
    "北海道道南",
    "北海道道北",
    "北海道道東",
    "青森",
    "岩手",
    "宮城",
    "秋田",
    "山形",
    "福島",
    "茨城",
    "栃木",
    "群馬",
    "埼玉",
    "千葉",
    "東京",
    "伊豆諸島",
    "小笠原",
    "神奈川",
    "新潟",
    "富山",
    "石川",
    "福井",
    "山梨",
    "長野",
    "岐阜",
    "静岡",
    "愛知",
    "三重",
    "滋賀",
    "京都",
    "大阪",
    "兵庫",
    "奈良",
    "和歌山",
    "鳥取",
    "島根",
    "岡山",
    "広島",
    "山口",
    "徳島",
    "香川",
    "愛媛",
    "高知",
    "福岡",
    "佐賀",
    "長崎",
    "熊本",
    "大分",
    "宮崎",
    "鹿児島",
    "奄美(群島)",
    "沖縄本島",
    "大東島",
    "宮古島",
    "八重山",
    "北海道",
    "東北",
    "関東",
    "伊豆諸島",
    "小笠原",
    "北陸",
    "甲信",
    "東海",
    "近畿",
    "中国",
    "四国",
    "九州",
    "奄美(群島)",
    "沖縄",
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    "その他の府県予報区および地方予報区"
};
static constexpr uint8_t QZSS_DCR_JMA_EEW_FORECAST_REGION_BASE = 1;
static constexpr uint8_t QZSS_DCR_JMA_EEW_FORECAST_REGION_SIZE = 80;
inline const char* qzss_dcr_jma_eew_forecast_region_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_EEW_FORECAST_REGION_BASE || id >= QZSS_DCR_JMA_EEW_FORECAST_REGION_BASE + QZSS_DCR_JMA_EEW_FORECAST_REGION_SIZE) return nullptr;
    return QZSS_DCR_JMA_EEW_FORECAST_REGION_TABLE[id - QZSS_DCR_JMA_EEW_FORECAST_REGION_BASE];
}

} // namespace def
} // namespace azaraC
