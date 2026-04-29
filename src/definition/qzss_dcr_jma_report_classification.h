#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_jma_report_classification
// Variable      : qzss_dcr_jma_report_classification
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_jma_report_classification_lookup(uint8_t id) {
    switch (id) {
        case 1: return "最優先";
        case 2: return "優先";
        case 3: return "通常";
        case 7: return "訓練/試験";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
