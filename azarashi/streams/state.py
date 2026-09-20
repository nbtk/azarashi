import threading
import weakref
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from ..exceptions import AzarashiDisconnectedError
from ..exceptions import AzarashiNoMoreData
from ..exceptions import AzarashiReopenStream
from ..exceptions import AzarashiStreamClosedError
from ..exceptions import AzarashiTimeoutError

_T = TypeVar('_T')


class StreamKeyedDict(Generic[_T]):
    """Per-stream values that are released together with their stream objects.

    Streams are keyed by identity, regardless of their equality or hash. Weakly referenced
    streams are dropped when collected; the others are kept until they report themselves closed.
    """

    def __init__(self) -> None:
        self._weak: dict[int, tuple[weakref.ReferenceType[object], _T]] = {}
        self._strong: dict[int, tuple[object, _T]] = {}

    def get(self, stream: object, default: _T | None = None) -> _T | None:
        key = id(stream)
        weak_entry = self._weak.get(key)
        if weak_entry is not None:
            return weak_entry[1] if weak_entry[0]() is stream else default
        self._discard_closed()
        entry = self._strong.get(key)
        return entry[1] if entry is not None and entry[0] is stream else default

    def __setitem__(self, stream: object, value: _T) -> None:
        key = id(stream)
        try:
            ref = weakref.ref(stream, lambda _: self._weak.pop(key, None))
        except TypeError:  # not weakly referenceable: kept until closed
            self._strong[key] = (stream, value)
        else:
            self._weak[key] = (ref, value)

    def clear(self) -> None:
        self._weak.clear()
        self._strong.clear()

    def _discard_closed(self) -> None:
        for key, (stream, _) in list(self._strong.items()):
            if getattr(stream, 'closed', False):
                del self._strong[key]


_locks: StreamKeyedDict['threading.RLock'] = StreamKeyedDict()  # one lock per stream, released with the stream
_locks_guard = threading.Lock()


def stream_lock(stream: object) -> 'threading.RLock':
    """The lock that keeps the state of one stream to one thread at a time."""
    with _locks_guard:  # two threads must not each make a lock of their own for the same stream
        lock = _locks.get(stream)
        if lock is None:
            lock = threading.RLock()
            _locks[stream] = lock
        return lock


class ReaderStore(Generic[_T]):
    """A value per reader (e.g. stream.read1), kept with the reader's stream and released together with it."""

    def __init__(self, factory: Callable[[], _T]) -> None:
        self._factory = factory
        self._by_stream: StreamKeyedDict[dict[str, _T]] = StreamKeyedDict()  # stream -> {reader name: value}
        self._unowned: StreamKeyedDict[tuple[_T]] = StreamKeyedDict()  # callable identity; tuple permits None values

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
        entry = self._unowned.get(reader)
        if entry is None:
            entry = (self._factory(),)
            self._unowned[reader] = entry
        return entry[0]

    def clear(self) -> None:
        self._by_stream.clear()
        self._unowned.clear()


def has_read_timeout(reader: Callable[..., Any]) -> bool:
    """Whether an empty or partial read may only mean that the stream's read timeout expired (e.g. pySerial)."""
    return getattr(getattr(reader, '__self__', None), 'timeout', None) is not None


def empty_read_error(reader: Callable[..., Any]) -> AzarashiTimeoutError | AzarashiNoMoreData:
    """The error for a read that delivered nothing: not yet on a stream with a timeout, never otherwise."""
    if has_read_timeout(reader):
        return AzarashiTimeoutError('Timed Out')
    return AzarashiNoMoreData('Encountered EOF')


def read_stream(reader: Callable[..., _T], reader_args: tuple[Any, ...] = ()) -> _T:
    """Read from a stream, reporting a stream that failed rather than one that ended."""
    try:
        return reader(*reader_args)
    # a TimeoutError is here on purpose: a file over a socket with settimeout() raises it and is
    # left unusable, so the way on is a new stream, not another read. pySerial hands over what it
    # read instead of raising, and that is the read timeout AzarashiTimeoutError is for.
    except OSError as e:  # e.g. serial.SerialException once the device is unplugged
        raise AzarashiDisconnectedError(f'{type(e).__name__}: {e}') from e
    except ValueError as e:
        if not getattr(getattr(reader, '__self__', None), 'closed', False):
            raise  # a ValueError from somewhere else is not the stream failing
        # an io object that was closed, e.g. while another thread was reopening the device
        raise AzarashiStreamClosedError(f'{type(e).__name__}: {e}') from e


_partial_lines: ReaderStore[list[Any]] = ReaderStore(list)  # the parts of a line, str or bytes as read
max_partial_line = 1024  # the longest sentence a decoder takes is 76 characters, so this cannot cut a message


def read_line(reader: Callable[..., str | bytes], reader_args: tuple[Any, ...]) -> str | bytes:
    """Read a line; a line cut off by a read timeout is kept and completed on the next call."""
    partial = _partial_lines.get(reader)
    try:
        line = read_stream(reader, reader_args)
    except AzarashiReopenStream:
        partial.clear()  # the rest of the line can never arrive, and would corrupt the next one
        raise
    if has_read_timeout(reader):
        complete = line.endswith(b'\n') if isinstance(line, (bytes, bytearray)) else line.endswith('\n')
        if not line or not complete:
            if line:
                partial.append(line)
                if sum(map(len, partial)) > max_partial_line:
                    partial.clear()  # a stream that never sends a newline must not fill the memory
            raise AzarashiTimeoutError('Timed Out')
    if not line:
        raise AzarashiNoMoreData('Encountered EOF')
    if partial:
        line = line[:0].join(partial + [line])
        partial.clear()
    return line
