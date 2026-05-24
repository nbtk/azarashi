// azaraC - src/internal/JsonWriter.cpp
// Common JSON writer helpers for serializers

#include "JsonWriter.h"
#include <cstdio>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// Primitive writers
// ---------------------------------------------------------------------------
void writeChar(Print& out, char c) { out.print(c); }

void writeUint32(Print& out, uint32_t v) {
    char buf[11]; int8_t i = 10; buf[i] = '\0';
    if (v == 0) { out.print('0'); return; }
    while (v) { buf[--i] = '0' + (v % 10); v /= 10; }
    out.print(buf + i);
}

// Write double with fixed precision (for coordinates, distances)
void writeDouble(Print& out, double v, int precision) {
    if (v < 0) {
        out.print('-');
        v = -v;
    }

    // Add rounding offset based on precision
    double round_off = 0.5;
    for (int i = 0; i < precision; ++i) round_off /= 10.0;
    v += round_off;

    // Integer part
    int64_t int_part = (int64_t)v;
    writeUint32(out, (uint32_t)int_part);
    out.print('.');
    // Fractional part
    double frac = v - (double)int_part;
    for (int i = 0; i < precision; ++i) {
        frac *= 10.0;
        int digit = (int)frac;
        out.print(static_cast<char>('0' + digit));
        frac -= digit;
    }
}

void writeStr(Print& out, std::string_view s) {
    out.print('"'); if (!s.empty()) out.write(s.data(), s.size()); out.print('"');
}

void writeOptStr(Print& out, std::optional<std::string_view> s) {
    writeStr(out, s.value_or(""));
}

void writeHex(Print& out, uint8_t v) {
    char buf[5] = "\"00\"";
    const char hex[] = "0123456789ABCDEF";
    buf[1] = hex[v >> 4];
    buf[2] = hex[v & 0x0F];
    out.print(buf);
}

// key: "foo":
void wk(Print& out, std::string_view k) {
    writeChar(out, '"'); if (!k.empty()) out.write(k.data(), k.size()); out.print("\":");
}

// "key":value,
void wf_u(Print& out, std::string_view k, uint32_t v, bool last) {
    wk(out, k); writeUint32(out, v); if (!last) writeChar(out, ',');
}

void wf_d(Print& out, std::string_view k, double v, bool last) {
    wk(out, k); writeDouble(out, v); if (!last) writeChar(out, ',');
}

void wf_s(Print& out, std::string_view k, std::optional<std::string_view> v, bool last) {
    wk(out, k); writeOptStr(out, v); if (!last) writeChar(out, ',');
}

// ---------------------------------------------------------------------------
// Helpers for repeated structures
// ---------------------------------------------------------------------------

// Write a DHM TimeFields object as nested JSON
void writeDHM(Print& out, std::string_view key, const TimeFields& t, bool last) {
    wk(out, key);
    out.print('{');
    wf_u(out, "month", t.month);
    wf_u(out, "day",   t.day);
    wf_u(out, "hour",  t.hour);
    wf_u(out, "min",   t.minute);
    wf_u(out, "unix",  t.unix_time, /*last=*/true);
    out.print('}');
    if (!last) writeChar(out, ',');
}

void writeLatLon(Print& out, std::string_view key, const LatLon& ll, bool last) {
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
void writeArrivalTimeFields(Print& out, uint16_t raw) {
    wf_u(out, "arrival_day_offset", (raw >> 11) & 1u);
    wf_u(out, "arrival_hour",       (raw >>  6) & 0x1Fu);
    wf_u(out, "arrival_min",        raw & 0x3Fu);
}

} // namespace internal
} // namespace azaraC
