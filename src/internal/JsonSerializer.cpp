
// azaraC - src/internal/JsonSerializer.cpp
// All label strings come from definition/_index.h lookup functions.
// No disaster strings are hardcoded here.

#include "JsonSerializer.h"
#include "../definition/_index.h"
#include <optional>
#include <string_view>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// Primitive writers
// ---------------------------------------------------------------------------
static void writeChar(Print& out, char c) { out.print(c); }

static void writeUint32(Print& out, uint32_t v) {
    char buf[11]; int8_t i = 10; buf[i] = '\0';
    if (v == 0) { out.print('0'); return; }
    while (v) { buf[--i] = '0' + (v % 10); v /= 10; }
    out.print(buf + i);
}

static void writeInt32(Print& out, int32_t v) {
    if (v < 0) {
        out.print('-');
        writeUint32(out, 0u - (uint32_t)v);
    } else {
        writeUint32(out, (uint32_t)v);
    }
}

static void writeStr(Print& out, std::string_view s) {
    out.print('"'); if (!s.empty()) out.write(s.data(), s.size()); out.print('"');
}

static void writeOptStr(Print& out, std::optional<std::string_view> s) {
    writeStr(out, s.value_or(""));
}

static void writeHex(Print& out, uint8_t v) {
    char buf[5] = "\"00\"";
    const char hex[] = "0123456789ABCDEF";
    buf[1] = hex[v >> 4];
    buf[2] = hex[v & 0x0F];
    out.print(buf);
}

// key: "foo":
static void wk(Print& out, std::string_view k) {
    writeChar(out, '"'); if (!k.empty()) out.write(k.data(), k.size()); out.print("\":");
}

// "key":value,
static void wf_u(Print& out, std::string_view k, uint32_t v, bool last = false) {
    wk(out, k); writeUint32(out, v); if (!last) writeChar(out, ',');
}
static void wf_i(Print& out, std::string_view k, int32_t v, bool last = false) {
    wk(out, k); writeInt32(out, v);  if (!last) writeChar(out, ',');
}
// Accepts optional<string_view> — outputs "" when nullopt (label not found)
static void wf_s(Print& out, std::string_view k, std::optional<std::string_view> v, bool last = false) {
    wk(out, k); writeOptStr(out, v); if (!last) writeChar(out, ',');
}


// ---------------------------------------------------------------------------
// Helpers for repeated structures
// ---------------------------------------------------------------------------

// Write a DHM TimeFields object as nested JSON
static void writeDHM(Print& out, std::string_view key, const TimeFields& t, bool last = false) {
    wk(out, key);
    out.print('{');
    wf_u(out, "day",   t.day);
    wf_u(out, "hour",  t.hour);
    wf_u(out, "min",   t.minute);
    wf_u(out, "unix",  t.unix_time, /*last=*/true);
    out.print('}');
    if (!last) writeChar(out, ',');
}

static void writeLatLon(Print& out, std::string_view key, const LatLon& ll, bool last = false) {
    wk(out, key);
    out.print('{');
    wf_u(out, "lat_ns",  ll.lat_ns);
    wf_u(out, "lat_deg", ll.lat_deg);
    wf_u(out, "lat_min", ll.lat_min);
    wf_u(out, "lat_sec", ll.lat_sec);
    wf_u(out, "lon_ew",  ll.lon_ew);
    wf_u(out, "lon_deg", ll.lon_deg);
    wf_u(out, "lon_min", ll.lon_min);
    wf_u(out, "lon_sec", ll.lon_sec, /*last=*/true);
    out.print('}');
    if (!last) writeChar(out, ',');
}

// Write the 12-bit packed arrival time (day_offset:1, hour:5, min:6)
static void writeArrivalTimeFields(Print& out, uint16_t raw) {
    wf_u(out, "arrival_day_offset", (raw >> 11) & 1u);
    wf_u(out, "arrival_hour",       (raw >>  6) & 0x1Fu);
    wf_u(out, "arrival_min",        raw & 0x3Fu);
}

