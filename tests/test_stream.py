"""decode_stream() tests for line-based messages and the per-stream dedup cache."""
import gc
import io
import threading
import time
import weakref

import pytest

import azarashi
from azarashi import api
from samples import EEW
from samples import EEW_HEX
from samples import FRAME
from samples import L_ALERT


class _LineSource:  # readline() only: no .closed, no buffer
    def __init__(self, text):
        self._lines = io.StringIO(text)

    def readline(self):
        return self._lines.readline()


class _SlotsLineSource:  # cannot be weakly referenced
    __slots__ = ('_lines',)

    def __init__(self, text):
        self._lines = io.StringIO(text)

    def readline(self):
        return self._lines.readline()


class _UnhashableLineSource(io.StringIO):  # can be weakly referenced, but not hashed
    __hash__ = None


class _EqualLineSource(io.StringIO):
    def __eq__(self, other):
        return isinstance(other, _EqualLineSource)

    def __hash__(self):
        return 1


def test_equal_streams_do_not_share_pending_sentences():
    first = _EqualLineSource(EEW + L_ALERT + '\n')
    second = _EqualLineSource(EEW + '\n')
    assert first == second and first is not second
    assert azarashi.decode_stream(first, ignore_dcx=False).message_type == 'DCR'
    assert azarashi.decode_stream(second, ignore_dcx=False).message_type == 'DCR'
    assert second.tell() > 0
    assert azarashi.decode_stream(first, ignore_dcx=False).message_type == 'DCX'


def test_equal_streams_do_not_share_duplicate_history():
    first = _EqualLineSource(EEW + '\n')
    second = _EqualLineSource(EEW + '\n')
    assert azarashi.decode_stream(first, unique=True) == azarashi.decode(EEW)
    assert azarashi.decode_stream(second, unique=True) == azarashi.decode(EEW)


def test_nmea_line_noise_does_not_stop_the_stream():
    # binary line sources such as pySerial's readline() may deliver non-UTF-8 noise
    stream = io.BytesIO(b'\xff\xfe\r\n' + EEW.encode() + b'\r\n')
    assert azarashi.decode_stream(stream, 'nmea') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('stream', [
    io.BytesIO(b'\x00\x00' + EEW.encode() + b'\r\n'),
    io.BytesIO(b'\xff' + EEW.encode() + b'\r\n'),
    io.StringIO('garbage' + EEW + '\n'),
])
def test_nmea_sentence_after_garbage_on_the_same_line(stream):
    assert azarashi.decode_stream(stream, 'nmea') == azarashi.decode(EEW, 'nmea')


def test_nmea_truncated_sentence_after_garbage_is_a_decoder_error():
    stream = io.StringIO('garbage' + EEW[:40] + '\n' + EEW + '\n')
    with pytest.raises(azarashi.AzarashiInvalidMessageError):
        azarashi.decode_stream(stream, 'nmea')
    assert azarashi.decode_stream(stream, 'nmea') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('line, results', [  # the newline between the sentences was lost
    (EEW[:30] + EEW, ['Too Short Sentence', 'EEW']),
    (EEW + EEW, ['EEW', 'EEW']),
    (EEW + EEW[:30], ['EEW', 'Too Short Sentence']),
])
def test_nmea_sentences_on_one_line_are_decoded_one_by_one(line, results):
    stream = io.BytesIO(line.encode() + b'\r\n')
    decoded = []
    with pytest.raises(EOFError):
        while True:
            try:
                decoded.append('EEW' if azarashi.decode_stream(stream, 'nmea') == azarashi.decode(EEW) else 'other')
            except azarashi.AzarashiInvalidMessageError as e:
                decoded.append(e.message)
    assert decoded == results


def test_sentences_left_on_a_line_do_not_keep_the_stream_alive():
    stream = io.BytesIO((EEW + EEW + '\r\n').encode())
    azarashi.decode_stream(stream, 'nmea')  # the second sentence is kept for the next call
    ref = weakref.ref(stream)
    del stream
    gc.collect()
    assert ref() is None


