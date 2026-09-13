"""azarashi CLI tests."""
import io
import sys

from azarashi import __main__ as cli
from test_ublox import FRAME

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
EEW_HEX = EEW.split(',')[2].split('*')[0]
NOISE = b'\xff\xfe\r\n'


def _run(monkeypatch, capsys, args, stdin=b''):
    monkeypatch.setattr(sys, 'argv', ['azarashi', *args])
    # the real stdin decodes strictly under a UTF-8 locale
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(stdin), encoding='utf-8', errors='strict'))
    code = cli.main()
    out, err = capsys.readouterr()
    return code, out, err


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
