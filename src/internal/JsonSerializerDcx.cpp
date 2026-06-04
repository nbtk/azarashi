// azaraC - src/internal/JsonSerializerDcx.cpp
// MT=44 DCX JSON serializer

#include "JsonWriter.h"
#include "DcxHelper.h"
#include "../definition/_index.h"
#include <optional>
#include <string_view>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// MT=44 DCX
// ---------------------------------------------------------------------------
void serializeDcx(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt44Data& d = m.mt44;
    wf_u(out, "dcx_type", (uint32_t)static_cast<uint8_t>(d.service_kind));

    std::string_view dcx_label = "UNKNOWN";
    switch (d.service_kind) {
        case Mt44ServiceKind::NullMessage:     dcx_label = "NULL"; break;
        case Mt44ServiceKind::LAlert:          dcx_label = "L_ALERT"; break;
        case Mt44ServiceKind::JAlert:          dcx_label = "J_ALERT"; break;
        case Mt44ServiceKind::LocalGovernment: dcx_label = "LOCAL_GOV"; break;
        case Mt44ServiceKind::OutsideJapan:    dcx_label = "OUTSIDE_JAPAN"; break;
        default: break;
    }
    wf_s(out, "dcx_type_label", dcx_label);

    wf_s(out, "a1_msg_type",
        qzss_dcx_camf_a1_message_type_lookup(d.camf.a1));
    wf_u(out, "a2_country", d.camf.a2);
    wf_s(out, "a2_country_label",
        qzss_dcx_camf_a2_country_region_name_lookup(d.camf.a2));
    wf_u(out, "a3_provider", d.camf.a3);
    wf_s(out, "a3_provider_label",
        qzss_dcx_camf_a3_provider_identifier_lookup(d.camf.a2, d.camf.a3));
    wf_u(out, "a4_hazard", d.camf.a4);
    wf_s(out, "a4_hazard_category",
        qzss_dcx_camf_a4_hazard_category_lookup(d.camf.a4));
    wf_s(out, "a4_hazard_type",
        qzss_dcx_camf_a4_hazard_type_lookup(d.camf.a4));
    wf_u(out, "a5_severity", d.camf.a5);
    wf_s(out, "a5_severity_label",
        qzss_dcx_camf_a5_severity_lookup(d.camf.a5));
    wf_u(out, "a6_onset_week", d.camf.a6);
    wf_u(out, "a7_onset_minute", d.camf.a7);
    wf_u(out, "a8_duration", d.camf.a8);
    wf_s(out, "a8_duration_label",
        qzss_dcx_camf_a8_hazard_duration_lookup(d.camf.a8));
    writeDHM(out, "onset_time", d.onset_time);

    // A11 Guidance to react library
    wf_u(out, "a11_guidance", d.camf.a11);
    wf_s(out, "a11_guidance_label",
        qzss_dcx_camf_a11_japanese_library_ja_lookup(d.camf.a11));

    // A17/A18 Specific Settings
    wf_u(out, "a17_specific_subject", d.camf.a17);
    wf_s(out, "a17_specific_subject_label",
        qzss_dcx_camf_a17_main_subject_for_specific_settings_lookup(d.camf.a17));
    wf_u(out, "a18_specific_settings", d.camf.a18);

    // Decoded main ellipse (A12-A16)
    const Mt44Decoded& dec = d.mt44_decoded;
    if (dec.main_ellipse_present) {
        wk(out, "main_ellipse");
        out.print('{');
        wf_d(out, "lat_deg", dec.main_ellipse.lat_deg);
        wf_d(out, "lon_deg", dec.main_ellipse.lon_deg);
        wf_d(out, "semi_major_km", dec.main_ellipse.semi_major_km);
        wf_d(out, "semi_minor_km", dec.main_ellipse.semi_minor_km);
        wf_d(out, "azimuth_deg", dec.main_ellipse.azimuth_deg, /*last=*/!d.camf.b1_present);

        // B1 refinement (EWSS CAMF v1.1 §3.7.1)
        if (d.camf.b1_present) {
            wk(out, "b1_refinement");
            out.print('{');
            wf_d(out, "c1_lat_offset_deg", dec.main_ellipse.b1_lat_offset_deg);
            wf_d(out, "c2_lon_offset_deg", dec.main_ellipse.b1_lon_offset_deg);
            wf_d(out, "c3_major_factor", dec.main_ellipse.b1_major_factor);
            wf_d(out, "c4_minor_factor", dec.main_ellipse.b1_minor_factor, /*last=*/true);
            out.print('}');
        }

        out.print('}');
        writeChar(out, ',');
    }

    // B2 (A17=01) - Hazard center offset (EWSS CAMF v1.1 §3.7.2)
    if (d.camf.b2_present) {
        wk(out, "hazard_center");
        out.print('{');
        wf_u(out, "c5_raw", d.camf.b2_c5);
        wf_u(out, "c6_raw", d.camf.b2_c6);
        double base_lat = decodeLatitude16(d.camf.a12);
        double base_lon = decodeLongitude17(d.camf.a13);
        wf_d(out, "delta_lat_deg", dec.main_ellipse.lat_deg - base_lat);
        wf_d(out, "delta_lon_deg", dec.main_ellipse.lon_deg - base_lon, /*last=*/true);
        out.print('}');
        writeChar(out, ',');
    }

    // B3 (A17=10) - Secondary ellipse definition (EWSS CAMF v1.1 §3.7.3)
    if (d.camf.b3_present) {
        wk(out, "secondary_ellipse");
        out.print('{');
        wf_u(out, "c7_shift", d.camf.b3_c7);
        wf_u(out, "c8_homothetic", d.camf.b3_c8);
        wf_u(out, "c9_bearing", d.camf.b3_c9);
        wf_u(out, "c10_guidance", d.camf.b3_c10, /*last=*/true);
        out.print('}');
        writeChar(out, ',');
    }

    // B4 (A17=11) - Detailed hazard information (EWSS CAMF v1.1 §3.7.4)
    if (d.camf.b4_present) {
        wk(out, "detailed_info");
        out.print('{');
        bool wroteAny = false;
        wf_u(out, "a4_code", d.camf.a4, /*last=*/true);
        wroteAny = true;
        if (d.camf.b4_d1_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d1_magnitude", d.camf.b4_d1, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d2_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d2_seismic_coeff", d.camf.b4_d2, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d3_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d3_azimuth", d.camf.b4_d3, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d4_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d4_vector_length", d.camf.b4_d4, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d5_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d5_wave_height", d.camf.b4_d5, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d6_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d6_temp_range", d.camf.b4_d6, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d7_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d7_hurricane_cat", d.camf.b4_d7, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d8_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d8_wind_speed", d.camf.b4_d8, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d9_present)  { if (wroteAny) writeChar(out, ','); wf_u(out, "d9_rainfall", d.camf.b4_d9, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d10_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d10_damage", d.camf.b4_d10, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d11_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d11_tornado_prob", d.camf.b4_d11, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d12_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d12_hail_scale", d.camf.b4_d12, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d13_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d13_visibility", d.camf.b4_d13, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d14_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d14_snow_depth", d.camf.b4_d14, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d15_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d15_flood_severity", d.camf.b4_d15, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d16_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d16_lightning", d.camf.b4_d16, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d17_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d17_fog_level", d.camf.b4_d17, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d18_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d18_drought", d.camf.b4_d18, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d19_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d19_avalanche", d.camf.b4_d19, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d20_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d20_ash_fall", d.camf.b4_d20, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d21_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d21_geomagnetic", d.camf.b4_d21, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d22_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d22_terrorism", d.camf.b4_d22, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d23_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d23_fire_risk", d.camf.b4_d23, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d24_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d24_water_quality", d.camf.b4_d24, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d25_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d25_uv_index", d.camf.b4_d25, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d26_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d26_cases_per_100k", d.camf.b4_d26, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d27_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d27_noise", d.camf.b4_d27, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d28_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d28_air_quality", d.camf.b4_d28, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d29_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d29_outage_duration", d.camf.b4_d29, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d30_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d30_nuclear_scale", d.camf.b4_d30, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d31_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d31_chemical_type", d.camf.b4_d31, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d32_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d32_biohazard_level", d.camf.b4_d32, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d33_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d33_biohazard_type", d.camf.b4_d33, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d34_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d34_explosive_type", d.camf.b4_d34, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d35_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d35_infection_type", d.camf.b4_d35, /*last=*/true); wroteAny = true; }
        if (d.camf.b4_d36_present) { if (wroteAny) writeChar(out, ','); wf_u(out, "d36_typhoon_cat", d.camf.b4_d36, /*last=*/true); wroteAny = true; }
        out.print('}');
        writeChar(out, ',');
    }

    // Extended Message fields
    if (d.ex_kind == ExtendedKind::LAlertOrLocal) {
        wf_u(out, "ex1_target_area", d.ex_lalert_local.ex1);
        wf_s(out, "ex1_target_area_label",
            qzss_dcx_ex1_target_area_code_ja_lookup(d.ex_lalert_local.ex1));

        // Decoded target area code (when main ellipse is absent)
        if (dec.target_area_code_present) {
            wf_u(out, "target_area_code", dec.target_area_code);
        }

        // EX2-EX7 Additional Ellipse (local government only)
        if (dec.additional_area.present) {
            wk(out, "additional_area");
            out.print('{');
            wf_u(out, "head_to_area", dec.additional_area.head_to_area);
            wk(out, "ellipse");
            out.print('{');
            wf_d(out, "lat_deg", dec.additional_area.ellipse.lat_deg);
            wf_d(out, "lon_deg", dec.additional_area.ellipse.lon_deg);
            wf_d(out, "semi_major_km", dec.additional_area.ellipse.semi_major_km);
            wf_d(out, "semi_minor_km", dec.additional_area.ellipse.semi_minor_km);
            wf_d(out, "azimuth_deg", dec.additional_area.ellipse.azimuth_deg, /*last=*/true);
            out.print('}');
            out.print('}');
            writeChar(out, ',');
        }
        wf_u(out, "ex_vn", d.ex_lalert_local.vn);
    } else if (d.ex_kind == ExtendedKind::JAlert) {
        wf_u(out, "ex8_area_type", d.ex_jalert.ex8);

        // Decoded J-Alert target area
        wk(out, "jalert_target");
        out.print('{');
        wf_u(out, "prefecture_mode", dec.jalert_prefecture_mode);
        if (dec.jalert_prefecture_mode) {
            // Prefecture positions
            wk(out, "prefecture_positions");
            out.print('[');
            for (uint8_t i = 0; i < dec.prefecture_count; ++i) {
                if (i) writeChar(out, ',');
                writeUint32(out, dec.prefecture_positions[i]);
            }
            out.print("],");
            // Prefecture labels
            wk(out, "prefecture_labels");
            out.print('[');
            for (uint8_t i = 0; i < dec.prefecture_count; ++i) {
                if (i) writeChar(out, ',');
                uint8_t pos = dec.prefecture_positions[i];
                std::optional<std::string_view> label = qzss_dcr_jma_prefecture_lookup(pos);
                writeOptStr(out, label);
            }
            out.print(']');
        } else {
            // City/town/village codes
            wk(out, "city_codes");
            out.print('[');
            for (uint8_t i = 0; i < dec.city_code_count; ++i) {
                if (i) writeChar(out, ',');
                writeUint32(out, dec.city_codes[i]);
            }
            out.print("],");
            // City labels
            wk(out, "city_labels");
            out.print('[');
            for (uint8_t i = 0; i < dec.city_code_count; ++i) {
                if (i) writeChar(out, ',');
                std::optional<std::string_view> label = qzss_dcx_ex1_target_area_code_ja_lookup(dec.city_codes[i]);
                writeOptStr(out, label);
            }
            out.print(']');
        }
        out.print('}');
        writeChar(out, ',');
        wf_u(out, "ex_vn", d.ex_jalert.vn);
    } else if (d.ex_kind == ExtendedKind::OutsideJapan) {
        // EX11 raw data (68 bits) - output as hex string
        char ex11_hex[19];
        for (int i = 0; i < 9; ++i) {
            snprintf(ex11_hex + i * 2, 3, "%02X", d.ex_outside.ex11_raw[i]);
        }
        wf_s(out, "ex11_raw", ex11_hex);
        wf_u(out, "ex_vn", d.ex_outside.vn);
    }

    // Alert identity
    wk(out, "alert_identity");
    out.print('{');
    wf_u(out, "a2", dec.alert_identity.a2);
    wf_u(out, "a3", dec.alert_identity.a3);
    wf_u(out, "a4", dec.alert_identity.a4);
    wf_u(out, "ex1", dec.alert_identity.ex1, /*last=*/true);
    out.print('}');
    writeChar(out, ',');

    wf_u(out, "sd_sdmt", d.sd.sdmt);
    wf_u(out, "sd_sdm", d.sd.sdm, /*last=*/true);
}

} // namespace internal
} // namespace azaraC
