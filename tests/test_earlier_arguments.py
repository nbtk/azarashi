"""msg_type, the earlier name of msg_format, which code written for earlier versions passes."""
import inspect
import io
import sys

import pytest

import azarashi
from azarashi.network import transmitter
from samples import EEW
from samples import EEW_HEX

TAKERS = [azarashi.decode, azarashi.decode_stream, azarashi.reset_reading_state, transmitter.Transmitter.start]


@pytest.mark.parametrize('function', TAKERS)
def test_the_signature_shows_msg_format_only(function):
    parameters = inspect.signature(function).parameters
    assert 'msg_format' in parameters and 'msg_type' not in parameters


def test_decode_takes_msg_type():
    assert azarashi.decode(EEW_HEX, msg_type='hex') == azarashi.decode(EEW)


def test_decode_stream_takes_msg_type():
    assert azarashi.decode_stream(io.BytesIO(f'{EEW_HEX}\r\n'.encode()), msg_type='hex') == azarashi.decode(EEW)


@pytest.mark.parametrize('call', [
    lambda stream: azarashi.reset_reading_state(stream, msg_type='net'),
    lambda stream: transmitter.Transmitter('127.0.0.1').start(stream, msg_type='net'),
])
def test_reset_and_the_transmitter_take_msg_type(call):
    stream = io.BytesIO(f'{EEW}\r\n'.encode())
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError, match='^Message Format net is not a stream format'):
        call(stream)
    assert stream.tell() == 0


@pytest.mark.parametrize('call, name', [
    (lambda stream: azarashi.decode(EEW, 'nmea', msg_type='nmea'), 'decode'),
    (lambda stream: azarashi.decode(EEW, msg_format='nmea', msg_type='nmea'), 'decode'),
    (lambda stream: azarashi.decode_stream(stream, 'nmea', msg_type='nmea'), 'decode_stream'),
    (lambda stream: azarashi.reset_reading_state(stream, msg_format='nmea', msg_type='nmea'), 'reset_reading_state'),
    (lambda stream: transmitter.Transmitter('127.0.0.1').start(stream, 'nmea', msg_type='nmea'), 'start'),
])
def test_both_names_at_once_are_refused_before_anything_is_read(call, name):
    stream = io.BytesIO(f'{EEW}\r\n'.encode())
    with pytest.raises(azarashi.AzarashiArgumentTypeError) as error:
        call(stream)
    assert str(error.value) == f'{name}() takes msg_format or its earlier name msg_type, not both'
    assert stream.tell() == 0


@pytest.mark.parametrize('options, msg_format', [
    ([], 'nmea'),
    (['-t', 'hex'], 'hex'),
    (['--msg-format', 'ublox'], 'ublox'),
    (['--msg-type', 'hex'], 'hex'),
])
def test_the_transmitter_command_takes_msg_type(options, msg_format, monkeypatch):
    given = []

    def start(self, stream, msg_format, unique):
        given.append(msg_format)
        raise EOFError('Encountered EOF')

    monkeypatch.setattr(transmitter.Transmitter, 'start', start)
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1', *options])
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO()))
    assert transmitter.main() == 0
    assert given == [msg_format]
