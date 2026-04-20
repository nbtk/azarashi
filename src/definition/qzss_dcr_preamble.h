#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_preamble
// Variable      : qzss_dcr_preamble
// Entries       : 3
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcr_preamble_lookup(uint8_t id) {
    switch (id) {
        case 83: return "A";
        case 154: return "B";
        case 198: return "C";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
