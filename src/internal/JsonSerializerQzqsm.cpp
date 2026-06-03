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
    wf_u(out, "long_period_lower", d.eew.long_period_lower);
    wf_s(out, "long_period_lower_label",
        qzss_dcr_jma_long_period_ground_motion_lower_limit_lookup(d.eew.long_period_lower));
    wf_u(out, "long_period_upper", d.eew.long_period_upper);
    wf_s(out, "long_period_upper_label",
        qzss_dcr_jma_long_period_ground_motion_upper_limit_lookup(d.eew.long_period_upper));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < d.eew.notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.eew.notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeDHM(out, "quake_time", d.eew.quake_time);
    wf_u(out, "depth", d.eew.depth);
    wf_u(out, "magnitude", d.eew.magnitude);
    wf_u(out, "epicenter", d.eew.epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(d.eew.epicenter));
    wf_u(out, "intensity_lower", d.eew.intensity_lower);
    wf_s(out, "intensity_lower_label",
        qzss_dcr_jma_seismic_intensity_lower_limit_lookup(d.eew.intensity_lower));
    wf_u(out, "intensity_upper", d.eew.intensity_upper);
    wf_s(out, "intensity_upper_label",
        qzss_dcr_jma_seismic_intensity_upper_limit_lookup(d.eew.intensity_upper));
    // regions array
    wk(out, "regions"); out.print('[');
    for (uint8_t i = 0; i < d.eew.region_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.eew.regions[i];
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
    writeDHM(out, "quake_time", d.hypo.quake_time);
    wf_u(out, "depth",     d.hypo.depth);
    wf_u(out, "magnitude", d.hypo.magnitude);
    wf_u(out, "epicenter", d.hypo.epicenter);
    wf_s(out, "epicenter_label",
        qzss_dcr_jma_epicenter_and_hypocenter_lookup(d.hypo.epicenter));
    wk(out, "notifications"); out.print('[');
    for (uint8_t i = 0; i < d.hypo.notification_count; ++i) {
        if (i) writeChar(out, ',');
        uint16_t code = d.hypo.notification[i];
        out.print('{');
        wf_u(out, "code", code);
        wf_s(out, "label", qzss_dcr_jma_notification_on_disaster_prevention_lookup(code), /*last=*/true);
        out.print('}');
    }
    out.print("],");
    writeLatLon(out, "coords", d.hypo.coords, /*last=*/true);
}

void serializeSeismic(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "quake_time", d.seis.quake_time);
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.seis.count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "intensity", d.seis.entries[i].intensity_code);
        wf_s(out, "intensity_label",
            qzss_dcr_jma_seismic_intensity_lookup(d.seis.entries[i].intensity_code));
        wf_u(out, "prefecture", d.seis.entries[i].prefecture_code);
        wf_s(out, "prefecture_label",
            qzss_dcr_jma_prefecture_lookup(d.seis.entries[i].prefecture_code), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeNankai(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "info_code", d.nankai.info_code);
    wf_s(out, "info_code_label",
        qzss_dcr_jma_information_serial_code_lookup(d.nankai.info_code));
    
    // Output aggregated text if available (multi-page complete)
    if (d.nankai.is_aggregated && d.nankai.aggregated_len > 0) {
        wf_u(out, "page", 1);
        wf_u(out, "total_page", 1);
        wk(out, "text_utf8");
        writeStr(out, std::string_view(d.nankai.aggregated_text, d.nankai.aggregated_len));
    } else {
        // Single page or incomplete - output page info and hex
        wf_u(out, "page", d.nankai.page);
        wf_u(out, "total_page", d.nankai.total_page);
        // text as hex bytes array
        wk(out, "text_hex"); out.print('[');
        for (uint8_t i = 0; i < 18; ++i) {
            if (i) writeChar(out, ',');
            writeHex(out, d.nankai.text[i]);
        }
        out.print(']');
    }
}

