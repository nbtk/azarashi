// azaraC - src/internal/JsonSerializerQzqsm.cpp
// MT=43 QZQSM JSON serializer

#include "JsonWriter.h"
#include "../definition/_index.h"
#include <optional>
#include <string_view>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// MT=43 sub-type serializers
// Each returns after writing its last field with last=true
// ---------------------------------------------------------------------------

void serializeEEW(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "long_period_lower", d.eew_long_period_lower);
    wf_s(out, "long_period_lower_label",
        qzss_dcr_jma_long_period_ground_motion_lower_limit_lookup(d.eew_long_period_lower));
    wf_u(out, "long_period_upper", d.eew_long_period_upper);
    wf_s(out, "long_period_upper_label",
        qzss_dcr_jma_long_period_ground_motion_upper_limit_lookup(d.eew_long_period_upper));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < d.eew_notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.eew_notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeDHM(out, "quake_time", d.eew_quake_time);
    wf_u(out, "depth", d.eew_depth);
    wf_u(out, "magnitude", d.eew_magnitude);
    wf_u(out, "epicenter", d.eew_epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(d.eew_epicenter));
    wf_u(out, "intensity_lower", d.eew_intensity_lower);
    wf_s(out, "intensity_lower_label",
        qzss_dcr_jma_seismic_intensity_lower_limit_lookup(d.eew_intensity_lower));
    wf_u(out, "intensity_upper", d.eew_intensity_upper);
    wf_s(out, "intensity_upper_label",
        qzss_dcr_jma_seismic_intensity_upper_limit_lookup(d.eew_intensity_upper));
    // regions array
    wk(out, "regions"); out.print('[');
    for (uint8_t i = 0; i < d.eew_region_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.eew_regions[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label",
            qzss_dcr_jma_eew_forecast_region_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeHypocenter(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "quake_time", d.hypo_quake_time);
    wf_u(out, "depth",     d.hypo_depth);
    wf_u(out, "magnitude", d.hypo_magnitude);
    wf_u(out, "epicenter", d.hypo_epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(d.hypo_epicenter));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < d.hypo_notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.hypo_notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeLatLon(out, "coords", d.hypo_coords, /*last=*/true);
}

void serializeSeismic(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "quake_time", d.seis_quake_time);
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.seis_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "intensity", d.seis_entries[i].intensity_code);
        wf_s(out, "intensity_label",
            qzss_dcr_jma_seismic_intensity_lookup(d.seis_entries[i].intensity_code));
        wf_u(out, "prefecture", d.seis_entries[i].prefecture_code);
        wf_s(out, "prefecture_label",
            qzss_dcr_jma_prefecture_lookup(d.seis_entries[i].prefecture_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeNankai(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "info_code", d.nankai_info_code);
    wf_s(out, "info_code_label",
        qzss_dcr_jma_information_serial_code_lookup(d.nankai_info_code));
    wf_u(out, "page",       d.nankai_page);
    wf_u(out, "total_page", d.nankai_total_page);
    // text as hex bytes array
    wk(out, "text_hex"); out.print('[');
    for (uint8_t i = 0; i < 18; ++i) {
        if (i) writeChar(out, ',');
        writeHex(out, d.nankai_text[i]);
    }
    out.print(']');
}

void serializeTsunami(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "warning_code", d.tsunami_warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_tsunami_warning_code_lookup(d.tsunami_warning_code));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.tsunami_count; ++i) {
        if (i) writeChar(out, ',');
        const TsunamiEntry& e = d.tsunamis[i];
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

void serializeNwPacTsu(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "potential", d.nw_pac_potential);
    wf_s(out, "potential_label",
        qzss_dcr_jma_tsunamigenic_potential_en_lookup(d.nw_pac_potential));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.nw_pac_count; ++i) {
        if (i) writeChar(out, ',');
        const NwPacTsunamiEntry& e = d.nw_pac_tsunamis[i];
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

void serializeVolcano(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "ambiguity",     d.vol_ambiguity);
    writeDHM(out, "activity_time", d.vol_activity_time);
    wf_u(out, "warning_code",  d.vol_warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_volcanic_warning_code_lookup(d.vol_warning_code));
    wf_u(out, "volcano_name",  d.vol_volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(d.vol_volcano_name));
    wk(out, "local_govs"); out.print('[');
    for (uint8_t i = 0; i < d.vol_lg_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "code", d.vol_local_govs[i]);
        wf_s(out, "label",
            qzss_dcr_jma_local_government_lookup(d.vol_local_govs[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeAshFall(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "activity_time", d.ash_activity_time);
    wf_u(out, "warning_type", d.ash_warning_type);
    wf_u(out, "volcano_name", d.ash_volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(d.ash_volcano_name));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.ash_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "arrival_hour", d.ash_entries_time[i]);
        wf_u(out, "warning_code", d.ash_entries_code[i]);
        wf_s(out, "warning_code_label",
            qzss_dcr_jma_ash_fall_warning_code_lookup(d.ash_entries_code[i]));
        wf_u(out, "local_gov", d.ash_entries_lg[i]);
        wf_s(out, "local_gov_label",
            qzss_dcr_jma_local_government_lookup(d.ash_entries_lg[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeWeather(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "warning_state", d.wx_warning_state);
    wf_s(out, "warning_state_label",
        qzss_dcr_jma_weather_warning_state_lookup(d.wx_warning_state));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.wx_count; ++i) {
        if (i) writeChar(out, ',');
        const WeatherEntry& e = d.wx_entries[i];
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

void serializeFlood(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.flood_count; ++i) {
        if (i) writeChar(out, ',');
        const FloodEntry& e = d.flood_entries[i];
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

void serializeMarine(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.marine_count; ++i) {
        if (i) writeChar(out, ',');
        const MarineEntry& e = d.marine_entries[i];
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

void serializeTyphoon(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "reference_time", d.typh_reference_time);
    wf_u(out, "ref_type", d.typh_ref_type);
    wf_s(out, "ref_type_label",
        qzss_dcr_jma_typhoon_reference_time_type_lookup(d.typh_ref_type));
    wf_u(out, "elapsed",   d.typh_elapsed);
    wf_u(out, "number",    d.typh_number);
    wf_u(out, "scale",     d.typh_scale);
    wf_s(out, "scale_label",
        qzss_dcr_jma_typhoon_scale_category_lookup(d.typh_scale));
    wf_u(out, "intensity", d.typh_intensity);
    wf_s(out, "intensity_label",
        qzss_dcr_jma_typhoon_intensity_category_lookup(d.typh_intensity));
    // Typhoon center coordinates (LatLon: 41-bit DMS format)
    writeLatLon(out, "coords", d.typh_coords);
    // Central pressure (11 bits, hPa)
    wf_u(out, "pressure", d.typh_pressure);
    // Maximum wind speed (7 bits, m/s)
    wf_u(out, "max_wind", d.typh_max_wind);
    // Maximum wind gust speed (7 bits, m/s)
    wf_u(out, "max_gust", d.typh_max_gust, /*last=*/true);
}

} // namespace internal
} // namespace azaraC