// ---------------------------------------------------------------------------
// MT=44 DCX
// ---------------------------------------------------------------------------
static void serializeDcx(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "dcx_type", (uint32_t)static_cast<uint8_t>(m.service_kind));

    std::string_view dcx_label = "UNKNOWN";
    switch (m.service_kind) {
        case Mt44ServiceKind::NullMessage:     dcx_label = "NULL"; break;
        case Mt44ServiceKind::LAlert:          dcx_label = "L_ALERT"; break;
        case Mt44ServiceKind::JAlert:          dcx_label = "J_ALERT"; break;
        case Mt44ServiceKind::LocalGovernment: dcx_label = "LOCAL_GOV"; break;
        case Mt44ServiceKind::OutsideJapan:    dcx_label = "OUTSIDE_JAPAN"; break;
        default: break;
    }
    wf_s(out, "dcx_type_label", dcx_label);

    wf_s(out, "a1_msg_type",
        qzss_dcx_camf_a1_message_type_lookup(m.camf.a1));
    wf_u(out, "a2_country", m.camf.a2);
    wf_s(out, "a2_country_label",
        qzss_dcx_camf_a2_country_region_name_lookup(m.camf.a2));
    wf_u(out, "a3_provider", m.camf.a3);
    wf_s(out, "a3_provider_label",
        qzss_dcx_camf_a3_provider_identifier_lookup(m.camf.a2, m.camf.a3));
    wf_u(out, "a4_hazard", m.camf.a4);
    wf_s(out, "a4_hazard_category",
        qzss_dcx_camf_a4_hazard_category_lookup(m.camf.a4));
    wf_s(out, "a4_hazard_type",
        qzss_dcx_camf_a4_hazard_type_lookup(m.camf.a4));
    wf_u(out, "a5_severity", m.camf.a5);
    wf_s(out, "a5_severity_label",
        qzss_dcx_camf_a5_severity_lookup(m.camf.a5));
    wf_u(out, "a6_onset_week", m.camf.a6);
    wf_u(out, "a7_onset_minute", m.camf.a7);
    wf_u(out, "a8_duration", m.camf.a8);
    wf_s(out, "a8_duration_label",
        qzss_dcx_camf_a8_hazard_duration_lookup(m.camf.a8));
    writeDHM(out, "onset_time", m.onset_time);
    wf_i(out, "lat_e2", (int32_t)m.camf.a12);
    wf_i(out, "lon_e2", (int32_t)m.camf.a13);

    // A11 Guidance to react library
    wf_u(out, "a11_guidance", m.camf.a11);
    wf_s(out, "a11_guidance_label",
        qzss_dcx_camf_a11_japanese_library_ja_lookup(m.camf.a11));

    // A17/A18 Specific Settings
    wf_u(out, "a17_specific_subject", m.camf.a17);
    wf_s(out, "a17_specific_subject_label",
        qzss_dcx_camf_a17_main_subject_for_specific_settings_lookup(m.camf.a17));
    wf_u(out, "a18_specific_settings", m.camf.a18);

    // Extended Message fields
    if (m.ex_kind == ExtendedKind::LAlertOrLocal) {
        wf_u(out, "ex1_target_area", m.ex_lalert_local.ex1);
        wf_s(out, "ex1_target_area_label",
            qzss_dcx_ex1_target_area_code_ja_lookup(m.ex_lalert_local.ex1));
        // EX2-EX7 Additional Ellipse (local government only)
        wf_u(out, "ex2_evac_dir", m.ex_lalert_local.ex2);
        wf_i(out, "ex3_add_lat", m.ex_lalert_local.ex3);
        wf_i(out, "ex4_add_lon", m.ex_lalert_local.ex4);
        wf_u(out, "ex5_add_semi_major", m.ex_lalert_local.ex5);
        wf_u(out, "ex6_add_semi_minor", m.ex_lalert_local.ex6);
        wf_u(out, "ex7_add_azimuth", m.ex_lalert_local.ex7);
        wf_u(out, "ex_vn", m.ex_lalert_local.vn);
    } else if (m.ex_kind == ExtendedKind::JAlert) {
        wf_u(out, "ex8_area_type", m.ex_jalert.ex8);
        wf_u(out, "ex9_area_list", m.ex_jalert.ex9);
        wf_u(out, "ex10_reserved", m.ex_jalert.ex10);
        wf_u(out, "ex_vn", m.ex_jalert.vn);
    } else if (m.ex_kind == ExtendedKind::OutsideJapan) {
        // EX11 raw data (68 bits) - output as hex string
        char ex11_hex[19];
        for (int i = 0; i < 9; ++i) {
            snprintf(ex11_hex + i * 2, 3, "%02X", m.ex_outside.ex11_raw[i]);
        }
        wf_s(out, "ex11_raw", ex11_hex);
        wf_u(out, "ex_vn", m.ex_outside.vn);
    }

    wf_u(out, "sd_sdmt", m.sd.sdmt);
    wf_u(out, "sd_sdm", m.sd.sdm, /*last=*/true);
}