void serializeTsunami(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "warning_code", d.tsunami.warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_tsunami_warning_code_lookup(d.tsunami.warning_code));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.tsunami.count; ++i) {
        if (i) writeChar(out, ',');
        const TsunamiEntry& e = d.tsunami.entries[i];
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
    wf_u(out, "potential", d.nw_pac.potential);
    wf_s(out, "potential_label",
        qzss_dcr_jma_tsunamigenic_potential_en_lookup(d.nw_pac.potential));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.nw_pac.count; ++i) {
        if (i) writeChar(out, ',');
        const NwPacTsunamiEntry& e = d.nw_pac.entries[i];
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
    wf_u(out, "ambiguity",     d.vol.ambiguity);
    writeDHM(out, "activity_time", d.vol.activity_time);
    wf_u(out, "warning_code",  d.vol.warning_code);
    wf_s(out, "warning_code_label",
        qzss_dcr_jma_volcanic_warning_code_lookup(d.vol.warning_code));
    wf_u(out, "volcano_name",  d.vol.volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(d.vol.volcano_name));
    wk(out, "local_govs"); out.print('[');
    for (uint8_t i = 0; i < d.vol.lg_count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "code", d.vol.local_govs[i]);
        wf_s(out, "label",
            qzss_dcr_jma_local_government_lookup(d.vol.local_govs[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeAshFall(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    writeDHM(out, "activity_time", d.ash.activity_time);
    wf_u(out, "warning_type", d.ash.warning_type);
    wf_u(out, "volcano_name", d.ash.volcano_name);
    wf_s(out, "volcano_name_label",
        qzss_dcr_jma_volcano_name_lookup(d.ash.volcano_name));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.ash.count; ++i) {
        if (i) writeChar(out, ',');
        out.print('{');
        wf_u(out, "arrival_hour", d.ash.entries_time[i]);
        wf_u(out, "warning_code", d.ash.entries_code[i]);
        wf_s(out, "warning_code_label",
            qzss_dcr_jma_ash_fall_warning_code_lookup(d.ash.entries_code[i]));
        wf_u(out, "local_gov", d.ash.entries_lg[i]);
        wf_s(out, "local_gov_label",
            qzss_dcr_jma_local_government_lookup(d.ash.entries_lg[i]), /*last=*/true);
        out.print('}');
    }
    out.print(']');
}

void serializeWeather(const Message& m, Print& out) {
    using namespace azaraC::def;
    const Mt43Data& d = m.mt43;
    wf_u(out, "warning_state", d.wx.warning_state);
    wf_s(out, "warning_state_label",
        qzss_dcr_jma_weather_warning_state_lookup(d.wx.warning_state));
    wk(out, "entries"); out.print('[');
    for (uint8_t i = 0; i < d.wx.count; ++i) {
        if (i) writeChar(out, ',');
        const WeatherEntry& e = d.wx.entries[i];
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
    for (uint8_t i = 0; i < d.flood.count; ++i) {
        if (i) writeChar(out, ',');
        const FloodEntry& e = d.flood.entries[i];
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
    for (uint8_t i = 0; i < d.marine.count; ++i) {
        if (i) writeChar(out, ',');
        const MarineEntry& e = d.marine.entries[i];
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
    writeDHM(out, "reference_time", d.typh.reference_time);
    wf_u(out, "ref_type", d.typh.ref_type);
    wf_s(out, "ref_type_label",
        qzss_dcr_jma_typhoon_reference_time_type_lookup(d.typh.ref_type));
    wf_u(out, "elapsed",   d.typh.elapsed);
    wf_u(out, "number",    d.typh.number);
    wf_u(out, "scale",     d.typh.scale);
    wf_s(out, "scale_label",
        qzss_dcr_jma_typhoon_scale_category_lookup(d.typh.scale));
    wf_u(out, "intensity", d.typh.intensity);
    wf_s(out, "intensity_label",
        qzss_dcr_jma_typhoon_intensity_category_lookup(d.typh.intensity));
    // Typhoon center coordinates (LatLon: 41-bit DMS format)
    writeLatLon(out, "coords", d.typh.coords);
    // Central pressure (11 bits, hPa)
    wf_u(out, "pressure", d.typh.pressure);
    // Maximum wind speed (7 bits, m/s)
    wf_u(out, "max_wind", d.typh.max_wind);
    // Maximum wind gust speed (7 bits, m/s)
    wf_u(out, "max_gust", d.typh.max_gust, /*last=*/true);
}

} // namespace internal
} // namespace azaraC
