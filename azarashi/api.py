import numbers
from collections.abc import Callable, Iterable
from decimal import Decimal
from datetime import datetime
from typing import Any, Literal, Protocol, TypeAlias, cast

from .streams import hex_qzss_dcr_message_extractor
from .streams import nmea_qzss_dcr_message_extractor
from .streams import l1s_qzss_dcr_message_extractor
from .streams import StreamKeyedDict
from .streams import stream_lock
from .streams import reader_lock as _reader_lock
from .streams.state import reset_partial_lines
from .streams.nmea import reset_pending_sentences
from .streams.ublox import buffers as _ublox_buffers
from .streams.l1s import archives as _l1s_archives
from .streams.l1s import buffers as _l1s_buffers
from .streams import ublox_qzss_dcr_message_extractor
from .decoders import hex as hex_decoder
from .decoders import net as net_decoder
from .decoders import nmea as nmea_decoder
from .decoders import l1s as l1s_decoder
from .decoders import ubx as ublox_decoder
from .exceptions import AzarashiArgumentTypeError
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiUnsupportedFormatError
from .reports import Report

#: the forms a stream can carry; 'spresense' is another name for 'nmea'
StreamFormat: TypeAlias = Literal['nmea', 'spresense', 'hex', 'ublox', 'l1s']
#: the forms decode() takes one message in: 'net' carries one datagram, not a stream, and a record
#: of 'l1s' means nothing without the archive's PRN, which only its stream gives
MessageFormat: TypeAlias = Literal['nmea', 'spresense', 'hex', 'ublox', 'net']


class SupportsReadline(Protocol):
    """A stream of lines, for 'nmea', 'spresense' and 'hex': a text or binary file, pySerial, ..."""

    def readline(self) -> str | bytes: ...


class SupportsRead1(Protocol):
    """A buffered binary stream, for 'ublox' and 'l1s'."""

    def read1(self) -> bytes: ...


class SupportsRead(Protocol):
    """A binary stream that is read one byte at a time, for 'ublox' and 'l1s': pySerial, an unbuffered file, ..."""

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


def _check_format(msg_type: object, formats: tuple[str, ...]) -> None:
    if not isinstance(msg_type, str):
        raise AzarashiArgumentTypeError(f'msg_type must be a str, not {type(msg_type).__name__}')
    if msg_type not in formats:
        raise AzarashiUnsupportedFormatError(f'Unknown Message Type: {msg_type}')


def _check_message(msg: object) -> None:
    if not isinstance(msg, (str, bytes, bytearray)):
        raise AzarashiArgumentTypeError(f'msg must be str or bytes, not {type(msg).__name__}')


def _check_timestamp(timestamp: object) -> None:
    if timestamp is not None and not isinstance(timestamp, datetime):
        raise AzarashiArgumentTypeError(f'timestamp must be a datetime, not {type(timestamp).__name__}')


def _check_callback(callback: object, callback_args: object, callback_kwargs: object) -> None:
    if callback is not None and not callable(callback):
        raise AzarashiArgumentTypeError(f'callback must be callable, not {type(callback).__name__}')
    try:
        iter(cast(Iterable[Any], callback_args))  # without taking anything from it
    except TypeError:
        raise AzarashiArgumentTypeError(
            f'callback_args must be a sequence, not {type(callback_args).__name__}') from None
    if callback_kwargs is None:
        return
    keys = getattr(callback_kwargs, 'keys', None)  # what ** takes a mapping by
    if not callable(keys) or not all(isinstance(key, str) for key in cast(Iterable[object], keys())):
        raise AzarashiArgumentTypeError(
            f'callback_kwargs must map names to values, not {type(callback_kwargs).__name__}')


def _check_unique(unique: object) -> None:
    if unique is not None and not isinstance(unique, (numbers.Real, Decimal)):  # a bool is a number too
        raise AzarashiArgumentTypeError(
            f'unique must be a truth value or a number of seconds, not {type(unique).__name__}')


