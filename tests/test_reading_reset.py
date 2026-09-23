"""Explicit reset discards extraction state, never I/O or delivery history."""
import gc
import io
import weakref

import pytest

import azarashi
from azarashi.streams.state import ReaderStore, StreamKeyedDict
from samples import EEW, EEW_HEX, FRAME, L_ALERT
from test_timeout import _SerialLike


@pytest.mark.parametrize('fmt,data', [('nmea', (EEW + '\n').encode()),
                                     ('hex', (EEW_HEX + '\n').encode()), ('ublox', FRAME)])
def test_reset_discards_partial_input_after_unobserved_reconnect(fmt, data):
    stream = _SerialLike(data[:20], b'', data)
    with pytest.raises(azarashi.AzarashiTimeoutError):
        azarashi.decode_stream(stream, fmt)
    azarashi.reset_reading_state(stream, fmt)
    assert azarashi.decode_stream(stream, fmt) == azarashi.decode(EEW)


def test_reset_discards_pending_nmea_but_keeps_history():
    stream = io.StringIO(EEW + L_ALERT + '\n' + EEW + '\n')
    azarashi.decode_stream(stream, unique=True, ignore_dcx=False)
    position = stream.tell()
    azarashi.reset_reading_state(stream)
    azarashi.reset_reading_state(stream)  # idempotent
    assert stream.tell() == position and not stream.closed
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, unique=True, ignore_dcx=False)


class Wrapper:
    def __init__(self, buffer):
        self.buffer = buffer


def test_reset_shared_buffer_affects_all_wrappers_but_not_other_owners():
    shared, other = io.BytesIO(FRAME * 3), io.BytesIO(FRAME * 2)
    first, second = Wrapper(shared), Wrapper(shared)
    azarashi.decode_stream(first, 'ublox', unique=True)
    azarashi.decode_stream(second, 'ublox', unique=True)
    azarashi.decode_stream(other, 'ublox')
    position = shared.tell()
    azarashi.reset_reading_state(first, 'ublox')
    assert shared.tell() == position
    with pytest.raises(EOFError):
        azarashi.decode_stream(second, 'ublox')
    assert azarashi.decode_stream(other, 'ublox') == azarashi.decode(EEW)
    for wrapper in (first, second):
        shared.seek(0)
        with pytest.raises(EOFError):
            azarashi.decode_stream(wrapper, 'ublox', unique=True)


def test_reader_store_discard_covers_all_methods_without_creating_values():
    created = []
    store = ReaderStore(lambda: created.append(1) or [])
    owner, other = io.BytesIO(), io.BytesIO()
    store.discard(owner.read)
    assert created == []
    store.get(owner.read).append('partial')
    store.get(owner.read1).append('pending')
    store.get(other.read).append('other')
    store.discard(owner.readline)
    assert store.get(owner.read) == store.get(owner.read1) == []
    assert store.get(other.read) == ['other']


def test_discard_does_not_inspect_unrelated_closed_properties():
    class BadClosed:
        __slots__ = ()

        @property
        def closed(self):
            raise AssertionError('must not inspect this owner')

    store = StreamKeyedDict()
    bad, owner = BadClosed(), io.BytesIO()
    store[bad], store[owner] = 1, 2
    store.discard(owner)
    store.discard(bad)
    assert store.get(owner) is None


def test_reset_unbound_function_drops_its_pending_sentences():
    class Source:
        def __init__(self):
            self.lines = io.StringIO(EEW + L_ALERT + '\n')
            self.readline = lambda: self.lines.readline()

    stream = Source()
    azarashi.decode_stream(stream, ignore_dcx=False)
    azarashi.reset_reading_state(stream)
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, ignore_dcx=False)
    ref = weakref.ref(stream)
    del stream
    gc.collect()
    assert ref() is None


@pytest.mark.parametrize('fmt', ['net', 'invalid'])
def test_invalid_reset_does_not_discard_pending_input(fmt):
    stream = io.StringIO(EEW + L_ALERT + '\n')
    azarashi.decode_stream(stream, ignore_dcx=False)
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError):
        azarashi.reset_reading_state(stream, fmt)
    assert azarashi.decode_stream(stream, ignore_dcx=False).message_type == 'DCX'


def test_reset_unused_stream_does_not_read_it():
    class Unreadable:
        def readline(self):
            raise AssertionError('reset must not perform I/O')

    azarashi.reset_reading_state(Unreadable())


def test_reset_works_for_non_weakly_referenceable_stream():
    class Source:
        __slots__ = ('lines',)

        def __init__(self):
            self.lines = io.StringIO(EEW + L_ALERT + '\n')

        def readline(self):
            return self.lines.readline()

    stream = Source()
    azarashi.decode_stream(stream, ignore_dcx=False)
    azarashi.reset_reading_state(stream)
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, ignore_dcx=False)
