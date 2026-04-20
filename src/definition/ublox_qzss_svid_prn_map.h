#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : ublox_qzss_svid_prn_map
// Variable      : ublox_qzss_svid_prn_map
// Entries       : 4
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline const char* ublox_qzss_svid_prn_map_lookup(uint8_t id) {
    switch (id) {
        case 2: return "184";
        case 3: return "185";
        case 4: return "186";
        case 7: return "189";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC
