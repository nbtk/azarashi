"""Input handling of the command line tools: opening inputs and recording them."""
import io
import os
import sys

import pytest
import serial

import azarashi
from azarashi.input_stream import RecordingStream
from azarashi.input_stream import open_input
from samples import EEW
from samples import FRAME


class _ReadOnly:  # like pySerial: read() but no read1()
    def __init__(self, data):
        self._data = io.BytesIO(data)

    def read(self, size=1):
        return self._data.read(size)

    def close(self):
        self._data.close()


def test_stdin_is_read_as_bytes(monkeypatch):
    stdin = io.TextIOWrapper(io.BytesIO(b''))
    monkeypatch.setattr(sys, 'stdin', stdin)
    assert open_input('stdin') is stdin.buffer


def test_regular_file_is_opened_as_a_file(tmp_path):
    path = tmp_path / 'frames.ubx'
    path.write_bytes(FRAME)
    with open_input(str(path), 115200) as stream:
        assert isinstance(stream, io.BufferedReader)
        assert stream.read() == FRAME


@pytest.mark.skipif(not hasattr(os, 'openpty'), reason='needs a pseudo terminal')
def test_character_device_is_opened_with_pyserial():
    master, slave = os.openpty()
    try:
        with open_input(os.ttyname(slave), 115200) as port:
            assert isinstance(port, serial.Serial)
            assert (port.baudrate, port.timeout) == (115200, None)
            os.write(master, FRAME)
            assert azarashi.decode_stream(port, 'ublox') == azarashi.decode(EEW, 'nmea')
    finally:
        os.close(master)
        os.close(slave)


def test_names_that_are_not_paths_go_to_pyserial():
    with open_input('loop://', 38400) as port:  # pySerial URL, like COM3 on Windows
        assert isinstance(port, serial.SerialBase)
        assert (port.baudrate, port.timeout) == (38400, None)


@pytest.mark.parametrize('msg_type, data, make_stream', [
    ('ublox', b'noise' + FRAME + FRAME, io.BytesIO),   # read1()
    ('ublox', b'noise' + FRAME + FRAME, _ReadOnly),    # read(1)
    ('nmea', (EEW + '\r\n').encode() * 2, io.BytesIO),  # readline()
])
def test_recording_copies_everything_read(tmp_path, msg_type, data, make_stream):
    path = tmp_path / 'record'
    stream = RecordingStream(make_stream(data), open(path, 'ab'))
    reports = []
    with pytest.raises(EOFError):
        while True:
            reports.append(azarashi.decode_stream(stream, msg_type))
    stream.close()
    assert reports == [azarashi.decode(EEW, 'nmea')] * 2
    assert path.read_bytes() == data


def test_recording_read(tmp_path):
    path = tmp_path / 'record'
    stream = RecordingStream(io.BytesIO(b'abc'), open(path, 'ab'))
    assert (stream.read(2), stream.read(), stream.read()) == (b'ab', b'c', b'')
    assert stream.seekable()  # anything else is passed through to the stream
    stream.close()
    assert path.read_bytes() == b'abc'


class _FullDisk(io.BytesIO):
    """A record file that runs out of space after `room` bytes."""

    def __init__(self, room):
        super().__init__()
        self._room = room

    def write(self, data):
        if self.tell() + len(data) > self._room:
            raise OSError(28, 'No space left on device')
        return super().write(data)


def test_a_record_that_cannot_be_written_does_not_stop_decoding(capsys):
    record = _FullDisk(len(FRAME))
    stream = RecordingStream(io.BytesIO(FRAME * 3), record)
    reports = []
    with pytest.raises(EOFError):
        while True:
            reports.append(azarashi.decode_stream(stream, 'ublox'))
    stream.close()
    assert reports == [azarashi.decode(EEW, 'nmea')] * 3
    assert capsys.readouterr().err == '# recording stopped: [OSError] [Errno 28] No space left on device\n'  # once
    assert record.closed


class _FullDiskThatFailsToClose(_FullDisk):
    """The same, but flushing what could not be written fails too."""

    def close(self):
        raise OSError(28, 'No space left on device')


def test_a_record_file_that_cannot_be_closed_does_not_stop_decoding(capsys):
    record = _FullDiskThatFailsToClose(len(FRAME))
    stream = RecordingStream(io.BytesIO(FRAME * 2), record)
    reports = []
    with pytest.raises(EOFError):
        while True:
            reports.append(azarashi.decode_stream(stream, 'ublox'))
    assert reports == [azarashi.decode(EEW, 'nmea')] * 2
    assert capsys.readouterr().err == '# recording stopped: [OSError] [Errno 28] No space left on device\n'
