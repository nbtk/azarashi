#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_c10_guidance_library_for_second_ellipse
// Variable      : qzss_dcx_camf_c10_guidance_library_for_second_ellipse_code
// Entries       : 19
// Strategy      : binary_search

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_Entry { uint8_t id; std::string_view label; };
inline constexpr QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_Entry QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_TABLE[] = {
    {0u, "IC-C-01"},

    {1u, "IC-C-02"},

    {2u, "IC-C-03"},

    {3u, "IC-C-04"},

    {4u, "IC-C-05"},

    {5u, "IC-C-06"},

    {6u, "IC-C-07"},

    {7u, "IC-C-08"},

    {8u, "IC-C-09"},

    {9u, "IC-C-10"},

    {10u, "IC-C-11"},

    {11u, "IC-C-12"},

    {12u, "IC-C-13"},

    {13u, "IC-C-14"},

    {14u, "IC-C-15"},

    {15u, "IC-C-16"},

    {16u, "IC-C-17"},

    {30u, "IC-C-31"},

    {31u, "IC-C-32"},
};
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_c10_guidance_library_for_second_ellipse_code_lookup(uint8_t id) {
    uint8_t lo = 0, hi = 19;
    while (lo < hi) {
        uint8_t mid = static_cast<uint8_t>(lo + (hi - lo) / 2);
        if (QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_TABLE[mid].id == id) return QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_TABLE[mid].label;
        if (QZSS_DCX_CAMF_C10_GUIDANCE_LIBRARY_FOR_SECOND_ELLIPSE_CODE_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return std::nullopt;
}

} // namespace def
} // namespace azaraC
