#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_report_classification
// Variable      : qzss_dcr_jma_report_classification_en
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_report_classification_en_lookup(uint8_t id) {
    switch (id) {
        case 1: return "Maximum Priority";
        case 2: return "Priority";
        case 3: return "Regular";
        case 7: return "Training/Test";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