def decode(msg: str | bytes, msg_type: MessageFormat = 'nmea', timestamp: datetime | None = None) -> Report:
    _check_message(msg)
    if cast(str, msg_type) == 'l1s':  # the annotation leaves l1s out, and a caller may still pass it
        raise AzarashiUnsupportedFormatError(
            'Message Type l1s is read as a stream, which gives the PRN; use decode_stream()')
    _check_format(msg_type, ('nmea', 'spresense', 'hex', 'ublox', 'net'))
    _check_timestamp(timestamp)
    return _decode(msg, msg_type, timestamp)


def _decode(msg: str | bytes, msg_type: str, timestamp: datetime | None) -> Report:
    if not msg:
        raise AzarashiInvalidMessageError('Empty Message')

    if msg_type == 'hex':
        return hex_decoder.Decoder(msg, timestamp=timestamp).decode()
    if msg_type == 'net':
        return net_decoder.Decoder(msg, timestamp=timestamp).decode()
    if msg_type == 'nmea' or msg_type == 'spresense':
        return nmea_decoder.Decoder(msg, timestamp=timestamp).decode()
    if msg_type == 'l1s':
        return l1s_decoder.Decoder(msg, timestamp=timestamp).decode()
    return ublox_decoder.Decoder(msg, timestamp=timestamp).decode()


def _select_reader(stream: QzssDcrStream, msg_type: str) -> tuple[
        Callable[..., str | bytes], Callable[..., Any], tuple[Any, ...]]:
    extractor: Callable[..., str | bytes]
    reader: Callable[..., Any]
    reader_args: tuple[Any, ...]
    if msg_type == 'net':
        raise AzarashiUnsupportedFormatError(
            "Message Type net is not a stream format; use decode(data, 'net') for each datagram")
    _check_format(msg_type, ('nmea', 'spresense', 'hex', 'ublox', 'l1s'))
    if msg_type in ('hex', 'nmea', 'spresense'):
        if not callable(readline := getattr(stream, 'readline', None)):
            raise AzarashiArgumentTypeError(f'readline() does not exist: {type(stream)}')
        extractor = hex_qzss_dcr_message_extractor if msg_type == 'hex' else nmea_qzss_dcr_message_extractor
        reader = readline
        reader_args = ()
    else:  # ublox, l1s: binary streams
        extractor = l1s_qzss_dcr_message_extractor if msg_type == 'l1s' else ublox_qzss_dcr_message_extractor
        if callable(read1 := getattr(stream, 'read1', None)):
            reader = read1
            reader_args = ()
        elif callable(buffer_read1 := getattr(getattr(stream, 'buffer', None), 'read1', None)):
            reader = buffer_read1
            reader_args = ()
        elif callable(read := getattr(stream, 'read', None)):
            reader = read
            reader_args = (1,)  # positional: raw streams (io.FileIO, SocketIO) reject read(size=1)
        else:
            raise AzarashiArgumentTypeError(f'Neither read() nor read1() exists: {type(stream)}')

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
        _l1s_buffers.discard(reader)
        _l1s_archives.discard(reader)  # reading again starts from the archive's PRN


def decode_stream(stream: QzssDcrStream,
                  msg_type: StreamFormat = 'nmea',
                  callback: Callable[..., object] | None = None,
                  callback_args: tuple[Any, ...] = (),
                  callback_kwargs: dict[str, Any] | None = None,
                  unique: bool | float = False,
                  ignore_dcr: bool = False,
                  ignore_dcx: bool = True,
                  timestamp: datetime | None = None) -> Report:
    # the call is checked in full before anything is read
    extractor, reader, reader_args = _select_reader(stream, msg_type)
    _check_callback(callback, callback_args, callback_kwargs)
    _check_unique(unique)
    _check_timestamp(timestamp)
    if msg_type == 'l1s' and timestamp is not None:
        raise AzarashiUnsupportedFormatError(
            'Message Type l1s gives the time of every message; do not give a timestamp')
    if callback_kwargs is None:
        callback_kwargs = {}

    lock = stream_lock(stream)
    reading_lock = _reader_lock(reader)
    while True:
        with lock:  # the state of a stream belongs to one thread at a time, message by message
            with reading_lock:  # shared buffers must yield one complete frame at a time
                msg = extractor(reader, reader_args=reader_args)
            report = _decode(msg, msg_type, timestamp)

            if report.message_type == 'DCR':
                if ignore_dcr:
                    continue
            elif report.message_type == 'DCX':
                if ignore_dcx:
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
