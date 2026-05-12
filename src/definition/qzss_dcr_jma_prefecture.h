#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcr_jma_prefecture
// Variable      : qzss_dcr_jma_prefecture
// Entries       : 47
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* QZSS_DCR_JMA_PREFECTURE_TABLE[] = {
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県"
};
inline constexpr uint8_t QZSS_DCR_JMA_PREFECTURE_BASE = 1;
inline constexpr uint8_t QZSS_DCR_JMA_PREFECTURE_SIZE = 47;
inline constexpr const char* qzss_dcr_jma_prefecture_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_PREFECTURE_BASE || id >= QZSS_DCR_JMA_PREFECTURE_BASE + QZSS_DCR_JMA_PREFECTURE_SIZE) return nullptr;
    return QZSS_DCR_JMA_PREFECTURE_TABLE[id - QZSS_DCR_JMA_PREFECTURE_BASE];
}

} // namespace def
} // namespace azaraC
