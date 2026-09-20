"""azarashi.network transmitter/receiver tests (loopback only)."""
import io
import logging
import socket
import subprocess
import sys
import threading
import time

import pytest
import serial

import azarashi
from azarashi.network import receiver
from azarashi.network import transmitter
from samples import EEW
from samples import EEW_HEX
from samples import L_ALERT


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


def test_transmitter_stops_when_the_serial_device_is_gone(monkeypatch, udp_sink):
    class Unplugged:
        closed = False

        def readline(self):
            raise serial.SerialException('device reports readiness to read but returned no data')

        def close(self):
            self.closed = True

    stream = Unplugged()
    monkeypatch.setattr(transmitter, 'open_input', lambda path, baudrate=9600: stream)
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1', '-p', str(udp_sink.getsockname()[1]),
                                      '-t', 'nmea', '-f', '/dev/ttyUSB0'])
    result = []
    thread = threading.Thread(target=lambda: result.append(transmitter.main()), daemon=True)
    thread.start()
    thread.join(5)
    assert result == [1] and stream.closed


@pytest.mark.parametrize('options', [[], ['-u']])  # with -u, the next copy of the alert is relayed
def test_transmitter_survives_a_failed_send(monkeypatch, udp_sink, options):
    sent = []

    def flaky_handler(self, report):
        if not sent:
            sent.append('failed')
            raise OSError('Network is unreachable')
        sent.append(report.message_type)

    monkeypatch.setattr(transmitter.Transmitter, 'handler', flaky_handler)
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1', '-p', str(udp_sink.getsockname()[1]),
                                      '-t', 'nmea', *options])
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(f'{EEW}\r\n{EEW}\r\n'.encode())))
    assert transmitter.main() == 0
    assert sent == ['failed', 'DCR']


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


def test_log_time_is_utc_with_z():
    from azarashi.network.log import utc_formatter
    record = logging.LogRecord('azarashi', logging.INFO, 'receiver.py', 1, 'hello', None, None)
    record.created, record.msecs = 1789300000.25, 250.0  # 2026-09-13T11:46:40.250 UTC
    assert utc_formatter().format(record) == '2026-09-13T11:46:40.250Z - INFO - hello'


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


@pytest.mark.parametrize('datagram, warning', [
    (b'hello', "[AzarashiInvalidMessageError] Too Short Sentence -> b'\\x68\\x65\\x6C\\x6C\\x6F'"),
    (b'', '[AzarashiInvalidMessageError] Empty Message'),
    (bytes((55,)) + bytes(32), '[AzarashiInvalidMessageError] Undefined Message Type: 0 -> $QZQSM,55,' + '0' * 63 + '*74'),
])
def test_receiver_skips_datagrams_that_are_not_messages(caplog, datagram, warning):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    recver = receiver.Receiver('127.0.0.1', port, address_family=socket.AF_INET)
    received = []
    payload = bytes((55,)) + azarashi.decode(EEW).message
    with caplog.at_level(logging.WARNING, logger=receiver.logger.name):
        thread = threading.Thread(target=recver.start, args=(received.append,), daemon=True)
        thread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            deadline = time.monotonic() + 5  # until the socket is bound, datagrams are dropped
            while time.monotonic() < deadline and not (received and warning in [r.getMessage() for r in caplog.records]):
                sender.sendto(datagram, ('127.0.0.1', port))
                sender.sendto(payload, ('127.0.0.1', port))  # right behind it: nothing queued may be lost
                time.sleep(0.01)
        messages = [r.getMessage() for r in caplog.records]
    assert thread.is_alive()
    assert received and received[0] == azarashi.decode(EEW)
    assert warning in messages


def test_receiver_command_keeps_receiving_after_an_empty_datagram(monkeypatch, caplog):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    monkeypatch.setattr(sys, 'argv', ['receiver', '-b', '127.0.0.1', '-p', str(port)])
    payload = bytes((55,)) + azarashi.decode(EEW).message
    with caplog.at_level(logging.INFO, logger=receiver.logger.name):
        thread = threading.Thread(target=receiver.main, daemon=True)
        thread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            warning = '[AzarashiInvalidMessageError] Empty Message'
            deadline = time.monotonic() + 5  # until the socket is bound, datagrams are dropped
            while time.monotonic() < deadline:
                messages = [r.getMessage() for r in caplog.records]
                if warning in messages and any('緊急地震速報' in m for m in messages[messages.index(warning):]):
                    break
                sender.sendto(b'', ('127.0.0.1', port))
                sender.sendto(payload, ('127.0.0.1', port))
                time.sleep(0.01)
        messages = [r.getMessage() for r in caplog.records]
    assert thread.is_alive()
    assert warning in messages
    assert any('緊急地震速報' in message for message in messages[messages.index(warning):])  # after the empty one


def test_receiver_handlers_log_the_report(caplog):
    report = azarashi.decode(EEW)
    with caplog.at_level(logging.INFO, logger=receiver.logger.name):
        receiver.Receiver.default_handler(report)
        receiver.simple_handler(report)
    verbose, simple = [r.getMessage() for r in caplog.records]
    assert "'disaster_category': '緊急地震速報'," in verbose
    assert simple == f'\n{report}\n'


def test_transmitter_command_warns_about_decoder_errors(monkeypatch, caplog, udp_sink, tmp_path):
    record = tmp_path / 'record.nmea'
    data = f'{EEW[:-2]}00\r\n{EEW}\r\n'.encode()
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1', '-p', str(udp_sink.getsockname()[1]),
                                      '-t', 'nmea', '--record', str(record)])
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(data)))
    with caplog.at_level(logging.WARNING, logger=transmitter.logger.name):
        assert transmitter.main() == 0
    assert [r.getMessage() for r in caplog.records] == [f'[AzarashiInvalidMessageError] Checksum Mismatch, should be 05 -> {EEW[:-2]}00']
    assert azarashi.decode(udp_sink.recv(256), 'net') == azarashi.decode(EEW)
    assert record.read_bytes() == data


def test_transmitter_command_warns_about_unimplemented_decoders(monkeypatch, caplog):
    errors = [azarashi.AzarashiNotImplementedError('Decoder Not Implemented')]

    def start(self, stream, msg_type, unique):
        if errors:
            raise errors.pop()
        raise EOFError('Encountered EOF')

    monkeypatch.setattr(transmitter.Transmitter, 'start', start)
    monkeypatch.setattr(sys, 'argv', ['transmitter', '-d', '127.0.0.1'])
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO()))
    with caplog.at_level(logging.WARNING, logger=transmitter.logger.name):
        assert transmitter.main() == 0
    assert [r.getMessage() for r in caplog.records] == ['[AzarashiNotImplementedError] Decoder Not Implemented']


@pytest.mark.parametrize('module', ['azarashi.network.receiver', 'azarashi.network.transmitter'])
def test_network_commands_run_as_modules(module):
    result = subprocess.run([sys.executable, '-m', module, '--help'], capture_output=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith('usage: ')


def test_receiver_binds_to_an_interface_only_on_linux(monkeypatch):
    recver = receiver.Receiver('127.0.0.1', 0, bind_iface='eth0', address_family=socket.AF_INET)
    monkeypatch.setattr(sys, 'platform', 'darwin')
    with pytest.raises(OSError, match='SO_BINDTODEVICE'):
        recver.start()