// ---------------------------------------------------------------------------
// MT=43 sub-type serializers
// Each returns after writing its last field with last=true
// ---------------------------------------------------------------------------

static void serializeEEW(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "long_period_lower", m.eew_long_period_lower);
    wf_s(out, "long_period_lower_label",
        qzss_dcr_jma_long_period_ground_motion_lower_limit_lookup(m.eew_long_period_lower));
    wf_u(out, "long_period_upper", m.eew_long_period_upper);
    wf_s(out, "long_period_upper_label",
        qzss_dcr_jma_long_period_ground_motion_upper_limit_lookup(m.eew_long_period_upper));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < m.eew_notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = m.eew_notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeDHM(out, "quake_time", m.eew_quake_time);
    wf_u(out, "depth", m.eew_depth);
    wf_u(out, "magnitude", m.eew_magnitude);
    wf_u(out, "epicenter", m.eew_epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(m.eew_epicenter));
    wf_u(out, "intensity_lower", m.eew_intensity_lower);
    wf_s(out, "intensity_lower_label",
        qzss_dcr_jma_seismic_intensity_lower_limit_lookup(m.eew_intensity_lower));
    wf_u(out, "intensity_upper", m.eew_intensity_upper);
    wf_s(out, "intensity_upper_label",
        qzss_dcr_jma_seismic_intensity_upper_limit_lookup(m.eew_intensity_upper));
    // regions array
    wk(out, "regions"); out.print('[');
    for (uint8_t i = 0; i < m.eew_region_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = m.eew_regions[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label",
            qzss_dcr_jma_eew_forecast_region_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeHypocenter(const Message& m, Print& out) {
    using namespace azaraC::def;
    writeDHM(out, "quake_time", m.hypo_quake_time);
    wf_u(out, "depth",     m.hypo_depth);
    wf_u(out, "magnitude", m.hypo_magnitude);
    wf_u(out, "epicenter", m.hypo_epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(m.hypo_epicenter));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < m.hypo_notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = m.hypo_notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeLatLon(out, "coords", m.hypo_coords, /*last=*/true);
}

static void serializeSeismic(const Message& m, Print& out) {
    using namespace azaraC::def;
    writeDHM(out, "quake_time", m.seis_quake_time);
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.seis_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "intensity", m.seis_entries[i].intensity_code);
        wf_s(out, "intensity_label",
            qzss_dcr_jma_seismic_intensity_lookup(m.seis_entries[i].intensity_code));
        wf_u(out, "prefecture", m.seis_entries[i].prefecture_code);
        wf_s(out, "prefecture_label",
            qzss_dcr_jma_prefecture_lookup(m.seis_entries[i].prefecture_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeNankai(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "info_code", m.nankai_info_code);
    wf_s(out, "info_code_label",
        qzss_dcr_jma_information_serial_code_lookup(m.nankai_info_code));
    wf_u(out, "page",       m.nankai_page);
    wf_u(out, "total_page", m.nankai_total_page);
    // text as hex bytes array
    wk(out, "text_hex"); out.print('[');
    for (uint8_t i = 0; i < 18; ++i) {
        if (i) writeChar(out, ',');
        writeHex(out, m.nankai_text[i]);
    }
    out.print(']');
}

static void serializeTsunami(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "warning_code", m.tsunami_warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_tsunami_warning_code_lookup(m.tsunami_warning_code));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.tsunami_count; ++i) {
        if (i) writeChar(out, ',');
        const TsunamiEntry& e = m.tsunamis[i];
        out.print('{');
        uint16_t raw = e.arrival_time_raw;
        writeArrivalTimeFields(out, raw);
        wf_u(out, "arrival_time_raw", raw);
        writeDHM(out, "arrival_time", e.arrival_time);
        wf_u(out, "height",           e.height_code);
        wf_s(out, "height_label",
            qzss_dcr_jma_tsunami_height_lookup(e.height_code));
        wf_u(out, "region",           e.region_code);
        wf_s(out, "region_label",
            qzss_dcr_jma_tsunami_forecast_region_lookup(e.region_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeNwPacTsu(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "potential", m.nw_pac_potential);
    wf_s(out, "potential_label",
        qzss_dcr_jma_tsunamigenic_potential_en_lookup(m.nw_pac_potential));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.nw_pac_count; ++i) {
        if (i) writeChar(out, ',');
        const NwPacTsunamiEntry& e = m.nw_pac_tsunamis[i];
        out.print('{');
        uint16_t raw = e.arrival_time_raw;
        writeArrivalTimeFields(out, raw);
        wf_u(out, "arrival_time_raw", raw);
        writeDHM(out, "arrival_time", e.arrival_time);
        wf_u(out, "height",           e.height_code);
        wf_s(out, "height_label",
            qzss_dcr_jma_northwest_pacific_tsunami_height_en_lookup(e.height_code));
        wf_u(out, "region",           e.region_code);
        wf_s(out, "region_label",
            qzss_dcr_jma_coastal_region_en_lookup(e.region_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeVolcano(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "ambiguity",     m.vol_ambiguity);
    writeDHM(out, "activity_time", m.vol_activity_time);
    wf_u(out, "warning_code",  m.vol_warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_volcanic_warning_code_lookup(m.vol_warning_code));
    wf_u(out, "volcano_name",  m.vol_volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(m.vol_volcano_name));
    wk(out, "local_govs"); out.print('[');
    for (uint8_t i = 0; i < m.vol_lg_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "code", m.vol_local_govs[i]);
        wf_s(out, "label",
            qzss_dcr_jma_local_government_lookup(m.vol_local_govs[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeAshFall(const Message& m, Print& out) {
    using namespace azaraC::def;
    writeDHM(out, "activity_time", m.ash_activity_time);
    wf_u(out, "warning_type", m.ash_warning_type);
    wf_u(out, "volcano_name", m.ash_volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(m.ash_volcano_name));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.ash_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "arrival_hour", m.ash_entries_time[i]);
        wf_u(out, "warning_code", m.ash_entries_code[i]);
        wf_s(out, "warning_code_label",
            qzss_dcr_jma_ash_fall_warning_code_lookup(m.ash_entries_code[i]));
        wf_u(out, "local_gov", m.ash_entries_lg[i]);
        wf_s(out, "local_gov_label",
            qzss_dcr_jma_local_government_lookup(m.ash_entries_lg[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeWeather(const Message& m, Print& out) {
    using namespace azaraC::def;
    wf_u(out, "warning_state", m.wx_warning_state);
    wf_s(out, "warning_state_label",
        qzss_dcr_jma_weather_warning_state_lookup(m.wx_warning_state));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.wx_count; ++i) {
        if (i) writeChar(out, ',');
        const WeatherEntry& e = m.wx_entries[i];
        out.print('{');
        wf_u(out, "sub_category", e.sub_category);
        wf_s(out, "sub_category_label",
            qzss_dcr_jma_weather_related_disaster_sub_category_lookup(e.sub_category));
        wf_u(out, "region", e.region_code);
        wf_s(out, "region_label",
            qzss_dcr_jma_weather_forecast_region_lookup(e.region_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeFlood(const Message& m, Print& out) {
    using namespace azaraC::def;
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.flood_count; ++i) {
        if (i) writeChar(out, ',');
        const FloodEntry& e = m.flood_entries[i];
        out.print('{');
        wf_u(out, "warning_level", e.warning_level);
        wf_s(out, "warning_level_label",
            qzss_dcr_jma_flood_warning_level_lookup(e.warning_level));
        // 40-bit region code: store as two uint32 fields (hi/lo split)
        wf_u(out, "region_hi", (uint32_t)(e.region_code >> 20));
        wf_u(out, "region_lo", (uint32_t)(e.region_code & 0xFFFFFu), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeMarine(const Message& m, Print& out) {
    using namespace azaraC::def;
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < m.marine_count; ++i) {
        if (i) writeChar(out, ',');
        const MarineEntry& e = m.marine_entries[i];
        out.print('{');
        wf_u(out, "warning_code", e.warning_code);
        wf_s(out, "warning_code_label",
            qzss_dcr_jma_marine_warning_code_lookup(e.warning_code));
        wf_u(out, "region", e.region_code);
        wf_s(out, "region_label",
            qzss_dcr_jma_marine_forecast_region_lookup(e.region_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

static void serializeTyphoon(const Message& m, Print& out) {
    using namespace azaraC::def;
    writeDHM(out, "reference_time", m.typh_reference_time);
    wf_u(out, "ref_type", m.typh_ref_type);
    wf_s(out, "ref_type_label",
        qzss_dcr_jma_typhoon_reference_time_type_lookup(m.typh_ref_type));
    wf_u(out, "elapsed",   m.typh_elapsed);
    wf_u(out, "number",    m.typh_number);
    wf_u(out, "scale",     m.typh_scale);
    wf_s(out, "scale_label",
        qzss_dcr_jma_typhoon_scale_category_lookup(m.typh_scale));
    wf_u(out, "intensity", m.typh_intensity);
    wf_s(out, "intensity_label",
        qzss_dcr_jma_typhoon_intensity_category_lookup(m.typh_intensity));
    wk(out, "positions"); out.print('[');
    for (uint8_t i = 0; i < m.typh_pos_count; ++i) {
        if (i) writeChar(out, ',');
        const TyphoonPos & p = m.typh_positions[i];
        out.print('{');
        wf_i(out, "lat_e1", (int32_t)p.lat_e1);
        wf_i(out, "lon_e1", (int32_t)p.lon_e1, /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

// ---------------------------------------------------------------------------
// Top-level serialize
// ---------------------------------------------------------------------------
void JsonSerializer::serialize(const Message& msg, Print& out) {
    using namespace azaraC::def;
    out.print('{');
    wf_u(out, "svid",     msg.svid);
    wf_u(out, "msg_type", msg.msg_type);
    wf_u(out, "crc24",    msg.crc24);

    if (msg.msg_type == 44) {
        serializeDcx(msg, out);

    } else if (msg.msg_type == 43) {
        wf_u(out, "report_classification", msg.report_classification);
        wf_s(out, "report_classification_label",
            qzss_dcr_jma_report_classification_lookup(msg.report_classification));
        wf_u(out, "disaster_category", msg.disaster_category);
        wf_s(out, "disaster_category_label",
            qzss_dcr_jma_disaster_category_lookup(msg.disaster_category));
        wf_u(out, "information_type", msg.information_type);
        wf_s(out, "information_type_label",
            qzss_dcr_jma_information_type_lookup(msg.information_type));
        writeDHM(out, "report_time", msg.event_time);
        wk(out, "detail"); out.print('{');
        switch (msg.disaster_category) {
            case  1: serializeEEW       (msg, out); break;
            case  2: serializeHypocenter(msg, out); break;
            case  3: serializeSeismic   (msg, out); break;
            case  4: serializeNankai    (msg, out); break;
            case  5: serializeTsunami   (msg, out); break;
            case  6: serializeNwPacTsu  (msg, out); break;
            case  8: serializeVolcano   (msg, out); break;
            case  9: serializeAshFall   (msg, out); break;
            case 10: serializeWeather   (msg, out); break;
            case 11: serializeFlood     (msg, out); break;
            case 12: serializeTyphoon   (msg, out); break;
            case 14: serializeMarine    (msg, out); break;
            default: wf_s(out, "note", "unsupported_category", /*last=*/true); break;
        }
        out.print('}');  // detail

    } else {
        wf_s(out, "note", "unsupported_msg_type", /*last=*/true);
    }

    out.print('}');
}

} // namespace internal
} // namespace azaraC
