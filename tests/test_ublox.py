"""u-blox UBX-RXM-SFRBX stream decoding tests."""
import gc
import io
import weakref

import pytest

import azarashi
from qzqsm import sfrbx
from qzqsm import ubx

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'


FRAME = sfrbx(EEW)


def _drain(stream):
    """Decode until EOF like the CLI does; returns the reports and the decoder error messages."""
    reports, errors = [], []
    while True:
        try:
            reports.append(azarashi.decode_stream(stream, 'ublox'))
        except azarashi.QzssDcrDecoderException as e:
            errors.append(e.message)
        except EOFError:
            return reports, errors


class _PausingStream:
    """read1() hands out two parts with an empty read in between, like a serial port timeout."""

    def __init__(self, first, second):
        self._parts = [first, b'', second]

    def read1(self, size=-1):
        return self._parts.pop(0) if self._parts else b''


class _SlotsStream:  # cannot be weakly referenced
    __slots__ = ('_data',)

    def __init__(self, data):
        self._data = io.BytesIO(data)

    def read1(self, size=-1):
        return self._data.read1(size)


class _UnhashableStream:
    __hash__ = None

    def __init__(self, data):
        self._data = io.BytesIO(data)

    def read1(self, size=-1):
        return self._data.read1(size)


def test_frame_decodes():
    report = azarashi.decode_stream(io.BytesIO(FRAME), 'ublox')
    assert report == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('prefix', [b'\xB5', b'\xB5\x62', b'\xB5\x62\x02'])
def test_frame_after_partial_header(prefix):
    # a stray sync char or a truncated header right before a frame must not swallow the frame
    report = azarashi.decode_stream(io.BytesIO(prefix + FRAME), 'ublox')
    assert report == azarashi.decode(EEW, 'nmea')


def test_unbuffered_binary_stream(tmp_path):
    # raw streams have neither read1() nor a buffer, and their read() takes no keyword arguments
    path = tmp_path / 'frames.ubx'
    path.write_bytes(FRAME + FRAME)
    with open(path, 'rb', buffering=0) as stream:
        assert not hasattr(stream, 'read1') and not hasattr(stream, 'buffer')
        assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW, 'nmea')
        assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW, 'nmea')
        with pytest.raises(EOFError):
            azarashi.decode_stream(stream, 'ublox')


@pytest.mark.parametrize('index, flip, expected_errors', [
    (5, 0x04, 0),  # length 40 -> 1064: longer than any SFRBX can be, skipped as a false header
    (4, 0x40, 1),  # length 40 -> 104: plausible, read and rejected by its checksum
])
def test_bit_flipped_length_keeps_following_frames(index, flip, expected_errors):
    damaged = bytearray(FRAME)
    damaged[index] ^= flip
    reports, errors = _drain(io.BytesIO(bytes(damaged) + FRAME * 25))
    assert len(reports) == 25
    assert len(errors) == expected_errors
    assert all(e.startswith('Checksum Mismatch') for e in errors)


def test_corrupted_payload_is_reported_and_skipped():
    damaged = bytearray(FRAME)
    damaged[20] ^= 0x01
    reports, errors = _drain(io.BytesIO(bytes(damaged) + FRAME * 3))
    assert len(reports) == 3
    assert len(errors) == 1 and errors[0].startswith('Checksum Mismatch')


def test_sfrbx_without_data_words_is_skipped():
    empty = ubx(b'\x02\x13', bytes((5, 0, 1, 0, 0, 0, 2, 0)))  # QZSS L1S, numWords=0
    assert azarashi.decode_stream(io.BytesIO(empty + FRAME), 'ublox') == azarashi.decode(EEW, 'nmea')


def test_frame_split_by_empty_read_is_resumed():
    for split in range(1, len(FRAME)):
        stream = _PausingStream(FRAME[:split], FRAME[split:])
        with pytest.raises(EOFError):
            azarashi.decode_stream(stream, 'ublox')
        assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW, 'nmea'), split


@pytest.mark.parametrize('make_stream', [io.BytesIO, _SlotsStream, _UnhashableStream])
def test_leftover_bytes_are_kept_between_calls(make_stream):
    stream = make_stream(FRAME + FRAME)  # a single read1() returns both frames
    assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW, 'nmea')
    assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW, 'nmea')
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, 'ublox')


def test_stream_is_not_kept_alive():
    stream = io.BytesIO(FRAME + FRAME)
    azarashi.decode_stream(stream, 'ublox', unique=True)  # leaves leftover bytes and a dedup cache behind
    ref = weakref.ref(stream)
    del stream
    gc.collect()
    assert ref() is None
