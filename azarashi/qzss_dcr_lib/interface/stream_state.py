import weakref


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
