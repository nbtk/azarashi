#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a3_provider_identifier
// Variable      : qzss_dcx_camf_a3_provider_identifier_map
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a3_provider_identifier_map_lookup(uint8_t id) {
    switch (id) {
        case 10: return "{1: 'National Emergency Management Agency', 2: 'Bureau of Meteorology', 3: 'Australian Climate Service', 4: 'Geoscience Australia', 5: 'Commonwealth Scientific and Industrial Research Organisation', 6: 'Australian Bureau of Statistics', 7: 'Resilience New South Wales', 8: 'State Emergency Service New South Wales', 9: 'New South Wales Rural Fire Service', 10: 'Joint Australian Tsunami Warning Centre', 11: 'Flood Knowledge Centre', 12: 'Australian Broadcasting Corporation'}";
        case 71: return "{1: 'National Disaster Management Office', 2: 'Fiji Meteorological Service', 3: 'Hydrology Section, Fiji Water Authority', 4: 'Mineral Resources Department', 5: 'Fiji Broadcasting Corporation'}";
        case 111: return "{1: 'Foundation for MultiMedia Communications', 2: 'Fire and Disaster Management Agency', 3: 'Related Ministries', 4: 'Local Government'}";
        case 219: return "{1: 'Department of Disaster Prevention and Mitigation', 2: 'Thai Meteorological Department', 3: 'National Disaster Warning Center', 4: 'Department of Mineral Resources', 5: 'Navy Hydrographic Department, Royal Thai Navy', 6: 'Department of Water Resources', 7: 'Royal Irrigation Department', 8: 'Department of Pollution Control', 9: 'Geo-Informatics and Space Technology Development Agency', 10: 'Electricity Generating Authority of Thailand', 11: 'Royal Forest Department', 12: 'Department of Parks, Wildlife and Plant Conservation', 13: 'Water Crisis Prevention Center'}";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
