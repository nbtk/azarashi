from collections.abc import Callable
from typing import Any, Protocol, TypeAlias

from .hex_interface import hex_qzss_dcr_message_extractor
from .nmea_interface import nmea_qzss_dcr_message_extractor
from .stream_state import StreamKeyedDict
from .ublox_interface import ublox_qzss_dcr_message_extractor
from ..decoder import HexQzssDcrDecoder
from ..decoder import NetQzssDcrDecoder
from ..decoder import NmeaQzssDcrDecoder
from ..decoder import UBloxQzssDcrDecoder
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReport


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
cache_size = 256


def decode(msg: str | bytes, msg_type: str = 'nmea') -> QzssDcReport:
    if not msg:
        raise EOFError('Encountered EOF')

    if msg_type == 'hex':
        return HexQzssDcrDecoder(msg).decode()
    elif msg_type == 'net':
        return NetQzssDcrDecoder(msg).decode()
    elif msg_type == 'nmea' or msg_type == 'spresense':
        return NmeaQzssDcrDecoder(msg).decode()
    elif msg_type == 'ublox':
        return UBloxQzssDcrDecoder(msg).decode()
    else:
        raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')


def decode_stream(stream: QzssDcrStream,  # do not decode one stream in parallel!
                  msg_type: str = 'nmea',
                  callback: Callable[..., object] | None = None,
                  callback_args: tuple[Any, ...] = (),
                  callback_kwargs: dict[str, Any] | None = None,
                  unique: bool | float = False,
                  ignore_dcr: bool = False,
                  ignore_dcx: bool = True) -> QzssDcReport:
    if callback_kwargs is None:
        callback_kwargs = {}

    cache: list[QzssDcReport] = []
    if unique:
        cache = caches.get(stream) or []

    extractor: Callable[..., str | bytes]
    reader: Callable[..., Any]
    reader_args: tuple[Any, ...]
    if msg_type == 'hex':
        if callable(readline := getattr(stream, 'readline', None)):
            extractor = hex_qzss_dcr_message_extractor
            reader = readline
            reader_args = ()
        else:
            raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
    elif msg_type == 'nmea' or msg_type == 'spresense':
        if callable(readline := getattr(stream, 'readline', None)):
            extractor = nmea_qzss_dcr_message_extractor
            reader = readline
            reader_args = ()
        else:
            raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
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
            raise QzssDcrDecoderException(f'Neither read() nor read1() exists: {type(stream)}')
    else:
        raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')

    while True:
        msg = extractor(reader, reader_args=reader_args)
        report = decode(msg, msg_type)

        if report.message_type == 'DCR':
            if ignore_dcr is True:
                continue
        elif report.message_type == 'DCX':
            if ignore_dcx is True:
                continue
        else:  # unknown message type
            continue

        seen = cache
        if unique:
            if report in cache:
                if unique is True:  # never expire: always suppress duplicates
                    fire = False
                else:  # unique is a number of seconds: re-fire once the cached copy is stale
                    cached = cache[cache.index(report)]
                    freshness = (report.timestamp - cached.timestamp).total_seconds()
                    fire = freshness > unique
            else:
                fire = True

            seen = ([r for r in cache if r != report] + [report])[-cache_size:]
            if fire is False:
                cache = seen
                caches[stream] = cache
                continue

        if callback is not None:
            callback(report, *callback_args, **callback_kwargs)
        if unique:  # only a delivered report counts as seen, so a failed callback gets the next copy
            cache = seen
            caches[stream] = cache
        if callback is None:
            return report
