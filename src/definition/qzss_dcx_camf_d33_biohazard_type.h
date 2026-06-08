#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d33_biohazard_type
// Entries       : 4
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d33_biohazard_type_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Biological agents. These include bacteria, viruses, parasites, and fungi (such as yeasts and molds).";
        case 1: return "Biotoxins. These refer to a group of substances with a biological origin that are toxic and poisonous to humans. Often, biotoxins are produced by plants, bacteria, insects, or certain animals, among others. Continuous exposure to these may cause, at the very least, a series of inflammatory reactions throughout the body.";
        case 2: return "Blood and blood products. While blood isn't considered a biological hazard, it can still bring potential risks if it's contaminated or its source is in any way infected. Also, blood products such as red blood cells, white blood cells, plasma, tissues, and platelets are also hazardous if not properly handled.";
        case 3: return "Environmental specimens. Generally, these refer to plants, soil, or water that potentially contain biological agents(include bacteria, viruses, parasites, and fungi) and biotoxins.";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
