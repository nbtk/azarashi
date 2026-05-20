#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcr_jma_coastal_region
// Variable      : qzss_dcr_jma_coastal_region_en
// Entries       : 63
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCR_JMA_COASTAL_REGION_EN_TABLE[] = {
    "Ust-Kamchatsk (East Coasts of Kamchatka Peninsula)",
    "Petropavlovsk-K (East Coasts of Kamchatka Peninsula)",
    "Severo Kurilsk (Kuril Islands)",
    "Urup Islands (Kuril Islands)",
    "Busan (South Coasts of Korean Peninsula)",
    "Nohwa (South Coasts of Korean Peninsula)",
    "Seogwipo (South Coasts of Korean Peninsula)",
    "Hualien (Taiwan)",
    "Basco (East Coasts of Philippines)",
    "Palanan (East Coasts of Philippines)",
    "Legaspi (East Coasts of Philippines)",
    "Laoang (East Coasts of Philippines)",
    "Madrid (East Coasts of Philippines)",
    "Davao (East Coasts of Philippines)",
    "Berebere (North Coasts of Irian Jaya)",
    "Patani (North Coasts of Irian Jaya)",
    "Sorong (North Coasts of Irian Jaya)",
    "Manokwari (North Coasts of Irian Jaya)",
    "Warsa (North Coasts of Irian Jaya)",
    "Jayapura (North Coasts of Irian Jaya)",
    "Vanimo (North Coasts of Papua New Guinea)",
    "Wewak (North Coasts of Papua New Guinea)",
    "Madang (North Coasts of Papua New Guinea)",
    "Manus Islands (North Coasts of Papua New Guinea)",
    "Rabaul (North Coasts of Papua New Guinea)",
    "Kavieng (North Coasts of Papua New Guinea)",
    "Kimbe (North Coasts of Papua New Guinea)",
    "Kieta (North Coasts of Papua New Guinea)",
    "Guam (Mariana Islands)",
    "Saipan (Mariana Islands)",
    "Malakal (Palau)",
    "Yap Island (Micronesia)",
    "Chuuk Island (Micronesia)",
    "Pohnpei Island (Micronesia)",
    "Kosrae Island (Micronesia)",
    "Eniwetok Island (Marshall Islands)",
    "Panggoe (North Coasts of Solomon Islands)",
    "Auki (North Coasts of Solomon Islands)",
    "Kirakira (North Coasts of Solomon Islands)",
    "Munda (Solomon Sea)",
    "Honiara (Solomon Sea)",
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    "Ostrov-Karaginskiy (East Coasts of Kamchatka Peninsula)",
    "Nikolskoya (East Coasts of Kamchatka Peninsula)",
    "Tongyeong (South Coasts of Korean Peninsula)",
    "Heuksando (South Coasts of Korean Peninsula)",
    "Cheju-Island (South Coasts of Korean Peninsula)",
    "Chilung (Taiwan)",
    "Taitung (Taiwan)",
    std::nullopt,
    "Homel (Taiwan)",
    "Geme (North Coasts of Irian Jaya)",
    "Ulamona (North Coasts of Papua New Guinea)",
    "Ghatere (North Coasts of Solomon Islands)",
    "Amun (Solomon Sea)",
    "Falamae (Solomon Sea)",
    "Misima (Solomon Sea)",
    "Alotau (Solomon Sea)",
    "Lae (Solomon Sea)",
    "Port-Moresby (Coral Sea)",
    "Shanghai (Coasts of East China Sea)",
    "Zhoushan (Coasts of East China Sea)",
    "Wenzhou (Coasts of East China Sea)",
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::nullopt,
    "Unknown",
    "Other region"
};
inline constexpr uint8_t QZSS_DCR_JMA_COASTAL_REGION_EN_BASE = 1;
inline constexpr uint8_t QZSS_DCR_JMA_COASTAL_REGION_EN_SIZE = 100;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcr_jma_coastal_region_en_lookup(uint8_t id) {
    if (id < QZSS_DCR_JMA_COASTAL_REGION_EN_BASE || id >= QZSS_DCR_JMA_COASTAL_REGION_EN_BASE + QZSS_DCR_JMA_COASTAL_REGION_EN_SIZE) return std::nullopt;
    return QZSS_DCR_JMA_COASTAL_REGION_EN_TABLE[id - QZSS_DCR_JMA_COASTAL_REGION_EN_BASE];
}

} // namespace def
} // namespace azaraC
