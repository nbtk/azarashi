#pragma once
// AUTO-GENERATED from azarashi: qzss_dcx_camf_a3_provider_identifier
#include <cstdint>
#include <optional>
#include <string_view>
namespace azaraC { namespace def {

struct A3Entry { uint16_t key; std::string_view label; };
static constexpr A3Entry QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER[] = {
  {161, "National Emergency Management Agency"},
  {162, "Bureau of Meteorology"},
  {163, "Australian Climate Service"},
  {164, "Geoscience Australia"},
  {165, "Commonwealth Scientific and Industrial Research Organisation"},
  {166, "Australian Bureau of Statistics"},
  {167, "Resilience New South Wales"},
  {168, "State Emergency Service New South Wales"},
  {169, "New South Wales Rural Fire Service"},
  {170, "Joint Australian Tsunami Warning Centre"},
  {171, "Flood Knowledge Centre"},
  {172, "Australian Broadcasting Corporation"},
  {1137, "National Disaster Management Office"},
  {1138, "Fiji Meteorological Service"},
  {1139, "Hydrology Section, Fiji Water Authority"},
  {1140, "Mineral Resources Department"},
  {1141, "Fiji Broadcasting Corporation"},
  {1777, "Foundation for MultiMedia Communications"},
  {1778, "Fire and Disaster Management Agency"},
  {1779, "Related Ministries"},
  {1780, "Local Government"},
  {3505, "Department of Disaster Prevention and Mitigation"},
  {3506, "Thai Meteorological Department"},
  {3507, "National Disaster Warning Center"},
  {3508, "Department of Mineral Resources"},
  {3509, "Navy Hydrographic Department, Royal Thai Navy"},
  {3510, "Department of Water Resources"},
  {3511, "Royal Irrigation Department"},
  {3512, "Department of Pollution Control"},
  {3513, "Geo-Informatics and Space Technology Development Agency"},
  {3514, "Electricity Generating Authority of Thailand"},
  {3515, "Royal Forest Department"},
  {3516, "Department of Parks, Wildlife and Plant Conservation"},
  {3517, "Water Crisis Prevention Center"},
};

[[nodiscard]] inline std::optional<std::string_view> qzss_dcx_camf_a3_provider_identifier_lookup(uint16_t country, uint8_t provider) {
  uint16_t key = (uint16_t)((country << 4) | (provider & 0xF));
  for (const auto& e : QZSS_DCX_CAMF_A3_PROVIDER_IDENTIFIER) {
    if (e.key == key) return e.label;
  }
  return std::nullopt;
}

}} // namespace