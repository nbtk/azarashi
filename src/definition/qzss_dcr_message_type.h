#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_message_type
// Variable      : qzss_dcr_message_type
// Entries       : 2
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_message_type_lookup(uint8_t id) {
    switch (id) {
        case 43: return "DCR";
        case 44: return "DCX";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
