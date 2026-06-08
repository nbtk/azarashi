#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_information_type
// Variable      : qzss_dcr_jma_information_type
// Entries       : 3
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_information_type_lookup(uint8_t id) {
    switch (id) {
        case 0: return "発表";
        case 1: return "訂正";
        case 2: return "取消";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
