import weakref
from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast

from ..exception import QzssDcrDecoderTimeoutError

_T = TypeVar('_T')


class StreamKeyedDict(Generic[_T]):
    """Per-stream values that are released together with their stream objects.

    Streams that can be weakly referenced but not hashed are keyed by identity and dropped when
    they are collected. Streams that cannot be weakly referenced are kept until they report
    themselves closed.
    """

    def __init__(self) -> None:
        self._weak: weakref.WeakKeyDictionary[object, _T] = weakref.WeakKeyDictionary()
        self._by_id: dict[int, tuple[object, _T]] = {}  # id -> (a weak reference to the stream, or the stream; value)

    def get(self, stream: object, default: _T | None = None) -> _T | None:
        try:
            return self._weak.get(stream, default)
        except TypeError:  # not weakly referenceable, or unhashable
            self._discard_closed()
            entry = self._by_id.get(id(stream))
            return entry[1] if entry is not None and _held(entry[0]) is stream else default

    def __setitem__(self, stream: object, value: _T) -> None:
        try:
            self._weak[stream] = value
        except TypeError:  # not weakly referenceable, or unhashable
            key = id(stream)
            try:
                held: object = weakref.ref(stream, lambda _: self._by_id.pop(key, None))
            except TypeError:  # not weakly referenceable: kept until closed
                held = stream
            self._by_id[key] = (held, value)

    def clear(self) -> None:
        self._weak.clear()
        self._by_id.clear()

    def _discard_closed(self) -> None:
        for key, (held, _) in list(self._by_id.items()):
            if getattr(_held(held), 'closed', False):
                del self._by_id[key]


def _held(held: object) -> object:
    """The stream that StreamKeyedDict holds, directly or through a weak reference."""
    if isinstance(held, weakref.ref):
        return cast('weakref.ref[object]', held)()
    return held


class ReaderStore(Generic[_T]):
    """A value per reader (e.g. stream.read1), kept with the reader's stream and released together with it."""

    def __init__(self, factory: Callable[[], _T]) -> None:
        self._factory = factory
        self._by_stream: StreamKeyedDict[dict[str, _T]] = StreamKeyedDict()  # stream -> {reader name: value}
        self._unowned: dict[Callable[..., Any], _T] = {}  # readers that are not bound methods

    def get(self, reader: Callable[..., Any]) -> _T:
        stream = getattr(reader, '__self__', None)
        if stream is not None:
            per_reader = self._by_stream.get(stream)
            if per_reader is None:
                per_reader = {}
                self._by_stream[stream] = per_reader
            if reader.__name__ not in per_reader:
                per_reader[reader.__name__] = self._factory()
            return per_reader[reader.__name__]
        if reader not in self._unowned:
            self._unowned[reader] = self._factory()
        return self._unowned[reader]

    def clear(self) -> None:
        self._by_stream.clear()
        self._unowned.clear()


def has_read_timeout(reader: Callable[..., Any]) -> bool:
    """Whether an empty or partial read may only mean that the stream's read timeout expired (e.g. pySerial)."""
    return getattr(getattr(reader, '__self__', None), 'timeout', None) is not None


def empty_read_error(reader: Callable[..., Any]) -> EOFError:
    if has_read_timeout(reader):
        return QzssDcrDecoderTimeoutError('Timed Out')
    return EOFError('Encountered EOF')


_partial_lines: ReaderStore[list[Any]] = ReaderStore(list)  # the parts of a line, str or bytes as read


def read_line(reader: Callable[..., str | bytes],
              reader_args: tuple[Any, ...],
              reader_kwargs: dict[str, Any]) -> str | bytes:
    """Read a line; a line cut off by a read timeout is kept and completed on the next call."""
    partial = _partial_lines.get(reader)
    line = reader(*reader_args, **reader_kwargs)
    if has_read_timeout(reader):
        complete = line.endswith(b'\n') if isinstance(line, (bytes, bytearray)) else line.endswith('\n')
        if not line or not complete:
            if line:
                partial.append(line)
            raise QzssDcrDecoderTimeoutError('Timed Out')
    if not line:
        raise EOFError('Encountered EOF')
    if partial:
        line = line[:0].join(partial + [line])
        partial.clear()
    return line
