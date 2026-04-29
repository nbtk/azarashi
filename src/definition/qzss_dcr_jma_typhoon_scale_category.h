#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_typhoon_scale_category
// Variable      : qzss_dcr_jma_typhoon_scale_category
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_typhoon_scale_category_lookup(uint8_t id) {
    switch (id) {
        case 0: return "なし";
        case 1: return "大型";
        case 2: return "超大型";
        case 15: return "その他の大きさ階級分類";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
