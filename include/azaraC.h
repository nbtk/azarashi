#pragma once
// azaraC — QZSS L1S DCX/CAMF + QZQSM decoder for Arduino
//
// Usage:
//   #include <azaraC.h>
//
// Optional compile-time overrides (define BEFORE this include):
//   #define AZARAC_DEDUP_SLOTS 16   // default: 8
//   #define AZARAC_LANG_JA 1        // Enable Japanese labels (default: 1)
//   #define AZARAC_LANG_EN 0        // Enable English labels (default: 0)

// ---- language selection macros -----------------------------------------------
#ifndef AZARAC_LANG_JA
#define AZARAC_LANG_JA 1
#endif

#ifndef AZARAC_LANG_EN
#define AZARAC_LANG_EN 0
#endif

#include "Message.h"
#include "Parser.h"
#include "internal/JsonSerializer.h"

#if defined(ARDUINO) && ARDUINO >= 1
#  include <Print.h>
#endif

#if __cplusplus < 201703L
#error "This tool requires C++17 or later"
#endif

namespace azaraC {

// Convenience wrapper: serialize msg as JSON to any Print& (Serial, WiFiClient, etc.)
inline void toJson(const Message& msg, Print& out) {
    internal::JsonSerializer::serialize(msg, out);
}

} // namespace azaraC
