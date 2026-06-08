// azaraC - src/internal/Dedup.cpp

#include "internal/Dedup.h"

namespace azaraC {
namespace internal {

bool DedupFilter::isDuplicate(const DedupKey& key) {
    uint16_t limit = _full ? AZARAC_DEDUP_SLOTS : _head;
    for (uint16_t i = 0; i < limit; ++i) {
        const DedupKey& s = _ring[i];
        if (s.svid == key.svid &&
            s.msg_type == key.msg_type &&
            s.crc24 == key.crc24) {
            return true;
        }
    }
    _ring[_head] = key;
    _head = (_head + 1) % AZARAC_DEDUP_SLOTS;
    if (_head == 0) _full = true;
    return false;
}

void DedupFilter::reset() {
    _head = 0;
    _full = false;
}

} // namespace internal
} // namespace azaraC
