"""azarashi CLI tests."""
import datetime
import io
import re
import subprocess
import sys
import time

import azarashi
from azarashi import __main__ as cli
from samples import EEW
from samples import EEW_HEX
from samples import FRAME
from samples import L_ALERT

NOISE = b'\xff\xfe\r\n'


def _run(monkeypatch, capsys, args, stdin=b''):
    monkeypatch.setattr(sys, 'argv', ['azarashi', *args])
    # the real stdin decodes strictly under a UTF-8 locale
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(stdin), encoding='utf-8', errors='strict'))
    code = cli.main()
    out, err = capsys.readouterr()
    return code, out, err


def test_records_and_replays(monkeypatch, capsys, tmp_path):
    record = tmp_path / 'record.ubx'
    record.write_bytes(b'')  # recording appends
    data = b'noise' + FRAME + b'$GNGGA,,*00\r\n' + FRAME
    code, live, err = _run(monkeypatch, capsys, ['ublox', '--record', str(record)], data)
    assert code == 0 and live.count('\n緊急地震速報\n') == 2
    assert record.read_bytes() == data
    code, replay, err = _run(monkeypatch, capsys, ['ublox', '-f', str(record)])
    assert code == 0 and replay.count('\n緊急地震速報\n') == 2


def test_passes_the_baud_rate(monkeypatch, capsys):
    opened = []

    def fake_open_input(path, baudrate=9600):
        opened.append((path, baudrate))
        return io.BytesIO(FRAME)

    monkeypatch.setattr(cli, 'open_input', fake_open_input)
    code, out, err = _run(monkeypatch, capsys, ['ublox', '-f', '/dev/ttyUSB0', '-b', '115200'])
    assert code == 0 and opened == [('/dev/ttyUSB0', 115200)]
    _run(monkeypatch, capsys, ['ublox', '-f', '/dev/ttyS0'])
    assert opened[-1] == ('/dev/ttyS0', 9600)


def test_nmea_line_noise_from_stdin(monkeypatch, capsys):
    code, out, err = _run(monkeypatch, capsys, ['nmea'], NOISE + EEW.encode() + b'\r\n')
    assert code == 0
    assert '\n緊急地震速報\n' in out


def test_nmea_line_noise_from_file(monkeypatch, capsys, tmp_path):
    path = tmp_path / 'noise.nmea'
    path.write_bytes(NOISE + EEW.encode() + b'\r\n')
    code, out, err = _run(monkeypatch, capsys, ['nmea', '-f', str(path)])
    assert code == 0
    assert '\n緊急地震速報\n' in out


def test_hex_line_noise_from_stdin(monkeypatch, capsys):
    code, out, err = _run(monkeypatch, capsys, ['hex'], NOISE + EEW_HEX.encode() + b'\n')
    assert code == 0
    assert '\n緊急地震速報\n' in out
    assert '[QzssDcrDecoderException]' in err


def test_ublox_from_stdin_with_source(monkeypatch, capsys):
    code, out, err = _run(monkeypatch, capsys, ['ublox', '-s'], FRAME)
    assert code == 0
    assert '\n緊急地震速報\n' in out
    assert "# src: b'\\xB5\\x62\\x02\\x13" in out


def test_header_time_is_utc_with_z(monkeypatch, capsys):
    before = datetime.datetime.now(datetime.timezone.utc)
    code, out, err = _run(monkeypatch, capsys, ['nmea'], EEW.encode() + b'\r\n')
    header = out.splitlines()[0]
    match = re.fullmatch(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d{6})?Z) -{32}', header)
    assert match, header
    assert before <= datetime.datetime.fromisoformat(match.group(1)) <= datetime.datetime.now(datetime.timezone.utc)


def test_header_time_is_when_the_message_arrived(monkeypatch, capsys):
    def decode_stream(stream, msg_type, **kwargs):
        time.sleep(0.3)  # the message takes a while to arrive
        return azarashi.decode_stream(stream, msg_type, **kwargs)

    monkeypatch.setattr(cli, 'decode_stream', decode_stream)
    started = datetime.datetime.now(datetime.timezone.utc)
    code, out, err = _run(monkeypatch, capsys, ['nmea'], EEW.encode() + b'\r\n')
    header = datetime.datetime.fromisoformat(out.splitlines()[0].split(' ')[0])
    assert header - started >= datetime.timedelta(seconds=0.3)


def test_verbose_prints_every_field(monkeypatch, capsys):
    code, out, err = _run(monkeypatch, capsys, ['nmea', '-v'], EEW.encode() + b'\r\n')
    assert code == 0
    assert "'disaster_category': '緊急地震速報'," in out
    assert "'magnitude': '7.2'," in out


def test_source_of_a_text_message(monkeypatch, capsys):
    code, out, err = _run(monkeypatch, capsys, ['nmea', '-s'], EEW.encode() + b'\r\n')
    assert code == 0
    assert f'# src: {EEW}\n# hex: {EEW_HEX}\n' in out


def test_dcx_is_shown_unless_ignored(monkeypatch, capsys):
    l_alert = L_ALERT.encode() + b'\r\n'
    code, out, err = _run(monkeypatch, capsys, ['nmea'], EEW.encode() + b'\r\n' + l_alert)
    assert '### DCX Message - L-Alert ###' in out and '\n緊急地震速報\n' in out
    code, out, err = _run(monkeypatch, capsys, ['nmea', '-x'], EEW.encode() + b'\r\n' + l_alert)
    assert '### DCX Message' not in out and '\n緊急地震速報\n' in out
    code, out, err = _run(monkeypatch, capsys, ['nmea', '-r', '-u'], EEW.encode() + b'\r\n' + l_alert * 2)
    assert out.count('### DCX Message - L-Alert ###') == 1 and '緊急地震速報' not in out


def test_decoder_errors_are_reported_and_skipped(monkeypatch, capsys):
    errors = [azarashi.QzssDcrDecoderNotImplementedError('Decoder Not Implemented'),
              azarashi.QzssDcrDecoderException('Bad Message')]

    def decode_stream(stream, msg_type, **kwargs):
        if errors:
            raise errors.pop()
        return azarashi.decode_stream(stream, msg_type, **kwargs)

    monkeypatch.setattr(cli, 'decode_stream', decode_stream)
    code, out, err = _run(monkeypatch, capsys, ['nmea'], EEW.encode() + b'\r\n')
    assert code == 0
    assert '# [QzssDcrDecoderException] Bad Message\n' in err
    assert '# [QzssDcrDecoderNotImplementedError] Decoder Not Implemented\n' in err
    assert err.endswith('Encountered EOF\n\n')
    assert '\n緊急地震速報\n' in out


def test_unexpected_errors_stop_with_status_1(monkeypatch, capsys):
    class Stream(io.BytesIO):
        def read1(self, size=-1):
            raise OSError('device disconnected')

    stream = Stream()
    monkeypatch.setattr(cli, 'open_input', lambda path, baudrate=9600: stream)
    code, out, err = _run(monkeypatch, capsys, ['ublox', '-f', '/dev/ttyACM0'])
    assert code == 1
    assert '# [OSError] device disconnected\n' in err
    assert stream.closed


def test_run_as_a_module(tmp_path):
    path = tmp_path / 'eew.nmea'
    path.write_bytes(EEW.encode() + b'\r\n')
    result = subprocess.run([sys.executable, '-m', 'azarashi', 'nmea', '-f', str(path)],
                            capture_output=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0, result.stderr
    assert '\n緊急地震速報\n' in result.stdout
    assert result.stderr == 'Encountered EOF\n\n'
