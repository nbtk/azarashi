#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_a11_japanese_library
// Variable      : qzss_dcx_camf_a11_japanese_library_ja
// Entries       : 38
// Strategy      : binary_search

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

struct QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_Entry { uint16_t id; std::string_view label; };
inline constexpr QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_Entry QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_TABLE[] = {
    {0u, ""},

    {1u, "直ちに命を守るための最善の行動を。"},

    {126u, "これは、DCX のテストです。"},

    {127u, "直ちに命を守るための最善の行動を。"},

    {128u, "ミサイル発射。ミサイル発射。ミサイルが発射されたものとみられます。建物の中、又は地下に避難して下さい。"},

    {129u, "ミサイル通過。ミサイル通過。先程のミサイルは通過したものとみられます。避難の呼びかけを解除します。不審なものには決して近寄らず直ちに警察や消防などに連絡して下さい。"},

    {130u, "先程のミサイルは、海に落下したものとみられます。避難の呼びかけを解除します。不審なものには決して近寄らず直ちに警察や消防などに連絡して下さい。"},

    {131u, "先程のミサイルは、我が国には飛来しないものとみられます。避難の呼びかけを解除します。"},

    {132u, "直ちに避難。直ちに避難。直ちに建物の中、又は地下に避難して下さい。ミサイルが、周辺に落下するものとみられます。直ちに避難して下さい。"},

    {133u, "先程のミサイルは、迎撃により破壊されました。ミサイルの破片の落下の可能性があります。続報を伝達しますので、引き続き屋内に避難して下さい。"},

    {134u, "ミサイル落下。ミサイル落下。ミサイルが、周辺に落下したものとみられます。続報を伝達しますので、引き続き屋内に避難して下さい。"},

    {135u, "先程のミサイルは、我が国には落下しないものとみられます。避難の呼びかけを解除します。"},

    {136u, "これは、Jアラートのテストです。"},

    {255u, "直ちに命を守るための最善の行動を。"},

    {256u, "留まれ。"},

    {257u, "留まれ。頑丈なものの下/中。"},

    {258u, "留まれ。3階以上。"},

    {259u, "留まれ。地下。"},

    {260u, "留まれ。山。"},

    {261u, "留まれ。水場。"},

    {262u, "留まれ。工場等化学系を取扱う建物。"},

    {263u, "留まれ。崖等崩れやすい場所。"},

    {512u, "向かえ。"},

    {513u, "向かえ。頑丈なものの下/中。"},

    {514u, "向かえ。3階以上。"},

    {515u, "向かえ。地下。"},

    {516u, "向かえ。山。"},

    {517u, "向かえ。水場。"},

    {518u, "向かえ。工場等化学系を取扱う建物。"},

    {519u, "向かえ。崖等崩れやすい場所。"},

    {768u, "離れろ。"},

    {769u, "離れろ。頑丈なものの下/中。"},

    {770u, "離れろ。3階以上。"},

    {771u, "離れろ。地下。"},

    {772u, "離れろ。山。"},

    {773u, "離れろ。水場。"},

    {774u, "離れろ。工場等化学系を取扱う建物。"},

    {775u, "離れろ。崖等崩れやすい場所。"},
};
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_a11_japanese_library_ja_lookup(uint16_t id) {
    uint8_t lo = 0, hi = 38;
    while (lo < hi) {
        uint8_t mid = static_cast<uint8_t>(lo + (hi - lo) / 2);
        if (QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_TABLE[mid].id == id) return QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_TABLE[mid].label;
        if (QZSS_DCX_CAMF_A11_JAPANESE_LIBRARY_JA_TABLE[mid].id < id) lo = mid + 1;
        else hi = mid;
    }
    return std::nullopt;
}

} // namespace def
} // namespace azaraC
