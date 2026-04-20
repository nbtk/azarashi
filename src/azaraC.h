#pragma once
// azaraC — QZSS L1S DCX/CAMF + QZQSM decoder for Arduino
//
// Usage:
//   #include <azaraC.h>
//
// Optional compile-time overrides (define BEFORE this include):
//   #define AZARAC_DEDUP_SLOTS 16   // default: 8

#include "Message.h"
#include "Parser.h"
#include "internal/JsonSerializer.h"

#if defined(ARDUINO) && ARDUINO >= 1
#  include <Print.h>
#endif

namespace azaraC {

// Convenience wrapper: serialize msg as JSON to any Print& (Serial, WiFiClient, etc.)
inline void toJson(const Message& msg, Print& out) {
    internal::JsonSerializer::serialize(msg, out);
}

} // namespace azaraC
