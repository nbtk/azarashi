#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d4_vector_length_between_centre_of_main_ellipse_and_epicentre
// Entries       : 16
// Strategy      : array

#include <cstdint>

namespace azaraC {
namespace def {

static constexpr const char* QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_TABLE[] = {
    "0.25",
    "0.5",
    "0.75",
    "1",
    "2",
    "3",
    "5",
    "10",
    "20",
    "30",
    "40",
    "50",
    "70",
    "100",
    "150",
    "200"
};
static constexpr uint8_t QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_BASE = 0;
static constexpr uint8_t QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_SIZE = 16;
inline const char* qzss_dcx_camf_d4_vector_length_between_centre_of_main_ellipse_and_epicentre_lookup(uint8_t id) {
    if (id < QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_BASE || id >= QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_BASE + QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_SIZE) return nullptr;
    return QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_TABLE[id - QZSS_DCX_CAMF_D4_VECTOR_LENGTH_BETWEEN_CENTRE_OF_MAIN_ELLIPSE_AND_EPICENTRE_BASE];
}

} // namespace def
} // namespace azaraC
