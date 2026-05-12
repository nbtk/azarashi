#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Requires C++17 or later
// Source module : qzss_dcx_camf_a9_selection_of_library
// Variable      : qzss_dcx_camf_a9_selection_of_library
// Entries       : 2
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_a9_selection_of_library_lookup(uint8_t id) {
    switch (id) {
        case 0: return "International library";
        case 1: return "Country/region guidance library";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