def test_hex_from_a_text_stream():
    # the documents recommend opening a file as bytes, but a text stream is what open() gives by
    # default, and hex is the one format a caller is likely to have as text
    stream = io.StringIO(f'{EEW_HEX}\n{EEW_HEX}\n')
    assert azarashi.decode_stream(stream, 'hex') == azarashi.decode(EEW, 'nmea')
    assert azarashi.decode_stream(stream, 'hex') == azarashi.decode(EEW, 'nmea')
    with pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(stream, 'hex')


def test_hex_line_noise_is_a_decoder_error():
    stream = io.BytesIO(b'\xff\xfe\n' + EEW_HEX.encode() + b'\n')
    with pytest.raises(azarashi.AzarashiInvalidMessageError):
        azarashi.decode_stream(stream, 'hex')
    assert azarashi.decode_stream(stream, 'hex') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('make_source', [_LineSource, _SlotsLineSource, _UnhashableLineSource])
def test_unique_with_minimal_stream_objects(make_source):
    source = make_source(EEW + '\n' + EEW + '\n')
    assert azarashi.decode_stream(source, 'nmea', unique=True) == azarashi.decode(EEW, 'nmea')
    with pytest.raises(EOFError):  # the duplicate is suppressed
        azarashi.decode_stream(source, 'nmea', unique=True)
    # other streams must not trip over the cached one
    assert azarashi.decode_stream(io.StringIO(EEW + '\n'), 'nmea') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('make_stream', [io.StringIO, _UnhashableLineSource])
def test_dedup_cache_does_not_keep_stream_alive(make_stream):
    stream = make_stream(EEW + '\n')
    azarashi.decode_stream(stream, 'nmea', unique=True)
    ref = weakref.ref(stream)
    del stream
    gc.collect()
    assert ref() is None


@pytest.mark.parametrize('unique', [True, 60])
def test_unique_counts_a_report_only_once_it_is_delivered(unique):
    delivered = []

    def callback(report):
        delivered.append(report)
        if len(delivered) == 1:
            raise OSError('Network is unreachable')

    stream = io.StringIO(f'{EEW}\n' * 3)
    with pytest.raises(OSError):
        azarashi.decode_stream(stream, callback=callback, unique=unique)
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, callback=callback, unique=unique)
    assert len(delivered) == 2  # the second copy is delivered, and the third is its duplicate


class _Trickle:  # a few bytes per read, the way a serial port delivers them
    def __init__(self, data, chunk=7):
        self._data, self._chunk, self._pos = data, chunk, 0

    def read1(self, size=-1):
        time.sleep(0)  # a real device releases the GIL while it waits for the bytes
        data = self._data[self._pos:self._pos + self._chunk]
        self._pos += len(data)
        return data


