"""The L1S archive: a byte of PRN, then a record of GPS time and L1S message for each second."""
import datetime
import io
import sys

import pytest

import azarashi
from azarashi import __main__ as cli
from azarashi.decoders.l1s import gps_to_utc
from samples import EEW
from samples import L_ALERT

PRN = 184  # QZS-2
WEEK, SECOND = 2436, 345618  # 2026-09-17 00:00:00 UTC, 18 seconds of GPS time ahead of it
START = datetime.datetime(2026, 9, 17, tzinfo=datetime.UTC)
AUGMENTATION = bytes((0x53, 50 << 2)) + bytes(30)  # message type 50: not a DCR or DCX message


def _record(message, second=SECOND, week=WEEK):
    return (week << 20 | second).to_bytes(4, 'big') + message


def _message(sentence):
    return azarashi.decode(sentence).message


def archive(*records, prn=PRN):
    return bytes((prn,)) + b''.join(records)


class OneByte:
    """A stream read one byte at a time, as pySerial is."""

    def __init__(self, data):
        self._data = io.BytesIO(data)

    def read(self, size):
        return self._data.read(size)


def test_each_message_takes_its_satellite_and_time_from_the_archive():
    report = azarashi.decode_stream(io.BytesIO(archive(_record(_message(EEW), SECOND + 5))), 'l1s')
    assert report == azarashi.decode(EEW)
    assert report.timestamp == START + datetime.timedelta(seconds=5)
    assert (report.satellite_prn, report.satellite_id) == (PRN, PRN & 0x3f)
    assert report.nmea.startswith('$QZQSM,56,')  # the satellite id of PRN 184


def test_the_json_gives_the_satellite_and_the_time_of_the_archive():
    record = azarashi.to_json_dict(azarashi.decode_stream(io.BytesIO(archive(_record(_message(EEW)))), 'l1s'))
    assert record['satellite'] == {'system': 'qzss', 'prn': PRN}
    assert record['received_at'] == '2026-09-17T00:00:00Z'


def test_records_that_are_not_dcr_or_dcx_are_passed_over():
    stream = io.BytesIO(archive(_record(AUGMENTATION), _record(AUGMENTATION, SECOND + 1),
                                _record(_message(L_ALERT), SECOND + 2)))
    report = azarashi.decode_stream(stream, 'l1s', ignore_dcx=False)
    assert report == azarashi.decode(L_ALERT)
    with pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(stream, 'l1s', ignore_dcx=False)


def test_the_prn_is_read_once_per_stream():
    stream = io.BytesIO(archive(_record(_message(EEW)), _record(_message(EEW), SECOND + 1)))
    first = azarashi.decode_stream(stream, 'l1s')
    second = azarashi.decode_stream(stream, 'l1s')
    assert (first.satellite_prn, second.satellite_prn) == (PRN, PRN)
    assert second.timestamp - first.timestamp == datetime.timedelta(seconds=1)


def test_a_stream_read_a_byte_at_a_time():
    report = azarashi.decode_stream(OneByte(archive(_record(AUGMENTATION), _record(_message(EEW)))), 'l1s')
    assert report == azarashi.decode(EEW) and report.satellite_prn == PRN


def test_resetting_the_reading_state_keeps_the_prn():
    stream = OneByte(archive(_record(_message(EEW)), _record(_message(EEW), SECOND + 1)))
    azarashi.decode_stream(stream, 'l1s')
    azarashi.reset_reading_state(stream, 'l1s')
    assert azarashi.decode_stream(stream, 'l1s').satellite_prn == PRN  # the PRN is not a partial record


@pytest.mark.parametrize('data', [b'', bytes((PRN,)), archive(_record(_message(EEW))[:20])],
                         ids=['empty', 'the PRN alone', 'a record cut short'])
def test_the_end_of_the_archive_ends_the_reading(data):
    with pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(io.BytesIO(data), 'l1s')


def test_a_second_past_the_week_is_a_message_that_cannot_be_read():
    stream = io.BytesIO(archive(_record(_message(EEW), 604800), _record(_message(EEW))))
    with pytest.raises(azarashi.AzarashiInvalidMessageError, match='Invalid Second of the Week'):
        azarashi.decode_stream(stream, 'l1s')
    assert azarashi.decode_stream(stream, 'l1s').timestamp == START  # reading on reaches the next record


def test_gps_time_is_utc_behind_the_leap_seconds():
    assert gps_to_utc(WEEK, SECOND) == START
    assert gps_to_utc(1930, 18) == datetime.datetime(2017, 1, 1, tzinfo=datetime.UTC)
    assert gps_to_utc(1930, 17) is None  # before the GPS-UTC offsets the table knows


def test_a_time_before_the_offsets_known_is_a_message_that_cannot_be_read():
    with pytest.raises(azarashi.AzarashiInvalidMessageError, match='Time Before the GPS-UTC Offsets Known'):
        azarashi.decode_stream(io.BytesIO(archive(_record(_message(EEW), 0, week=1930))), 'l1s')


def test_a_timestamp_is_refused_before_anything_is_read():
    stream = io.BytesIO(archive(_record(_message(EEW))))
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError, match='gives the time of every message'):
        azarashi.decode_stream(stream, 'l1s', timestamp=START)
    assert stream.tell() == 0


def test_decode_refuses_a_record_alone():
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError, match='use decode_stream'):
        azarashi.decode(archive(_record(_message(EEW))), 'l1s')


def test_the_archive_is_read_as_bytes():
    with pytest.raises(azarashi.AzarashiArgumentTypeError, match='open the stream in binary mode'):
        azarashi.decode_stream(io.StringIO('text'), 'l1s')


def _cli(monkeypatch, capsys, args):
    monkeypatch.setattr(sys, 'argv', ['azarashi', *args])
    code = cli.main()
    return (code, *capsys.readouterr())


def test_the_command_reads_an_archive(monkeypatch, capsys, tmp_path):
    path = tmp_path / 'Q002_20260917.l1s'
    path.write_bytes(archive(_record(AUGMENTATION), _record(_message(EEW), SECOND + 60)))
    code, out, err = _cli(monkeypatch, capsys, ['l1s', '-f', str(path), '--json'])
    report = azarashi.decode_stream(io.BytesIO(archive(_record(_message(EEW)))), 'l1s')
    assert code == 0 and out.count('\n') == 1
    assert '"received_at":"2026-09-17T00:01:00Z"' in out and f'"nmea":"{report.nmea}"' in out


def test_the_command_refuses_a_time_for_an_archive(monkeypatch, capsys, tmp_path):
    path = tmp_path / 'archive.l1s'
    path.write_bytes(archive(_record(_message(EEW))))
    with pytest.raises(SystemExit) as exit_:
        _cli(monkeypatch, capsys, ['l1s', '-f', str(path), '--time', '2026-09-17T00:00:00Z'])
    assert exit_.value.code == 2 and 'gives the time of every message' in capsys.readouterr().err
