"""Input handling of the command line tools: opening inputs and recording them."""
import io
import os
import sys

import pytest
import serial

import azarashi
from azarashi import __main__ as cli
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


def _run(monkeypatch, capsys, args, stdin=b''):
    monkeypatch.setattr(sys, 'argv', ['azarashi', *args])
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(stdin)))
    code = cli.main()
    out, err = capsys.readouterr()
    return code, out


def test_cli_records_and_replays(monkeypatch, capsys, tmp_path):
    record = tmp_path / 'record.ubx'
    record.write_bytes(b'')  # recording appends
    data = b'noise' + FRAME + b'$GNGGA,,*00\r\n' + FRAME
    code, live = _run(monkeypatch, capsys, ['ublox', '--record', str(record)], data)
    assert code == 0 and live.count('\n緊急地震速報\n') == 2
    assert record.read_bytes() == data
    code, replay = _run(monkeypatch, capsys, ['ublox', '-f', str(record)])
    assert code == 0 and replay.count('\n緊急地震速報\n') == 2


def test_cli_passes_the_baud_rate(monkeypatch, capsys):
    opened = []

    def fake_open_input(path, baudrate=9600):
        opened.append((path, baudrate))
        return io.BytesIO(FRAME)

    monkeypatch.setattr(cli, 'open_input', fake_open_input)
    code, out = _run(monkeypatch, capsys, ['ublox', '-f', '/dev/ttyUSB0', '-b', '115200'])
    assert code == 0 and opened == [('/dev/ttyUSB0', 115200)]
    code, out = _run(monkeypatch, capsys, ['ublox', '-f', '/dev/ttyS0'])
    assert opened[-1] == ('/dev/ttyS0', 9600)


def test_recording_read(tmp_path):
    path = tmp_path / 'record'
    stream = RecordingStream(io.BytesIO(b'abc'), open(path, 'ab'))
    assert (stream.read(2), stream.read(), stream.read()) == (b'ab', b'c', b'')
    assert stream.seekable()  # anything else is passed through to the stream
    stream.close()
    assert path.read_bytes() == b'abc'
