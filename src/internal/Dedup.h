#pragma once
// azaraC - src/internal/Dedup.h
// Ring-buffer duplicate suppression.
// A message is considered duplicate when {svid, msg_type, crc24} matches
// any slot in the ring.

#include <cstdint>

#ifndef AZARAC_DEDUP_SLOTS
#define AZARAC_DEDUP_SLOTS 32
#endif

namespace azaraC {
namespace internal {

struct DedupKey {
    uint8_t  svid;
    uint8_t  msg_type;
    uint32_t crc24;
};

class DedupFilter {
public:
    // Returns true if key is a duplicate (already seen).
    // If not duplicate, stores key and returns false.
    bool isDuplicate(const DedupKey& key);
    void reset();

private:
    DedupKey _ring[AZARAC_DEDUP_SLOTS] = {};
    uint8_t  _head = 0;
    bool     _full = false;
};

} // namespace internal
} // namespace azaraC
