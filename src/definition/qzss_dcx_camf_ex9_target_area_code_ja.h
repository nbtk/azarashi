#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_ex9_target_area_code
// Variable      : qzss_dcx_camf_ex9_target_area_code_ja
// Entries       : 47
// Strategy      : binary_search

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_Entry { uint64_t id; std::string_view label; };
inline constexpr QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_Entry QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_TABLE[] = {
    {1u, "北海道"},

    {2u, "青森県"},

    {4u, "岩手県"},

    {8u, "宮城県"},

    {16u, "秋田県"},

    {32u, "山形県"},

    {64u, "福島県"},

    {128u, "茨城県"},

    {256u, "栃木県"},

    {512u, "群馬県"},

    {1024u, "埼玉県"},

    {2048u, "千葉県"},

    {4096u, "東京都"},

    {8192u, "神奈川県"},

    {16384u, "新潟県"},

    {32768u, "富山県"},

    {65536u, "石川県"},

    {131072u, "福井県"},

    {262144u, "山梨県"},

    {524288u, "長野県"},

    {1048576u, "岐阜県"},

    {2097152u, "静岡県"},

    {4194304u, "愛知県"},

    {8388608u, "三重県"},

    {16777216u, "滋賀県"},

    {33554432u, "京都府"},

    {67108864u, "大阪府"},

    {134217728u, "兵庫県"},

    {268435456u, "奈良県"},

    {536870912u, "和歌山県"},

    {1073741824u, "鳥取県"},

    {2147483648u, "島根県"},

    {4294967296u, "岡山県"},

    {8589934592u, "広島県"},

    {17179869184u, "山口県"},

    {34359738368u, "徳島県"},

    {68719476736u, "香川県"},

    {137438953472u, "愛媛県"},

    {274877906944u, "高知県"},

    {549755813888u, "福岡県"},

    {1099511627776u, "佐賀県"},

    {2199023255552u, "長崎県"},

    {4398046511104u, "熊本県"},

    {8796093022208u, "大分県"},

    {17592186044416u, "宮崎県"},

    {35184372088832u, "鹿児島県"},

    {70368744177664u, "沖縄県"},
};
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_ex9_target_area_code_ja_lookup(uint64_t id) {
    uint8_t lo = 0, hi = 47;
    while (lo < hi) {
        uint8_t mid = static_cast<uint8_t>(lo + (hi - lo) / 2);
        if (QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_TABLE[mid].id == id) return QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_TABLE[mid].label;
        if (QZSS_DCX_CAMF_EX9_TARGET_AREA_CODE_JA_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return std::nullopt;
}

} // namespace def
} // namespace azaraC
