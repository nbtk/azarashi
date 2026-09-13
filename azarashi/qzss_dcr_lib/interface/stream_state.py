import weakref

from ..exception import QzssDcrDecoderTimeoutError


class StreamKeyedDict:
    """Per-stream values that are released together with their stream objects.

    Streams that cannot be weakly referenced fall back to a regular dict, whose
    entries are dropped once their stream reports itself closed.
    """

    def __init__(self):
        self._weak = weakref.WeakKeyDictionary()
        self._strong = {}

    def get(self, stream, default=None):
        try:
            return self._weak.get(stream, default)
        except TypeError:  # not weakly referenceable
            self._discard_closed()
            return self._strong.get(stream, default)

    def __setitem__(self, stream, value):
        try:
            self._weak[stream] = value
        except TypeError:  # not weakly referenceable
            self._strong[stream] = value

    def clear(self):
        self._weak.clear()
        self._strong.clear()

    def _discard_closed(self):
        for stream in list(self._strong):
            if getattr(stream, 'closed', False):
                del self._strong[stream]


class ReaderStore:
    """A value per reader (e.g. stream.read1), kept with the reader's stream and released together with it."""

    def __init__(self, factory):
        self._factory = factory
        self._by_stream = StreamKeyedDict()  # stream -> {reader name: value}
        self._unowned = {}  # readers that are not bound methods of a hashable object

    def get(self, reader):
        stream = getattr(reader, '__self__', None)
        if stream is not None:
            try:
                per_reader = self._by_stream.get(stream)
                if per_reader is None:
                    per_reader = {}
                    self._by_stream[stream] = per_reader
            except TypeError:  # unhashable stream
                pass
            else:
                if reader.__name__ not in per_reader:
                    per_reader[reader.__name__] = self._factory()
                return per_reader[reader.__name__]
        if reader not in self._unowned:
            self._unowned[reader] = self._factory()
        return self._unowned[reader]

    def clear(self):
        self._by_stream.clear()
        self._unowned.clear()


def has_read_timeout(reader):
    """Whether an empty or partial read may only mean that the stream's read timeout expired (e.g. pySerial)."""
    return getattr(getattr(reader, '__self__', None), 'timeout', None) is not None


def empty_read_error(reader):
    if has_read_timeout(reader):
        return QzssDcrDecoderTimeoutError('Timed Out')
    return EOFError('Encountered EOF')


_partial_lines = ReaderStore(list)


def read_line(reader, reader_args, reader_kwargs):
    """Read a line; a line cut off by a read timeout is kept and completed on the next call."""
    partial = _partial_lines.get(reader)
    line = reader(*reader_args, **reader_kwargs)
    if has_read_timeout(reader):
        newline = b'\n' if isinstance(line, (bytes, bytearray)) else '\n'
        if not line or not line.endswith(newline):
            if line:
                partial.append(line)
            raise QzssDcrDecoderTimeoutError('Timed Out')
    if not line:
        raise EOFError('Encountered EOF')
    if partial:
        line = line[:0].join(partial + [line])
        partial.clear()
    return line
