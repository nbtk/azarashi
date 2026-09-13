"""azarashi.network transmitter/receiver tests (loopback only)."""
import io
import socket
import sys
import threading
import time

import pytest

import azarashi
from azarashi.network import receiver
from azarashi.network import transmitter

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
EEW_HEX = EEW.split(',')[2].split('*')[0]
# DCX message (L-Alert)
L_ALERT = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E'


class _Enough(Exception):
    pass


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


def test_transmitter_relays_dcr_and_dcx(udp_sink):
    xmitter = transmitter.Transmitter('127.0.0.1', udp_sink.getsockname()[1], socket.AF_INET)
    with pytest.raises(EOFError):
        xmitter.start(io.BytesIO(f'{EEW}\r\n{L_ALERT}\r\n'.encode()), msg_type='nmea')
    received = [azarashi.decode(udp_sink.recv(256), 'net') for _ in range(2)]
    assert [r.message_type for r in received] == ['DCR', 'DCX']


@pytest.mark.parametrize('start_kwargs, expected_types', [
    ({}, {'DCR'}),  # like decode_stream(), DCX is ignored by default
    ({'ignore_dcx': False}, {'DCR', 'DCX'}),
    ({'ignore_dcr': True, 'ignore_dcx': False}, {'DCX'}),
])
def test_receiver_filters_message_types(start_kwargs, expected_types):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    received = []

    def callback(report):
        received.append(report.message_type)
        if len(received) == 6:
            raise _Enough

    recver = receiver.Receiver('127.0.0.1', port, address_family=socket.AF_INET)
    thread = threading.Thread(target=lambda: pytest.raises(_Enough, recver.start, callback, **start_kwargs),
                              daemon=True)
    thread.start()
    payloads = [bytes((55,)) + azarashi.decode(s).message for s in (EEW, L_ALERT)]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        deadline = time.monotonic() + 5
        while thread.is_alive() and time.monotonic() < deadline:
            for payload in payloads:
                sender.sendto(payload, ('127.0.0.1', port))
            time.sleep(0.01)
    thread.join(1)
    assert not thread.is_alive()
    assert set(received) == expected_types


@pytest.mark.parametrize('args, expected', [([], None), (['-i', 'eth0'], b'eth0\0')])
def test_receiver_passes_bind_iface(monkeypatch, args, expected):
    started = []
    monkeypatch.setattr(receiver.Receiver, 'start', lambda self, **kwargs: started.append(self))
    monkeypatch.setattr(sys, 'argv', ['receiver', *args])
    receiver.main()
    assert started[0].bind_iface == expected


@pytest.mark.parametrize('args, expected', [
    ([], {'ignore_dcr': False, 'ignore_dcx': False}),  # the command shows both, like the azarashi CLI
    (['-x'], {'ignore_dcr': False, 'ignore_dcx': True}),
    (['-r', '-v'], {'ignore_dcr': True, 'ignore_dcx': False}),
])
def test_receiver_command_filter_options(monkeypatch, args, expected):
    started = []
    monkeypatch.setattr(receiver.Receiver, 'start', lambda self, **kwargs: started.append(kwargs))
    monkeypatch.setattr(sys, 'argv', ['receiver', *args])
    receiver.main()
    assert {k: started[0][k] for k in expected} == expected
