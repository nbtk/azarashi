"""Streams with a read timeout (pySerial): timeouts are distinguishable from EOF and resumable."""
import io
import os

import pytest
import serial

import azarashi
from azarashi.streams import state
from samples import EEW
from samples import EEW_HEX
from samples import FRAME

EEW_LINE = EEW.encode() + b'\r\n'
EEW_HEX_LINE = EEW_HEX.encode() + b'\n'


class _SerialLike:
    """Behaves like pySerial with a read timeout; an empty chunk in the script is a timeout."""
    timeout = 0.1

    def __init__(self, *script):
        self._script = list(script)
        self._data = b''

    def read(self, size=1):
        if not self._data:
            if not self._script:
                return b''
            self._data = self._script.pop(0)
        ret, self._data = self._data[:size], self._data[size:]
        return ret

    def readline(self):
        line = b''
        while not line.endswith(b'\n'):
            c = self.read(1)
            if not c:
                break  # timeout: pySerial returns what it has read so far
            line += c
        return line


def _expected():
    return azarashi.decode(EEW, 'nmea')


def test_ublox_frame_split_by_a_timeout():
    for split in range(1, len(FRAME)):
        stream = _SerialLike(FRAME[:split], b'', FRAME[split:])
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(stream, 'ublox')
        assert azarashi.decode_stream(stream, 'ublox') == _expected(), split
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(stream, 'ublox')


@pytest.mark.parametrize('msg_type, line', [('nmea', EEW_LINE), ('hex', EEW_HEX_LINE)])
def test_line_split_by_a_timeout(msg_type, line):
    for split in range(1, len(line)):
        stream = _SerialLike(line[:split], b'', line[split:])
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(stream, msg_type)
        assert azarashi.decode_stream(stream, msg_type) == _expected(), split


def test_a_timeout_is_not_the_end_of_the_data():
    # a stream that may still send more must not be taken for one that has run out: a handler
    # that stops on EOFError would stop reading a device that is working
    with pytest.raises(azarashi.AzarashiTimeoutError) as e:
        azarashi.decode_stream(_SerialLike(), 'nmea')
    assert not isinstance(e.value, EOFError)
    assert isinstance(e.value, azarashi.AzarashiReadOn)  # the way on is to read again


@pytest.mark.parametrize('msg_type, data', [('ublox', FRAME[:10]), ('nmea', b'$GPGGA,,'), ('hex', b'')])
def test_streams_without_a_timeout_still_end_with_eof(msg_type, data):
    with pytest.raises(EOFError) as e:
        azarashi.decode_stream(io.BytesIO(data), msg_type)
    # the data ended, which is not the timeout of a stream that may still send more
    assert isinstance(e.value, azarashi.AzarashiNoMoreData)
    assert not isinstance(e.value, azarashi.AzarashiTimeoutError)


@pytest.mark.skipif(not hasattr(os, 'openpty'), reason='needs a pseudo terminal')
@pytest.mark.parametrize('msg_type, data', [('ublox', FRAME), ('nmea', EEW_LINE)])
def test_pyserial_timeout_mid_message(msg_type, data):
    master, slave = os.openpty()
    try:
        with serial.Serial(os.ttyname(slave), 115200, timeout=0.2) as port:
            os.write(master, data[:20])
            with pytest.raises(azarashi.AzarashiTimeoutError):
                azarashi.decode_stream(port, msg_type)
            os.write(master, data[20:])
            assert azarashi.decode_stream(port, msg_type) == _expected()
    finally:
        os.close(master)
        os.close(slave)


class _NeverANewline:
    """A stream with a read timeout that keeps sending data and never ends a line."""

    timeout = 1

    def readline(self, *args):
        return b'X' * 100


def test_a_stream_that_never_sends_a_newline_does_not_fill_the_memory():
    stream = _NeverANewline()
    for _ in range(1000):
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(stream, 'nmea')
    held = state._partial_lines.get(stream.readline)
    assert sum(map(len, held)) <= state.max_partial_line


def test_a_sentence_split_by_timeouts_is_still_completed():
    # the cap is far above any sentence, so the parts of a real one are never dropped
    stream = _SerialLike(EEW_LINE[:20], b'', EEW_LINE[20:50], b'', EEW_LINE[50:])
    for _ in range(2):
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(stream, 'nmea')
    assert azarashi.decode_stream(stream, 'nmea') == _expected()
