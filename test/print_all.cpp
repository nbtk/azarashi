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
    bool ok = dec.decode(frame, msg, 1704067200u);
    
    if (!ok) {
        printf("Decode failed\n");
        return;
    }
    
    printf("msg_type: %u, disaster_category: %u\n", msg.msg_type, msg.disaster_category);
    
    switch (msg.disaster_category) {
        case 1: // EEW
            printf("  eew_long_period_lower: %u\n", msg.eew_long_period_lower);
            printf("  eew_long_period_upper: %u\n", msg.eew_long_period_upper);
            printf("  eew_notification_count: %u\n", msg.eew_notification_count);
            printf("  eew_quake_time: day=%u hour=%u minute=%u\n", 
                   msg.eew_quake_time.day, msg.eew_quake_time.hour, msg.eew_quake_time.minute);
            printf("  eew_depth: %u\n", msg.eew_depth);
            printf("  eew_magnitude: %u\n", msg.eew_magnitude);
            printf("  eew_epicenter: %u\n", msg.eew_epicenter);
            printf("  eew_intensity_lower: %u\n", msg.eew_intensity_lower);
            printf("  eew_intensity_upper: %u\n", msg.eew_intensity_upper);
            printf("  eew_region_count: %u\n", msg.eew_region_count);
            break;
        case 2: // Hypocenter
            printf("  hypo_notification_count: %u\n", msg.hypo_notification_count);
            printf("  hypo_quake_time: day=%u hour=%u minute=%u\n",
                   msg.hypo_quake_time.day, msg.hypo_quake_time.hour, msg.hypo_quake_time.minute);
            printf("  hypo_depth: %u\n", msg.hypo_depth);
            printf("  hypo_magnitude: %u\n", msg.hypo_magnitude);
            printf("  hypo_epicenter: %u\n", msg.hypo_epicenter);
            printf("  hypo_coords: lat_ns=%u lat_deg=%u lat_min=%u lat_sec=%u lon_ew=%u lon_deg=%u lon_min=%u lon_sec=%u\n",
                   msg.hypo_coords.lat_ns, msg.hypo_coords.lat_deg, msg.hypo_coords.lat_min, msg.hypo_coords.lat_sec,
                   msg.hypo_coords.lon_ew, msg.hypo_coords.lon_deg, msg.hypo_coords.lon_min, msg.hypo_coords.lon_sec);
            break;
        case 3: // Seismic Intensity
            printf("  seis_count: %u\n", msg.seis_count);
            for (int i = 0; i < msg.seis_count; i++) {
                printf("    [%d] intensity_code=%u prefecture_code=%u\n",
                       i, msg.seis_entries[i].intensity_code, msg.seis_entries[i].prefecture_code);
            }
            break;
        case 5: // Tsunami
            printf("  tsunami_warning_code: %u\n", msg.tsunami_warning_code);
            printf("  tsunami_count: %u\n", msg.tsunami_count);
            for (int i = 0; i < msg.tsunami_count; i++) {
                printf("    [%d] region_code=%u height_code=%u arrival_time_raw=%u\n",
                       i, msg.tsunamis[i].region_code, msg.tsunamis[i].height_code,
                       msg.tsunamis[i].arrival_time_raw);
                printf("         arrival_time: day=%u hour=%u minute=%u\n",
                       msg.tsunamis[i].arrival_time.day, msg.tsunamis[i].arrival_time.hour,
                       msg.tsunamis[i].arrival_time.minute);
            }
            break;
        case 6: // NW Pacific Tsunami
            printf("  nw_pac_potential: %u\n", msg.nw_pac_potential);
            printf("  nw_pac_count: %u\n", msg.nw_pac_count);
            break;
        case 8: // Volcano
            printf("  vol_ambiguity: %u\n", msg.vol_ambiguity);
            printf("  vol_activity_time: day=%u hour=%u minute=%u\n",
                   msg.vol_activity_time.day, msg.vol_activity_time.hour, msg.vol_activity_time.minute);
            printf("  vol_warning_code: %u\n", msg.vol_warning_code);
            printf("  vol_volcano_name: %u\n", msg.vol_volcano_name);
            printf("  vol_lg_count: %u\n", msg.vol_lg_count);
            break;
        case 9: // Ash Fall
            printf("  ash_activity_time: day=%u hour=%u minute=%u\n",
                   msg.ash_activity_time.day, msg.ash_activity_time.hour, msg.ash_activity_time.minute);
            printf("  ash_warning_type: %u\n", msg.ash_warning_type);
            printf("  ash_volcano_name: %u\n", msg.ash_volcano_name);
            printf("  ash_count: %u\n", msg.ash_count);
            break;
        case 10: // Weather
            printf("  wx_warning_state: %u\n", msg.wx_warning_state);
            printf("  wx_count: %u\n", msg.wx_count);
            break;
        case 11: // Flood
            printf("  flood_count: %u\n", msg.flood_count);
            break;
        case 12: // Typhoon
            printf("  typh_reference_time: day=%u hour=%u minute=%u\n",
                   msg.typh_reference_time.day, msg.typh_reference_time.hour, msg.typh_reference_time.minute);
            printf("  typh_ref_type: %u\n", msg.typh_ref_type);
            printf("  typh_elapsed: %u\n", msg.typh_elapsed);
            printf("  typh_number: %u\n", msg.typh_number);
            printf("  typh_scale: %u\n", msg.typh_scale);
            printf("  typh_intensity: %u\n", msg.typh_intensity);
            printf("  typh_pos_count: %u\n", msg.typh_pos_count);
            break;
        case 14: // Marine
            printf("  marine_count: %u\n", msg.marine_count);
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
