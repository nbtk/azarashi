#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_information_type
// Variable      : qzss_dcr_jma_information_type_en
// Entries       : 3
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_information_type_en_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Issue";
        case 1: return "Correction";
        case 2: return "Cancellation";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