def _drain(target, *args, **kwargs):
    threads = [threading.Thread(target=target, args=args, kwargs=kwargs) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_threads_reading_one_stream_lose_no_message():
    stream = _Trickle(FRAME * 50, chunk=1)  # a byte at a time, as decode_stream() reads an unbuffered stream
    decoded = []

    def drain():
        while True:
            try:
                decoded.append(azarashi.decode_stream(stream, 'ublox'))
            except EOFError:
                return

    _drain(drain)
    assert len(decoded) == 50


def test_a_callback_does_not_hold_the_stream():
    stream = io.StringIO(f'{EEW}\n{L_ALERT}\n')
    first_in_callback, second_delivered = threading.Event(), threading.Event()
    delivered, overlapped = [], []

    def callback(report):
        delivered.append(report)
        if first_in_callback.is_set():
            second_delivered.set()
        else:
            first_in_callback.set()
            overlapped.append(second_delivered.wait(5))  # the second message has to arrive while we wait here

    def drain():
        try:
            azarashi.decode_stream(stream, 'nmea', callback=callback, ignore_dcx=False)
        except EOFError:
            return

    _drain(drain)
    assert overlapped == [True]  # False: the stream stayed locked until the callback returned
    assert len(delivered) == 2


def test_a_report_being_delivered_does_not_suppress_it_on_another_stream():
    streams = [io.StringIO(f'{EEW}\n'), io.StringIO(f'{EEW}\n')]
    in_callback, second_done = threading.Event(), threading.Event()
    delivered = []

    def callback(report):
        delivered.append(report)
        if in_callback.is_set():
            second_done.set()
        else:
            in_callback.set()
            second_done.wait(5)  # the other stream delivers its copy while this one is still in the callback

    def drain(stream, wait_first):
        if wait_first:
            in_callback.wait(5)
        try:
            azarashi.decode_stream(stream, 'nmea', callback=callback, unique=True)
        except EOFError:
            return

    threads = [threading.Thread(target=drain, args=(stream, i > 0)) for i, stream in enumerate(streams)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(delivered) == 2  # unique is per stream: one delivery must not swallow the other


def test_threads_reading_one_stream_share_the_dedup_cache():
    stream = io.StringIO(f'{EEW}\n' * 40)
    delivered = []

    def callback(report):
        delivered.append(report)
        time.sleep(0.05)  # long enough for the other threads to reach the duplicates behind it

    def drain():
        try:
            azarashi.decode_stream(stream, 'nmea', callback=callback, unique=True)
        except EOFError:
            return

    _drain(drain)
    assert len(delivered) == 1


def test_unique_keeps_the_newest_cache_size_reports(monkeypatch):
    monkeypatch.setattr(api, 'cache_size', 1)
    stream = io.StringIO(f'{EEW}\n{L_ALERT}\n{EEW}\n')
    received = []
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, callback=received.append, unique=True, ignore_dcx=False)
    assert [report.message_type for report in received] == ['DCR', 'DCX', 'DCR']  # the L-Alert pushed the EEW out
    assert len(api.caches.get(stream)) == 1


class _PlainFunctionReader:
    """A stream whose readline is a plain function, so the reader has no __self__ to key state on."""

    def __init__(self, chunks):
        chunks = iter(chunks)
        self.readline = lambda *args: next(chunks, b'')


def test_a_reader_that_is_not_a_bound_method_gets_its_own_state():
    # such a reader cannot have a read timeout, so it never holds a partial line, but it still needs an entry
    line = EEW.encode() + b'\r\n'
    first, second = _PlainFunctionReader([line, line]), _PlainFunctionReader([line])
    assert azarashi.decode_stream(first, 'nmea') == azarashi.decode(EEW, 'nmea')
    assert azarashi.decode_stream(second, 'nmea') == azarashi.decode(EEW, 'nmea')
    assert azarashi.decode_stream(first, 'nmea') == azarashi.decode(EEW, 'nmea')  # its own chunks, not the other's
    with pytest.raises(EOFError):
        azarashi.decode_stream(first, 'nmea')


def test_plain_function_reader_keeps_pending_sentences():
    stream = _PlainFunctionReader([(EEW + L_ALERT + '\n').encode()])
    assert azarashi.decode_stream(stream, ignore_dcx=False).message_type == 'DCR'
    gc.collect()
    assert azarashi.decode_stream(stream, ignore_dcx=False).message_type == 'DCX'
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, ignore_dcx=False)


def test_plain_function_reader_releases_its_captured_stream():
    class Source:
        def __init__(self):
            self.lines = io.StringIO(EEW + L_ALERT + '\n')
            self.readline = lambda: self.lines.readline()

    stream = Source()
    assert azarashi.decode_stream(stream, ignore_dcx=False, unique=True).message_type == 'DCR'
    stream_ref, reader_ref = weakref.ref(stream), weakref.ref(stream.readline)
    lines_ref = weakref.ref(stream.lines)
    del stream
    gc.collect()
    assert stream_ref() is None
    assert reader_ref() is None
    assert lines_ref() is None
