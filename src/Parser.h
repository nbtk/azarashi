#pragma once
// azaraC - src/Parser.h

#include "Message.h"
#include "internal/IFramer.h"
#include "internal/UbxFramer.h"
#include "internal/NmeaFramer.h"
#include "internal/Decoder.h"
#include "internal/Dedup.h"

namespace azaraC {

class Parser {
public:
    Parser() = default;
    // Custom framer (e.g. Sony, Furuno) — caller owns the object
    explicit Parser(internal::IFramer& framer) : _custom(&framer) {}

    // Feed one byte. Returns true when a new, non-duplicate, valid message is in `out`.
    // now_unix: current UNIX epoch (0 = skip absolute time resolution)
    bool feed(uint8_t byte, Message& out, uint32_t now_unix = 0);

    void reset();

private:
    internal::UbxFramer   _ubx;
    internal::NmeaFramer  _nmea;
    internal::Decoder     _decoder;
    internal::DedupFilter _dedup;
    internal::IFramer*    _custom = nullptr;

    enum class Mode : uint8_t { AUTO, UBX, NMEA, CUSTOM };
    Mode _mode = Mode::AUTO;
};

} // namespace azaraC
