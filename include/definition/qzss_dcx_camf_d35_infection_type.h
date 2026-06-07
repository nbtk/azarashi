#pragma once
// AUTO-GENERATED from azarashi 0.15.1 with CI-CD
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d35_infection_type
// Entries       : 63
// Strategy      : array

#include <cstdint>
#include <optional>
#include <string_view>

namespace azaraC {
namespace def {

inline constexpr std::optional<std::string_view> QZSS_DCX_CAMF_D35_INFECTION_TYPE_TABLE[] = {
    "Anthrax",
    "Avian influenza in humans",
    "Botulism",
    "Brucellosis",
    "Campylobacteriosis",
    "Chikungunya virus disease",
    "Chlamydia infections",
    "Cholera",
    "COVID - 19",
    "Creutzfeldt - Jakob Disease - variant(vCJD)",
    "Cryptosporidiosis",
    "Dengue",
    "Diphtheria",
    "Echinococcosis",
    "Giardiasis",
    "Gonorrhoea",
    "Hepatitis A",
    "Hepatitis B",
    "Hepatitis C",
    "HIV infection and AIDS",
    "Infections with haemophilus influenza group B",
    "Influenza including Influenza A(H1N1)",
    "Invasive meningococcal disease",
    "Invasive pneumococcal disease",
    "Legionnaires' disease",
    "Leptospirosis",
    "Listeriosis",
    "Lyme neuroborreliosis",
    "Malaria",
    "Measles",
    "Meningococcal disease, invasive",
    "Mumps",
    "Pertussis",
    "Plague",
    "Pneumococcal invasive diseases",
    "Poliomyelitis",
    "Q fever",
    "Rabies",
    "Rubella",
    "Rubella, congenital",
    "Salmonellosis",
    "Severe Acute Respiratory Syndrome (SARS)",
    "Shiga toxin /verocytotoxin -producing Escherichia coli (STEC/VTEC)",
    "Shigellosis",
    "Smallpox",
    "Syphilis",
    "Syphilis, congenital",
    "Tetanus",
    "Tick-borne encephalitis",
    "Toxoplasmosis, congenital",
    "Trichinellosis",
    "Tuberculosis",
    "Tularaemia",
    "Typhoid and paratyphoid fevers",
    "Viral haemorrhagic fevers",
    "West Nile virus infection",
    "Yellow fever",
    "Yersinosis",
    "Zika virus disease",
    "Zika virus disease, congenital",
    "Nosocomial infections",
    "Antimicrobial resistance",
    "unidentified infection"
};
inline constexpr uint8_t QZSS_DCX_CAMF_D35_INFECTION_TYPE_BASE = 0;
inline constexpr uint8_t QZSS_DCX_CAMF_D35_INFECTION_TYPE_SIZE = 63;
[[nodiscard]] inline constexpr std::optional<std::string_view> qzss_dcx_camf_d35_infection_type_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D35_INFECTION_TYPE_BASE || id >= QZSS_DCX_CAMF_D35_INFECTION_TYPE_BASE + QZSS_DCX_CAMF_D35_INFECTION_TYPE_SIZE) return std::nullopt;
    return QZSS_DCX_CAMF_D35_INFECTION_TYPE_TABLE[id - QZSS_DCX_CAMF_D35_INFECTION_TYPE_BASE];
}

} // namespace def
} // namespace azaraC
