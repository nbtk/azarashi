"""azarashi.network transmitter/receiver tests (loopback only)."""
import io
import socket
import sys

import pytest

import azarashi
from azarashi.network import receiver
from azarashi.network import transmitter

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
EEW_HEX = EEW.split(',')[2].split('*')[0]


@pytest.fixture
def udp_sink():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1', 0))
        sock.settimeout(5)
        yield sock


def test_transmitter_default_satellite_id(udp_sink):
    xmitter = transmitter.Transmitter('127.0.0.1', udp_sink.getsockname()[1], socket.AF_INET)
    report = azarashi.decode(EEW_HEX, 'hex')  # hex input carries no satellite id
    xmitter.handler(report)
    received = azarashi.decode(udp_sink.recv(256), 'net')
    assert (received.satellite_id, received.satellite_prn) == (55, 183)
    assert received.nmea == report.nmea


def test_transmitter_forwards_sentence_after_line_noise(monkeypatch, udp_sink):
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1', '-p', str(udp_sink.getsockname()[1]),
                                      '-t', 'nmea'])
    stdin = io.BytesIO(b'\xff\xfe\r\n' + EEW.encode() + b'\r\n')
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(stdin, encoding='utf-8', errors='strict'))
    assert transmitter.main() == 0
    assert azarashi.decode(udp_sink.recv(256), 'net') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('args, expected', [([], None), (['-i', 'eth0'], b'eth0\0')])
def test_receiver_passes_bind_iface(monkeypatch, args, expected):
    started = []
    monkeypatch.setattr(receiver.Receiver, 'start', lambda self, **kwargs: started.append(self))
    monkeypatch.setattr(sys, 'argv', ['receiver', *args])
    receiver.main()
    assert started[0].bind_iface == expected
