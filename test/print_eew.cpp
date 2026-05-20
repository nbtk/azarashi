// print_eew.cpp — EEWデコード結果の出力
#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/Decoder.h"
#include <cstdio>

using namespace azaraC;
using namespace azaraC::internal;

int main() {
    const char* nmea = "$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F\r\n";

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
        return 1;
    }

    Decoder dec;
    Message msg{};
    bool ok = dec.decode(frame, msg, 1704067200u); // 2024-01-01 00:00:00 UTC

    if (!ok) {
        printf("Decode failed\n");
        return 1;
    }

    printf("EEW Decoded Fields:\n");
    printf("  msg_type: %u\n", msg.msg_type);
    printf("  disaster_category: %u\n", msg.disaster_category);
    printf("  eew_long_period_lower: %u\n", msg.eew_long_period_lower);
    printf("  eew_long_period_upper: %u\n", msg.eew_long_period_upper);
    printf("  eew_notification_count: %u\n", msg.eew_notification_count);
    {
        const int notification_cap = sizeof(msg.eew_notification) / sizeof(msg.eew_notification[0]);
        int notification_count = msg.eew_notification_count;
        if (notification_count > notification_cap) {
            fprintf(stderr, "  WARNING: eew_notification_count (%u) exceeds capacity (%d), clamping\n", msg.eew_notification_count, notification_cap);
            notification_count = notification_cap;
        }
        for (int i = 0; i < notification_count; i++) {
            printf("    notification[%d]: %u\n", i, msg.eew_notification[i]);
        }
    }
    printf("  eew_quake_time: day=%u hour=%u minute=%u unix=%u\n",
           msg.eew_quake_time.day, msg.eew_quake_time.hour,
           msg.eew_quake_time.minute, msg.eew_quake_time.unix_time);
    printf("  eew_depth: %u\n", msg.eew_depth);
    printf("  eew_magnitude: %u\n", msg.eew_magnitude);
    printf("  eew_epicenter: %u\n", msg.eew_epicenter);
    printf("  eew_intensity_lower: %u\n", msg.eew_intensity_lower);
    printf("  eew_intensity_upper: %u\n", msg.eew_intensity_upper);
    printf("  eew_region_count: %u\n", msg.eew_region_count);
    {
        const int region_cap = sizeof(msg.eew_regions) / sizeof(msg.eew_regions[0]);
        int region_count = msg.eew_region_count;
        if (region_count > region_cap) {
            fprintf(stderr, "  WARNING: eew_region_count (%u) exceeds capacity (%d), clamping\n", msg.eew_region_count, region_cap);
            region_count = region_cap;
        }
        for (int i = 0; i < region_count; i++) {
            printf("    region[%d]: %u\n", i, msg.eew_regions[i]);
        }
    }

    return 0;
}
