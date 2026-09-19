from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal, Protocol, TypeAlias

from .hex_interface import hex_qzss_dcr_message_extractor
from .nmea_interface import nmea_qzss_dcr_message_extractor
from .stream_state import StreamKeyedDict
from .stream_state import stream_lock
from .ublox_interface import ublox_qzss_dcr_message_extractor
from ..decoders import HexQzssDcrDecoder
from ..decoders import NetQzssDcrDecoder
from ..decoders import NmeaQzssDcrDecoder
from ..decoders import UBloxQzssDcrDecoder
from ..exceptions import AzarashiInvalidMessageError
from ..reports import QzssDcReport

#: the forms a message can arrive in; 'spresense' is another name for 'nmea'
MessageFormat: TypeAlias = Literal['nmea', 'spresense', 'hex', 'ublox', 'net']


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

caches: StreamKeyedDict[list[QzssDcReport]] = StreamKeyedDict()  # stream -> recent reports, released with the stream
deliveries: StreamKeyedDict[list[QzssDcReport]] = StreamKeyedDict()  # stream -> reports handed to a callback right now
cache_size = 256


def _cached(cache: list[QzssDcReport], report: QzssDcReport) -> list[QzssDcReport]:
    return ([r for r in cache if r != report] + [report])[-cache_size:]  # the newest copy, at the newest end


def _dropped(reports: list[QzssDcReport], report: QzssDcReport) -> list[QzssDcReport]:
    return [r for r in reports if r != report]


def decode(msg: str | bytes, msg_type: MessageFormat = 'nmea', timestamp: datetime | None = None) -> QzssDcReport:
    if not msg:
        raise EOFError('Encountered EOF')

    if msg_type == 'hex':
        return HexQzssDcrDecoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'net':
        return NetQzssDcrDecoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'nmea' or msg_type == 'spresense':
        return NmeaQzssDcrDecoder(msg, timestamp=timestamp).decode()
    elif msg_type == 'ublox':
        return UBloxQzssDcrDecoder(msg, timestamp=timestamp).decode()
    else:
        raise AzarashiInvalidMessageError(f'Unknown Message Type: {msg_type}')


def decode_stream(stream: QzssDcrStream,
                  msg_type: MessageFormat = 'nmea',
                  callback: Callable[..., object] | None = None,
                  callback_args: tuple[Any, ...] = (),
                  callback_kwargs: dict[str, Any] | None = None,
                  unique: bool | float = False,
                  ignore_dcr: bool = False,
                  ignore_dcx: bool = True,
                  timestamp: datetime | None = None) -> QzssDcReport:
    if callback_kwargs is None:
        callback_kwargs = {}

    extractor: Callable[..., str | bytes]
    reader: Callable[..., Any]
    reader_args: tuple[Any, ...]
    if msg_type == 'hex':
        if callable(readline := getattr(stream, 'readline', None)):
            extractor = hex_qzss_dcr_message_extractor
            reader = readline
            reader_args = ()
        else:
            raise AzarashiInvalidMessageError(f'readline() does not exist: {type(stream)}')
    elif msg_type == 'nmea' or msg_type == 'spresense':
        if callable(readline := getattr(stream, 'readline', None)):
            extractor = nmea_qzss_dcr_message_extractor
            reader = readline
            reader_args = ()
        else:
            raise AzarashiInvalidMessageError(f'readline() does not exist: {type(stream)}')
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
    else:
        raise AzarashiInvalidMessageError(f'Unknown Message Type: {msg_type}')

    lock = stream_lock(stream)
    while True:
        with lock:  # the state of a stream belongs to one thread at a time, message by message
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

            if unique:
                cache = caches.get(stream) or []
                if report in (deliveries.get(stream) or []):  # another thread is delivering this report now
                    continue
                if report in cache:
                    if unique is True:  # never expire: always suppress duplicates
                        fire = False
                    else:  # unique is a number of seconds: re-fire once the cached copy is stale
                        cached = cache[cache.index(report)]
                        freshness = (report.timestamp - cached.timestamp).total_seconds()
                        fire = freshness > unique
                else:
                    fire = True

                if fire is False:
                    caches[stream] = _cached(cache, report)
                    continue

                deliveries[stream] = (deliveries.get(stream) or []) + [report]

        try:  # the callback runs without the lock, so it cannot block or deadlock the other readers
            if callback is not None:
                callback(report, *callback_args, **callback_kwargs)
        except BaseException:
            if unique:  # only a delivered report counts as seen, so a failed callback gets the next copy
                with lock:
                    deliveries[stream] = _dropped(deliveries.get(stream) or [], report)
            raise

        if unique:
            with lock:
                caches[stream] = _cached(caches.get(stream) or [], report)
                deliveries[stream] = _dropped(deliveries.get(stream) or [], report)
        if callback is None:
            return report
