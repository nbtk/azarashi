#pragma once
// azaraC - src/internal/TimeFields.h
// Platform-independent time utility

#include <cstdint>

#if defined(ARDUINO) && ARDUINO >= 1
#  include <Arduino.h>
#else
#  include <chrono>
#endif

namespace azaraC {
namespace internal {

// Get current time in milliseconds
// Uses millis() on Arduino, std::chrono::steady_clock otherwise
//
// NOTE on wraparound (non-ARDUINO path): the raw millisecond count from
// std::chrono::steady_clock is cast to uint32_t. This causes the returned
// value to wrap around approximately every 49.7 days (2^32 ms), matching
// the behavior of Arduino::millis(). This wraparound is intentional.
// Callers MUST perform timeout checks using unsigned arithmetic, e.g.:
//     (current - start) < timeout
// to handle rollovers safely.
static inline uint32_t getMillis() {
#if defined(ARDUINO) && ARDUINO >= 1
    return millis();
#else
    auto now = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count();
    return static_cast<uint32_t>(ms);
#endif
}

} // namespace internal
} // namespace azaraC
