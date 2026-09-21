from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal, Protocol, TypeAlias

from .streams import hex_qzss_dcr_message_extractor
from .streams import nmea_qzss_dcr_message_extractor
from .streams import StreamKeyedDict
from .streams import stream_lock
from .streams import reader_lock as _reader_lock
from .streams.state import reset_partial_lines
from .streams.nmea import reset_pending_sentences
from .streams.ublox import buffers as _ublox_buffers
from .streams import ublox_qzss_dcr_message_extractor
from .decoders import hex as hex_decoder
from .decoders import net as net_decoder
from .decoders import nmea as nmea_decoder
from .decoders import ubx as ublox_decoder
from .exceptions import AzarashiInvalidMessageError
from .reports import Report

#: the forms a stream can carry; 'spresense' is another name for 'nmea'
StreamFormat: TypeAlias = Literal['nmea', 'spresense', 'hex', 'ublox']
MessageFormat: TypeAlias = StreamFormat | Literal['net']  # 'net' carries one datagram, not a stream


class SupportsReadline(Protocol):
    """A stream of lines, for 'nmea', 'spresense' and 'hex': a text or binary file, pySerial, ..."""

    def readline(self) -> str | bytes: ...


class SupportsRead1(Protocol):
    """A buffered binary stream, for 'ublox'."""

    def read1(self) -> bytes: ...


class SupportsRead(Protocol):
    """A binary stream that is read one byte at a time, for 'ublox': pySerial, an unbuffered file, ..."""

    def read(self, size: int, /) -> bytes | None: ...


QzssDcrStream: TypeAlias = SupportsReadline | SupportsRead1 | SupportsRead  # what decode_stream() reads

_ReportKey: TypeAlias = tuple[type[Report], bytes]
caches: StreamKeyedDict[dict[_ReportKey, datetime]] = StreamKeyedDict()
deliveries: StreamKeyedDict[set[_ReportKey]] = StreamKeyedDict()
cache_size = 256


def _cached(cache: dict[_ReportKey, datetime], key: _ReportKey, received: datetime) -> dict[_ReportKey, datetime]:
    updated = {k: stamp for k, stamp in cache.items() if k != key}
    updated[key] = received
    return dict(list(updated.items())[-cache_size:])


def decode(msg: str | bytes, msg_type: MessageFormat = 'nmea', timestamp: datetime | None = None) -> Report:
    if not msg:
        raise AzarashiInvalidMessageError('Empty Message')

    if msg_type == 'hex':
        return hex_decoder.Decoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'net':
        return net_decoder.Decoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'nmea' or msg_type == 'spresense':
        return nmea_decoder.Decoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'ublox':
        return ublox_decoder.Decoder(msg, timestamp=timestamp).decode()
    else:
        raise AzarashiInvalidMessageError(f'Unknown Message Type: {msg_type}')


def _select_reader(stream: QzssDcrStream, msg_type: str) -> tuple[
        Callable[..., str | bytes], Callable[..., Any], tuple[Any, ...]]:
    extractor: Callable[..., str | bytes]
    reader: Callable[..., Any]
    reader_args: tuple[Any, ...]
    if msg_type in ('hex', 'nmea', 'spresense'):
        if not callable(readline := getattr(stream, 'readline', None)):
            raise AzarashiInvalidMessageError(f'readline() does not exist: {type(stream)}')
        extractor = hex_qzss_dcr_message_extractor if msg_type == 'hex' else nmea_qzss_dcr_message_extractor
        reader = readline
        reader_args = ()
    elif msg_type == 'ublox':
        if callable(read1 := getattr(stream, 'read1', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = read1
            reader_args = ()
        elif callable(buffer_read1 := getattr(getattr(stream, 'buffer', None), 'read1', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = buffer_read1
            reader_args = ()
        elif callable(read := getattr(stream, 'read', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = read
            reader_args = (1,)  # positional: raw streams (io.FileIO, SocketIO) reject read(size=1)
        else:
            raise AzarashiInvalidMessageError(f'Neither read() nor read1() exists: {type(stream)}')
    elif msg_type == 'net':
        raise AzarashiInvalidMessageError(
            "Message Type net is not a stream format; use decode(data, 'net') for each datagram")
    else:
        raise AzarashiInvalidMessageError(f'Unknown Message Type: {msg_type}')

    return extractor, reader, reader_args


def reset_reading_state(stream: QzssDcrStream, msg_type: StreamFormat = 'nmea') -> None:
    """Discard this reader owner's partial and pending data, keeping duplicate history.

    Stop all reads and callbacks sharing the owner before calling. This neither cancels
    an active read nor changes the underlying I/O buffers, position or open/closed state.
    """
    _, reader, _ = _select_reader(stream, msg_type)
    with stream_lock(stream), _reader_lock(reader):
        reset_partial_lines(reader)
        reset_pending_sentences(reader)
        _ublox_buffers.discard(reader)


def decode_stream(stream: QzssDcrStream,
                  msg_type: StreamFormat = 'nmea',
                  callback: Callable[..., object] | None = None,
                  callback_args: tuple[Any, ...] = (),
                  callback_kwargs: dict[str, Any] | None = None,
                  unique: bool | float = False,
                  ignore_dcr: bool = False,
                  ignore_dcx: bool = True,
                  timestamp: datetime | None = None) -> Report:
    if callback_kwargs is None:
        callback_kwargs = {}

    extractor, reader, reader_args = _select_reader(stream, msg_type)

    lock = stream_lock(stream)
    reading_lock = _reader_lock(reader)
    while True:
        with lock:  # the state of a stream belongs to one thread at a time, message by message
            with reading_lock:  # shared buffers must yield one complete frame at a time
                msg = extractor(reader, reader_args=reader_args)
            report = decode(msg, msg_type, timestamp)

            if report.message_type == 'DCR':
                if ignore_dcr is True:
                    continue
            elif report.message_type == 'DCX':
                if ignore_dcx is True:
                    continue
            else:  # unknown message type
                continue

            key = (type(report), report.raw)
            received = report.timestamp
            if unique:
                cache = caches.get(stream) or {}
                if key in (deliveries.get(stream) or set()):  # another thread is delivering this report now
                    continue
                if key in cache:
                    if unique is True:  # never expire: always suppress duplicates
                        fire = False
                    else:  # unique is a number of seconds: re-fire once the cached copy is stale
                        freshness = (received - cache[key]).total_seconds()
                        fire = freshness > unique
                else:
                    fire = True

                if fire is False:
                    caches[stream] = _cached(cache, key, received)
                    continue

                deliveries[stream] = (deliveries.get(stream) or set()) | {key}

        try:  # the callback runs without the lock, so it cannot block or deadlock the other readers
            if callback is not None:
                callback(report, *callback_args, **callback_kwargs)
        except BaseException:
            if unique:  # only a delivered report counts as seen, so a failed callback gets the next copy
                with lock:
                    deliveries[stream] = (deliveries.get(stream) or set()) - {key}
            raise

        if unique:
            with lock:
                caches[stream] = _cached(caches.get(stream) or {}, key, received)
                deliveries[stream] = (deliveries.get(stream) or set()) - {key}
        if callback is None:
            return report
