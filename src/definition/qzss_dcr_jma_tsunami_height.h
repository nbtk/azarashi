#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_tsunami_height
// Variable      : qzss_dcr_jma_tsunami_height
// Entries       : 8
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcr_jma_tsunami_height_lookup(uint8_t id) {
    switch (id) {
        case 1: return "0.2m未満";
        case 2: return "1m";
        case 3: return "3m";
        case 4: return "5m";
        case 5: return "10m";
        case 6: return "10m超";
        case 14: return "不明";
        case 15: return "その他の津波の高さ";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
