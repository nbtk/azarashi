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
    switch (_st) {
    case St::WAIT:
        if (c == '$') { _pos = 0; _xsum = 0; _st = St::COLLECT; }
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
    uint8_t svid = 0;
    while (*p && *p != ',') {
        if (*p >= '0' && *p <= '9') {
            svid = svid * 10 + (*p - '0');
        }
        p++;
    }
    if (*p != ',') return false;
    ++p;  // skip comma

    // hex decode into bits[]
    memset(out.bits, 0, sizeof(out.bits));
    uint8_t byte_idx = 0;

    // Ensure hex string length is even and at least 64 chars (32 bytes)
    const char* start_p = p;
    while ((*p >= '0' && *p <= '9') || (*p >= 'A' && *p <= 'F') || (*p >= 'a' && *p <= 'f')) p++;
    size_t hex_len = p - start_p;
    if (hex_len % 2 != 0 || hex_len < 64) return false;

    p = start_p;
    while (byte_idx < 32) {
        uint8_t hi = hexVal(*p++);
        uint8_t lo = hexVal(*p++);
        if (hi == 0xFF || lo == 0xFF) return false;
        out.bits[byte_idx++] = (hi << 4) | lo;
    }
    if (byte_idx < 32) return false;

    out.svid   = svid;
    out.source = FrameSource::NMEA;
    return true;
}

} // namespace internal
} // namespace azaraC
