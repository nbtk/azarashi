#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_ex9_target_area_code
// Variable      : qzss_dcx_camf_ex9_target_area_code_en
// Entries       : 47
// Strategy      : binary_search

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_Entry { uint64_t id; std::string_view label; };
inline constexpr QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_Entry QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_TABLE[] = {
    {1u, "Hokkaido"},

    {2u, "Aomori"},

    {4u, "Iwate"},

    {8u, "Miyagi"},

    {16u, "Akita"},

    {32u, "Yamagata"},

    {64u, "Fukushima"},

    {128u, "Ibaraki"},

    {256u, "Tochigi"},

    {512u, "Gunma"},

    {1024u, "Saitama"},

    {2048u, "Chiba"},

    {4096u, "Tokyo"},

    {8192u, "Kanagawa"},

    {16384u, "Niigata"},

    {32768u, "Toyama"},

    {65536u, "Ishikawa"},

    {131072u, "Fukui"},

    {262144u, "Yamanashi"},

    {524288u, "Nagano"},

    {1048576u, "Gifu"},

    {2097152u, "Shizuoka"},

    {4194304u, "Aichi"},

    {8388608u, "Mie"},

    {16777216u, "Shiga"},

    {33554432u, "Kyoto"},

    {67108864u, "Osaka"},

    {134217728u, "Hyogo"},

    {268435456u, "Nara"},

    {536870912u, "Wakayama"},

    {1073741824u, "Tottori"},

    {2147483648u, "Shimane"},

    {4294967296u, "Okayama"},

    {8589934592u, "Hiroshima"},

    {17179869184u, "Yamaguchi"},

    {34359738368u, "Tokushima"},

    {68719476736u, "Kagawa"},

    {137438953472u, "Ehime"},

    {274877906944u, "Kochi"},

    {549755813888u, "Fukuoka"},

    {1099511627776u, "Saga"},

    {2199023255552u, "Nagasaki"},

    {4398046511104u, "Kumamoto"},

    {8796093022208u, "Oita"},

    {17592186044416u, "Miyazaki"},

    {35184372088832u, "Kagoshima"},

    {70368744177664u, "Okinawa"},
};
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_ex9_target_area_code_en_lookup(uint64_t id) {
#if AZARAC_LANG_EN
    uint8_t lo = 0, hi = 47;
    while (lo < hi) {
        uint8_t mid = static_cast<uint8_t>(lo + (hi - lo) / 2);
        if (QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_TABLE[mid].id == id) return QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_TABLE[mid].label;
        if (QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_EN_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return std::nullopt;
#else
    (void)id;
    return std::nullopt;
#endif
}

} // namespace def
} // namespace azaraC
