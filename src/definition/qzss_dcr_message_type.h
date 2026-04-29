#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcr_message_type
// Variable      : qzss_dcr_message_type
// Entries       : 2
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcr_message_type_lookup(uint8_t id) {
    switch (id) {
        case 43: return "DCR";
        case 44: return "DCX";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
