"""Streams with a read timeout (pySerial): timeouts are distinguishable from EOF and resumable."""
import io
import os

import pytest
import serial

import azarashi
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
        with pytest.raises(azarashi.QzssDcrDecoderTimeoutError):
            azarashi.decode_stream(stream, 'ublox')
        assert azarashi.decode_stream(stream, 'ublox') == _expected(), split
        with pytest.raises(azarashi.QzssDcrDecoderTimeoutError):
            azarashi.decode_stream(stream, 'ublox')


@pytest.mark.parametrize('msg_type, line', [('nmea', EEW_LINE), ('hex', EEW_HEX_LINE)])
def test_line_split_by_a_timeout(msg_type, line):
    for split in range(1, len(line)):
        stream = _SerialLike(line[:split], b'', line[split:])
        with pytest.raises(azarashi.QzssDcrDecoderTimeoutError):
            azarashi.decode_stream(stream, msg_type)
        assert azarashi.decode_stream(stream, msg_type) == _expected(), split


def test_timeout_is_an_eof_error():
    with pytest.raises(EOFError):  # existing EOF handling keeps working
        azarashi.decode_stream(_SerialLike(), 'nmea')


@pytest.mark.parametrize('msg_type, data', [('ublox', FRAME[:10]), ('nmea', b'$GPGGA,,'), ('hex', b'')])
def test_streams_without_a_timeout_still_end_with_eof(msg_type, data):
    with pytest.raises(EOFError) as e:
        azarashi.decode_stream(io.BytesIO(data), msg_type)
    assert type(e.value) is EOFError


@pytest.mark.skipif(not hasattr(os, 'openpty'), reason='needs a pseudo terminal')
@pytest.mark.parametrize('msg_type, data', [('ublox', FRAME), ('nmea', EEW_LINE)])
def test_pyserial_timeout_mid_message(msg_type, data):
    master, slave = os.openpty()
    try:
        with serial.Serial(os.ttyname(slave), 115200, timeout=0.2) as port:
            os.write(master, data[:20])
            with pytest.raises(azarashi.QzssDcrDecoderTimeoutError):
                azarashi.decode_stream(port, msg_type)
            os.write(master, data[20:])
            assert azarashi.decode_stream(port, msg_type) == _expected()
    finally:
        os.close(master)
        os.close(slave)
