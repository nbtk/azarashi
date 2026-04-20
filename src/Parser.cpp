// azaraC - src/Parser.cpp

#include "Parser.h"

namespace azaraC {

bool Parser::feed(uint8_t byte, Message& out, uint32_t now_unix) {
    Frame frame;

    // --- カスタムフレーマ（排他モード）---
    if (_custom) {
        if (!_custom->feed(byte, frame)) return false;
        // カスタムフレーマ成功時は重複チェックとデコードのみ
        internal::DedupKey key{ frame.svid, 0, 0 };
        // CRC はデコード前に不明なので一時的に 0; decode 後に正式キーを作る
        if (!_decoder.decode(frame, out, now_unix)) return false;
        key.msg_type = out.msg_type;
        key.crc24    = out.crc24;
        if (_dedup.isDuplicate(key)) return false;
        return true;
    }

    // --- AUTO モード: UBX / NMEA を並行試行 ---
    bool ubx_ok  = false;
    bool nmea_ok = false;

    switch (_mode) {
    case Mode::UBX:
        ubx_ok = _ubx.feed(byte, frame);
        break;
    case Mode::NMEA:
        nmea_ok = _nmea.feed(byte, frame);
        break;
    case Mode::AUTO:
    default:
        ubx_ok  = _ubx.feed(byte, frame);
        if (!ubx_ok) nmea_ok = _nmea.feed(byte, frame);
        break;
    }

    if (!ubx_ok && !nmea_ok) return false;

    // フレームが取れたらデコード
    if (!_decoder.decode(frame, out, now_unix)) return false;

    // 重複チェック
    internal::DedupKey key{ out.svid, out.msg_type, out.crc24 };
    if (_dedup.isDuplicate(key)) return false;

    return true;
}

void Parser::reset() {
    _ubx.reset();
    _nmea.reset();
    if (_custom) _custom->reset();
    _dedup.reset();
    _mode = Mode::AUTO;
}

} // namespace azaraC
