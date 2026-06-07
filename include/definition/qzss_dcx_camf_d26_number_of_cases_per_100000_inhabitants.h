#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d26_number_of_cases_per_100000_inhabitants
// Entries       : 21
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_TABLE[] = {
    "0 - 9",
    "10 - 20",
    "21 - 50",
    "51 - 70",
    "71 - 100",
    "101- 125",
    "126 - 150",
    "151 - 175",
    "176 - 200",
    "201 - 250",
    "251 - 300",
    "301 - 350",
    "351 - 400",
    "401 - 450",
    "451 - 500",
    "501 - 750",
    "751 - 1000",
    "> 1000",
    "> 2000",
    "> 3000",
    "> 5000"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_SIZE = 21;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d26_number_of_cases_per_100000_inhabitants_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_BASE || id >= QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_BASE + QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_SIZE) return std::nullopt;
    return QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_TABLE[id - QZSS_DCX_CAMF_D26_NUMBER_OF_CASES_PER_100000_INHABITANTS_BASE];
}

} // namespace def
} // namespace azaraC
