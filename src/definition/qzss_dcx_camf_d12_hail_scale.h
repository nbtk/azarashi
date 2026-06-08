#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d12_hail_scale
// Entries       : 11
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCX_CAMF_D12_HAIL_SCALE_TABLE[] = {
    "H0 Hard hail. Typical hail diameter of 5 mm, No damage",
    "H1 Potentially damaging. Typical hail diameter of 5-15 mm. Slight general damage to plants, crops",
    "H2 Significant. Typical hail diameter of 10-20 mm. Slight general damage to fruit, crops, vegetation",
    "H3 Severe. Typical hail diameter of 20-30 mm (size of a walnut). Severe damage to fruit and crops, damage to glass and plastic structures, paint and wood scored",
    "H4 Severe. Typical hail diameter of 25-40 mm (size of a squash ball). Widespread glass damage, vehicle bodywork damage",
    "H5 Destructive. Typical hail diameter of 30-50 mm (size of a golf ball). Wholesale destruction of glass, damage to tiled roofs, significant risk of injuries",
    "H6 Destructive. Typical hail diameter of 40-60 mm. Bodywork of grounded aircraft dented, brick walls pitted",
    "H7 Destructive. Typical hail diameter of 50-75 mm (size of a tennis ball). Severe roof damage, risk of serious injuries",
    "H8 Destructive. Typical hail diameter of 60-90 mm (size of a large orange). Severe damage to aircraft bodywork",
    "H9 Super Hailstorms. Typical hail diameter of 75-100 mm (size of a grapefruit). Extensive structural damage. Risk of severe or even fatal injuries to persons caught in the open",
    "H10 Super Hailstorms. Typical hail diameter > 100 mm (size of a melon). Extensive structural damage. Risk of severe or even fatal injuries to persons caught in the open"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D12_HAIL_SCALE_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D12_HAIL_SCALE_SIZE = 11;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d12_hail_scale_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D12_HAIL_SCALE_BASE || id >= QZSS_DCX_CAMF_D12_HAIL_SCALE_BASE + QZSS_DCX_CAMF_D12_HAIL_SCALE_SIZE) return std::nullopt;
    return QZSS_DCX_CAMF_D12_HAIL_SCALE_TABLE[id - QZSS_DCX_CAMF_D12_HAIL_SCALE_BASE];
}

} // namespace def
} // namespace azaraC
