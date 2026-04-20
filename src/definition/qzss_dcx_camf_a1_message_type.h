#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_a1_message_type
// Variable      : qzss_dcx_camf_a1_message_type
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* qzss_dcx_camf_a1_message_type_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Test";
        case 1: return "Alert";
        case 2: return "Update";
        case 3: return "All Clear";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
