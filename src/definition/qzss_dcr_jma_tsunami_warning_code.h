#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcr_jma_tsunami_warning_code
// Variable      : qzss_dcr_jma_tsunami_warning_code
// Entries       : 6
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_tsunami_warning_code_lookup(uint8_t id) {
    switch (id) {
        case 1: return "津波なし";
        case 2: return "警報解除";
        case 3: return "津波警報";
        case 4: return "大津波警報";
        case 5: return "大津波警報：発表";
        case 15: return "その他の警報";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
