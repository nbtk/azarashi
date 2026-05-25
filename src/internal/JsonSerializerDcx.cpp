// azaraC - src/internal/JsonSerializerDcx.cpp
// MT=44 DCX JSON serializer

#include "JsonWriter.h"
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
        wf_d(out, "azimuth_deg", dec.main_ellipse.azimuth_deg, /*last=*/true);
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
