"""decode_stream() tests for line-based messages and the per-stream dedup cache."""
import gc
import io
import weakref

import pytest

import azarashi
from samples import EEW
from samples import EEW_HEX


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
    with pytest.raises(azarashi.QzssDcrDecoderException):
        azarashi.decode_stream(stream, 'nmea')
    assert azarashi.decode_stream(stream, 'nmea') == azarashi.decode(EEW, 'nmea')


def test_hex_line_noise_is_a_decoder_error():
    stream = io.BytesIO(b'\xff\xfe\n' + EEW_HEX.encode() + b'\n')
    with pytest.raises(azarashi.QzssDcrDecoderException):
        azarashi.decode_stream(stream, 'hex')
    assert azarashi.decode_stream(stream, 'hex') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('make_source', [_LineSource, _SlotsLineSource])
def test_unique_with_minimal_stream_objects(make_source):
    source = make_source(EEW + '\n' + EEW + '\n')
    assert azarashi.decode_stream(source, 'nmea', unique=True) == azarashi.decode(EEW, 'nmea')
    with pytest.raises(EOFError):  # the duplicate is suppressed
        azarashi.decode_stream(source, 'nmea', unique=True)
    # other streams must not trip over the cached one
    assert azarashi.decode_stream(io.StringIO(EEW + '\n'), 'nmea') == azarashi.decode(EEW, 'nmea')


def test_dedup_cache_does_not_keep_stream_alive():
    stream = io.StringIO(EEW + '\n')
    azarashi.decode_stream(stream, 'nmea', unique=True)
    ref = weakref.ref(stream)
    del stream
    gc.collect()
    assert ref() is None
