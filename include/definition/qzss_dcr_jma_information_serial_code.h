#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_information_serial_code
// Variable      : qzss_dcr_jma_information_serial_code
// Entries       : 7
// Strategy      : switch

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_information_serial_code_lookup(uint8_t id) {
    switch (id) {
        case 1: return "調査中A（監視領域内でマグニチュード6.8以上の地震が発生したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）";
        case 2: return "調査中B（1カ所以上のひずみ計での有意な変化と共に、他の複数の観測点でもそれに関係すると思われる変化が観測され、想定震源域内のプレート境界で通常と異なるゆっくりすべりが発生している可能性がある場合など、ひずみ計で南海トラフ地震との関連性の検討が必要と認められる変化を観測したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）";
        case 3: return "調査中C（その他、想定震源域内のプレート境界の固着状態の変化を示す可能性のある現象が観測される等、南海トラフ地震との関連性の検討が必要と認められる現象を観測したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）";
        case 4: return "巨大地震警戒";
        case 5: return "巨大地震注意";
        case 6: return "調査終了";
        case 15: return "その他の情報";
        default: return std::nullopt;
    }
}

} // namespace def
} // namespace azaraC
