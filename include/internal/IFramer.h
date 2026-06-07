#pragma once
// azaraC - src/internal/IFramer.h

#include "Frame.h"

namespace azaraC {
namespace internal {

class IFramer {
public:
    virtual bool feed(uint8_t byte, Frame& out) = 0;
    virtual void reset() = 0;
    virtual ~IFramer() = default;
};

} // namespace internal
} // namespace azaraC
