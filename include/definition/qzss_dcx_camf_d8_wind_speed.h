#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d8_wind_speed
// Entries       : 13
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCX_CAMF_D8_WIND_SPEED_TABLE[] = {
    "Beaufort 0 - 0km/h < v < 1km/h - Calm",
    "Beaufort 1 - 1km/h < v < 5km/h - Light Air",
    "Beaufort 2 - 6km/h < v < 11km/h - Light Breeze",
    "Beaufort 3 - 12km/h < v < 19km/h - Gentle Breeze",
    "Beaufort 4 - 20km/h < v < 30km/h - Moderate Breeze",
    "Beaufort 5 - 31km/h < v < 39km/h - Fresh Breeze",
    "Beaufort 6 - 40km/h < v < 50km/h - Strong Breeze",
    "Beaufort 7 - 51km/h < v < 61km/h - Near Gale",
    "Beaufort 8 - 62km/h < v < 74km/h - Gale",
    "Beaufort 9 - 75km/h < v < 88km/h - Strong Gale",
    "Beaufort 10 - 89km/h < v < 102km/h - Storm",
    "Beaufort 11 - 103km/h < v < 117km/h - Violent Storm",
    "Beaufort 12 - v > 118km/h - Hurricane"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D8_WIND_SPEED_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D8_WIND_SPEED_SIZE = 13;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d8_wind_speed_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D8_WIND_SPEED_BASE || id >= QZSS_DCX_CAMF_D8_WIND_SPEED_BASE + QZSS_DCX_CAMF_D8_WIND_SPEED_SIZE) return std::nullopt;
    return QZSS_DCX_CAMF_D8_WIND_SPEED_TABLE[id - QZSS_DCX_CAMF_D8_WIND_SPEED_BASE];
}

} // namespace def
} // namespace azaraC
