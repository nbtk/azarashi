// print_all.cpp — 全災害カテゴリのデコード結果出力
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

static void decode_and_print(const char* name, const char* nmea) {
    printf("\n========== %s ==========\n", name);
    NmeaFramer framer;
    Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            found = true;
            break;
        }
    }
    if (!found) {
        printf("Failed to frame\n");
        return;
    }

    Decoder dec;
    Message msg{};
// 2024-01-01 00:00:00 UTC for reproducible testing
static constexpr uint32_t TEST_TIMESTAMP = 1704067200u;

static void decode_and_print(const char* name, const char* nmea) {
    printf("\n========== %s ==========\n", name);
    NmeaFramer framer;
    Frame frame;
    bool found = false;
    for (int i = 0; nmea[i]; i++) {
        if (framer.feed((uint8_t)nmea[i], frame)) {
            found = true;
            break;
        }
    }
    if (!found) {
        printf("Failed to frame\n");
        return;
    }

    Decoder dec;
    Message msg{};
    bool ok = dec.decode(frame, msg, TEST_TIMESTAMP);
}

    if (!ok) {
        printf("Decode failed\n");
        return;
    }

    printf("msg_type: %u, disaster_category: %u\n", msg.msg_type, msg.mt43.disaster_category);

    switch (msg.mt43.disaster_category) {
        case 1: // EEW
            printf("  eew_long_period_lower: %u\n", msg.mt43.eew.long_period_lower);
            printf("  eew_long_period_upper: %u\n", msg.mt43.eew.long_period_upper);
            printf("  eew_notification_count: %u\n", msg.mt43.eew.notification_count);
            printf("  eew_quake_time: day=%u hour=%u minute=%u\n",
                   msg.mt43.eew.quake_time.day, msg.mt43.eew.quake_time.hour, msg.mt43.eew.quake_time.minute);
            printf("  eew_depth: %u\n", msg.mt43.eew.depth);
            printf("  eew_magnitude: %u\n", msg.mt43.eew.magnitude);
            printf("  eew_epicenter: %u\n", msg.mt43.eew.epicenter);
            printf("  eew_intensity_lower: %u\n", msg.mt43.eew.intensity_lower);
            printf("  eew_intensity_upper: %u\n", msg.mt43.eew.intensity_upper);
            printf("  eew_region_count: %u\n", msg.mt43.eew.region_count);
            break;
        case 2: // Hypocenter
            printf("  hypo_notification_count: %u\n", msg.mt43.hypo.notification_count);
            printf("  hypo_quake_time: day=%u hour=%u minute=%u\n",
                   msg.mt43.hypo.quake_time.day, msg.mt43.hypo.quake_time.hour, msg.mt43.hypo.quake_time.minute);
            printf("  hypo_depth: %u\n", msg.mt43.hypo.depth);
            printf("  hypo_magnitude: %u\n", msg.mt43.hypo.magnitude);
            printf("  hypo_epicenter: %u\n", msg.mt43.hypo.epicenter);
            printf("  hypo_coords: lat_ns=%u lat_deg=%u lat_min=%u lat_sec=%u lon_ew=%u lon_deg=%u lon_min=%u lon_sec=%u\n",
                   msg.mt43.hypo.coords.lat_ns, msg.mt43.hypo.coords.lat_deg, msg.mt43.hypo.coords.lat_min, msg.mt43.hypo.coords.lat_sec,
                   msg.mt43.hypo.coords.lon_ew, msg.mt43.hypo.coords.lon_deg, msg.mt43.hypo.coords.lon_min, msg.mt43.hypo.coords.lon_sec);
            break;
        case 3: // Seismic Intensity
            printf("  seis_count: %u\n", msg.mt43.seis.count);
            for (int i = 0; i < msg.mt43.seis.count; i++) {
                printf("    [%d] intensity_code=%u prefecture_code=%u\n",
                       i, msg.mt43.seis.entries[i].intensity_code, msg.mt43.seis.entries[i].prefecture_code);
            }
            break;
        case 5: // Tsunami
            printf("  tsunami_warning_code: %u\n", msg.mt43.tsunami.warning_code);
            printf("  tsunami_count: %u\n", msg.mt43.tsunami.count);
            for (int i = 0; i < msg.mt43.tsunami.count; i++) {
                printf("    [%d] region_code=%u height_code=%u arrival_time_raw=%u\n",
                       i, msg.mt43.tsunami.entries[i].region_code, msg.mt43.tsunami.entries[i].height_code,
                       msg.mt43.tsunami.entries[i].arrival_time_raw);
                printf("         arrival_time: day=%u hour=%u minute=%u\n",
                       msg.mt43.tsunami.entries[i].arrival_time.day, msg.mt43.tsunami.entries[i].arrival_time.hour,
                       msg.mt43.tsunami.entries[i].arrival_time.minute);
            }
            break;
        case 6: // NW Pacific Tsunami
            printf("  nw_pac_potential: %u\n", msg.mt43.nw_pac.potential);
            printf("  nw_pac_count: %u\n", msg.mt43.nw_pac.count);
            break;
        case 8: // Volcano
            printf("  vol_ambiguity: %u\n", msg.mt43.vol.ambiguity);
            printf("  vol_activity_time: day=%u hour=%u minute=%u\n",
                   msg.mt43.vol.activity_time.day, msg.mt43.vol.activity_time.hour, msg.mt43.vol.activity_time.minute);
            printf("  vol_warning_code: %u\n", msg.mt43.vol.warning_code);
            printf("  vol_volcano_name: %u\n", msg.mt43.vol.volcano_name);
            printf("  vol_lg_count: %u\n", msg.mt43.vol.lg_count);
            break;
        case 9: // Ash Fall
            printf("  ash_activity_time: day=%u hour=%u minute=%u\n",
                   msg.mt43.ash.activity_time.day, msg.mt43.ash.activity_time.hour, msg.mt43.ash.activity_time.minute);
            printf("  ash_warning_type: %u\n", msg.mt43.ash.warning_type);
            printf("  ash_volcano_name: %u\n", msg.mt43.ash.volcano_name);
            printf("  ash_count: %u\n", msg.mt43.ash.count);
            break;
        case 10: // Weather
            printf("  wx_warning_state: %u\n", msg.mt43.wx.warning_state);
            printf("  wx_count: %u\n", msg.mt43.wx.count);
            break;
        case 11: // Flood
            printf("  flood_count: %u\n", msg.mt43.flood.count);
            break;
        case 12: // Typhoon
            printf("  typh_reference_time: day=%u hour=%u minute=%u\n",
                   msg.mt43.typh.reference_time.day, msg.mt43.typh.reference_time.hour, msg.mt43.typh.reference_time.minute);
            printf("  typh_ref_type: %u\n", msg.mt43.typh.ref_type);
            printf("  typh_elapsed: %u\n", msg.mt43.typh.elapsed);
            printf("  typh_number: %u\n", msg.mt43.typh.number);
            printf("  typh_scale: %u\n", msg.mt43.typh.scale);
            printf("  typh_intensity: %u\n", msg.mt43.typh.intensity);
            break;
        case 14: // Marine
            printf("  marine_count: %u\n", msg.mt43.marine.count);
            break;
        default:
            printf("  Unknown disaster category\n");
    }
}

int main() {
    // EEW
    decode_and_print("EEW", "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F\r\n");

    // Seismic Intensity
    decode_and_print("Seismic Intensity", "$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB800000000000000011E027E5C*76\r\n");

    // Hypocenter
    decode_and_print("Hypocenter", "$QZQSM,58,9AAF919C82800388000039051440C5C82A010830000000000000012497DA18*0A\r\n");

    // Tsunami
    decode_and_print("Tsunami", "$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F\r\n");

    // NW Pacific Tsunami
    decode_and_print("NW Pacific Tsunami", "$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000118372EC8*0C\r\n");

    // Volcano
    decode_and_print("Volcano", "$QZQSM,58,C6AFC19CA50001CA5341F783E0F1091042123020000000000000011B086438*70\r\n");

    // Ash Fall
    decode_and_print("Ash Fall", "$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71\r\n");

    // Weather
    decode_and_print("Weather", "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73\r\n");

    // Flood
    decode_and_print("Flood", "$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E\r\n");

    return 0;
}
