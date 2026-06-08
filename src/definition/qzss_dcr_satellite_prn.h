#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_satellite_prn
// Variable      : qzss_dcr_satellite_prn
// Entries       : 5
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_satellite_prn_lookup(uint8_t id) {
    switch (id) {
        case 55: return "PRN183";
        case 56: return "PRN184";
        case 57: return "PRN185";
        case 58: return "PRN186";
        case 61: return "PRN189";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
