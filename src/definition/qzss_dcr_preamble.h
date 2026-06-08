#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_preamble
// Variable      : qzss_dcr_preamble
// Entries       : 3
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_preamble_lookup(uint8_t id) {
    switch (id) {
        case 83: return "A";
        case 154: return "B";
        case 198: return "C";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
