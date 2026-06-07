#pragma once
// azaraC - src/internal/Frame.h

#include <cstdint>

namespace azaraC {
namespace internal {

enum class FrameSource : uint8_t { UBX = 0, NMEA = 1 };

struct Frame {
    uint8_t     svid;       // QZSS svId (UBX) or PRN-offset
    uint8_t     bits[32];   // 250 bits MSB-first; bits[31] lower 6 = padding zeros
    FrameSource source;
};

} // namespace internal
} // namespace azaraC
