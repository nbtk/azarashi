#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcr_jma_information_type
// Variable      : qzss_dcr_jma_information_type
// Entries       : 3
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_information_type_lookup(uint8_t id) {
    switch (id) {
        case 0: return "発表";
        case 1: return "訂正";
        case 2: return "取消";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
