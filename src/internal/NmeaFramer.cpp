// azaraC - src/internal/NmeaFramer.cpp

#include "NmeaFramer.h"
#include <cstring>

namespace azaraC {
namespace internal {

void NmeaFramer::reset() {
    _st  = St::WAIT;
    _pos = 0;
    _xsum = 0;
}

uint8_t NmeaFramer::hexVal(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return 0xFF;
}

bool NmeaFramer::feed(uint8_t b, Frame& out) {
    char c = static_cast<char>(b);
    if (c == '$') {
        _pos = 0; _xsum = 0; _st = St::COLLECT;
        return false;
    }

    switch (_st) {
    case St::WAIT:
        break;
    case St::COLLECT:
        if (c == '*') {
            _buf[_pos] = '\0';
            _st = St::CSUM1;
        } else if (c == '\r' || c == '\n') {
            reset();
        } else {
            if (_pos < sizeof(_buf) - 1) {
                _xsum ^= b;
                _buf[_pos++] = c;
            } else {
                reset();
            }
        }
        break;
    case St::CSUM1:
        _csumH = hexVal(c);
        _st = St::CSUM2;
        break;
    case St::CSUM2: {
        uint8_t recv = (_csumH << 4) | hexVal(c);
        _st = St::WAIT;
        if (recv != _xsum) return false;
        return parse(out);
    }
    }
    return false;
}

bool NmeaFramer::parse(Frame& out) {
    // Expected: QZQSM,<svid>,<hex-data>
    if (strncmp(_buf, "QZQSM,", 6) != 0) return false;

    // parse svid
    char* p = _buf + 6;
    uint16_t svid_tmp = 0;
    bool has_digit = false;
    while (*p && *p != ',') {
        if (*p >= '0' && *p <= '9') {
            svid_tmp = svid_tmp * 10 + (*p - '0');
            has_digit = true;
            if (svid_tmp > 255) return false;
        } else {
            return false; // Reject non-digit characters
        }
        p++;
    }
    if (!has_digit || *p != ',') return false;
    uint8_t svid = static_cast<uint8_t>(svid_tmp);
    ++p;  // skip comma

    // hex decode into bits[]
    memset(out.bits, 0, sizeof(out.bits));
    uint8_t byte_idx = 0;

    // Count hex characters — QZSS L1S is 250 bits = 63 hex chars (31 bytes + 1 nibble).
    // Per IS-QZSS-DCX-003, exactly 63 hex chars are expected.
    char* start_p = p;
    while ((*p >= '0' && *p <= '9') || (*p >= 'A' && *p <= 'F') || (*p >= 'a' && *p <= 'f')) p++;
    size_t hex_len = p - start_p;
    if (hex_len != 63) return false;

    p = start_p;
    // Decode full byte pairs
    size_t full_bytes = hex_len / 2;
    if (full_bytes > 32) full_bytes = 32;
    while (byte_idx < full_bytes) {
        uint8_t hi = hexVal(*p++);
        uint8_t lo = hexVal(*p++);
        if (hi == 0xFF || lo == 0xFF) return false;
        out.bits[byte_idx++] = (hi << 4) | lo;
    }
    // Handle trailing nibble (odd hex length, e.g. 63 chars)
    if ((hex_len & 1) && byte_idx < 32) {
        uint8_t hi = hexVal(*p++);
        if (hi == 0xFF) return false;
        out.bits[byte_idx++] = hi << 4;
    }
    if (byte_idx < 31) return false;  // Need at least 31 bytes for 250 bits

    out.svid   = svid;
    out.source = FrameSource::NMEA;
    return true;
}

} // namespace internal
} // namespace azaraC
