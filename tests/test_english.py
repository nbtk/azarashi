"""The English text of the reports: get_text_en(), text_en in JSON and azarashi --english."""
import datetime
import re
import sys

import pytest

import azarashi
from azarashi import __main__ as cli
from azarashi.decoders import nmea
from azarashi.reports.dcr import Base
from azarashi.reports.dcr import NankaiTroughEarthquake as Nankai
from qzqsm import with_fields
from test_dcr import EEW, HYPOCENTER, NWP, TSUNAMI, _with_arrival_time
from test_golden import LOGS, TESTS

VOLCANO = '$QZQSM,56,9AAFC454450005445341F783E0F10910421230200000000000000012FB46E14*78'
JAPANESE = re.compile('[ぁ-んァ-ヶー一-龥々、。，．（）「」【】：・〜]')


def _reports():
    for log, received in sorted(LOGS.items()):
        with open(f'{TESTS}/{log}', encoding='utf-8') as f:
            for line in f:
                if line.startswith('$QZQSM'):
                    try:
                        yield nmea.Decoder(line.strip(), timestamp=received).decode()
                    except azarashi.AzarashiInvalidMessageError:
                        pass


@pytest.fixture(autouse=True)
def fresh_nankai_assembly(monkeypatch):
    monkeypatch.setattr(Nankai, 'reports', {})
    monkeypatch.setattr(Nankai, 'completed', False)
    monkeypatch.setattr(Nankai, 'announcement', None)


def test_every_dcr_report_but_nankai_has_english_with_no_japanese():
    names = set()
    for report in _reports():
        if report.message_type != 'DCR':
            continue
        text = report.get_text_en()
        if isinstance(report, Nankai):
            assert text is None
            continue
        names.add(type(report).__name__)
        assert text is not None and not JAPANESE.search(text), text
    assert names == {'EarthquakeEarlyWarning', 'Hypocenter', 'SeismicIntensity', 'Tsunami', 'Volcano', 'AshFall',
                     'Weather', 'Flood', 'Marine', 'Typhoon'}


def test_reports_written_in_english_give_their_text():
    dcx = [r for r in _reports() if r.message_type == 'DCX']
    assert dcx and all(r.get_text_en() == str(r) for r in dcx)
    nwp = azarashi.decode(NWP)
    assert nwp.get_text_en() == str(nwp)


def test_json_gives_the_english_text():
    report = azarashi.decode(HYPOCENTER)
    record = azarashi.to_json_dict(report)
    assert record['text_en'] == report.get_text_en()
    assert record['text'] == str(report)


def test_the_hypocenter_in_english():
    lines = azarashi.decode(HYPOCENTER).get_text_en().splitlines()
    assert lines[0] == 'JMA-DC Report (Hypocenter) (Issue) (Training/Test)'
    assert lines[2] == 'Occurred at 13:05 JST, 7 Mar.'
    assert 'Latitude and longitude: N 32°42´00˝, E 132°06´00˝' in lines


def test_coordinates_out_of_range_are_named_by_the_same_code_as_in_japanese():
    report = azarashi.decode(with_fields(HYPOCENTER, [(122 + 29, 6, 60)]))
    assert report.coordinates_of_hypocenter == '緯度・経度(コード番号：280515596032)'
    assert 'Latitude and longitude: Undefined Latitude and Longitude (Code: 280515596032)' in report.get_text_en()


def test_tsunami_arrival_types_in_english():
    sentence = _with_arrival_time(TSUNAMI, 1, 0, 31, 63)
    sentence = _with_arrival_time(sentence, 2, 0, 30, 62)
    report = azarashi.decode(_with_arrival_time(sentence, 0, 0, 24, 0))
    assert report.expected_tsunami_arrival_time_types_en == [
        'Undefined Expected Tsunami Arrival Time (Code: 1536)', 'Tsunami arrival expected', 'No data']
    assert [line for line in report.get_text_en().splitlines() if line.startswith('Estimated initial')] == [
        'Estimated initial tsunami arrival time: Undefined Expected Tsunami Arrival Time (Code: 1536)',
        'Estimated initial tsunami arrival time: Tsunami arrival expected',
        'Estimated initial tsunami arrival time: No data',
    ]
    assert report.get_text_en().splitlines()[2] == 'Warning code: Tsunami Warning'


@pytest.mark.parametrize('code, line', [
    (1, 'Warning code: No Tsunami'),
    (2, 'Warning code: Warning Lifted'),
    (5, 'Warning code: Major Tsunami Warning: Issued'),
])
def test_the_tsunami_warning_is_a_line_of_its_own(code, line):
    report = azarashi.decode(with_fields(TSUNAMI, [(80, 4, code)]))
    assert report.get_text_en().splitlines()[2] == line


def test_the_seismic_intensity_gives_the_occurrence_time():
    report = next(r for r in _reports() if type(r).__name__ == 'SeismicIntensity')
    assert 'Occurrence time of earthquake: 10:05 JST, 21 Aug.' in report.get_text_en().splitlines()


def test_an_occurrence_time_that_is_not_a_time_is_named_by_its_code():
    report = azarashi.decode(with_fields(EEW, [(85, 5, 24)]))  # hour 24
    assert report.occurrence_time_of_earthquake is None
    assert 'Occurrence time of earthquake: Undefined Occurrence Time of Earthquake (Code: ' in report.get_text_en()


def test_the_assumptive_hypocenter_is_marked():
    report = azarashi.decode(EEW)
    report.assumptive = True
    text = report.get_text_en()
    assert 'Depth: 10 km (assumptive hypocenter)' in text
    assert 'Magnitude: 7.2 (assumptive hypocenter)' in text


@pytest.mark.parametrize('utc, jst', [
    (datetime.datetime(2026, 8, 31, 20, 5, tzinfo=datetime.UTC), '05:05 JST, 1 Sep.'),  # the next day in JST
    (datetime.datetime(2026, 5, 3, 0, 0, tzinfo=datetime.UTC), '09:00 JST, 3 May'),  # May is not cut short
])
def test_times_are_in_jst_as_jma_writes_them(utc, jst):
    assert Base.convert_dt_to_str_en(utc) == jst


@pytest.mark.parametrize('du, line', [
    (0, 'Activity time: 11:10 JST, 21 Aug.'),
    (1, 'Activity time: around 11:10 JST, 21 Aug.'),
    (4, 'Activity time: around 11:00 JST, 21 Aug.'),
    (5, 'Activity time: around 21 Aug.'),  # only the UTC day is valid, so it stays in UTC
])
def test_an_approximate_activity_time(du, line):
    received = datetime.datetime(2026, 8, 21, 15, 0, tzinfo=datetime.UTC)
    report = nmea.Decoder(with_fields(VOLCANO, [(50, 3, du)]), timestamp=received).decode()
    assert line in report.get_text_en().splitlines()


def test_an_activity_time_of_a_month_or_a_year_is_not_shown():
    report = azarashi.decode(with_fields(VOLCANO, [(50, 3, 6)]))
    assert not any(line.startswith('Activity time') for line in report.get_text_en().splitlines())


def _run(monkeypatch, capsys, path, *options):
    monkeypatch.setattr(sys, 'argv', ['azarashi', 'nmea', '-f', str(path), *options])
    code = cli.main()
    return code, capsys.readouterr()


def test_the_command_shows_english(monkeypatch, capsys, tmp_path):
    path = tmp_path / 'messages.log'
    path.write_text(HYPOCENTER + '\n', encoding='utf-8')
    code, out = _run(monkeypatch, capsys, path, '--english')
    assert code == 0
    assert azarashi.decode(HYPOCENTER).get_text_en() in out.out
    assert not JAPANESE.search(out.out)


def test_the_command_shows_japanese_where_there_is_no_english(monkeypatch, capsys, tmp_path):
    nankai = next(r for r in _reports() if isinstance(r, Nankai))
    path = tmp_path / 'messages.log'
    path.write_text(nankai.nmea + '\n', encoding='utf-8')
    code, out = _run(monkeypatch, capsys, path, '--english')
    assert code == 0
    assert '南海トラフ' in out.out


@pytest.mark.parametrize('option', ['--json', '--verbose'])
def test_the_command_refuses_english_with(option, monkeypatch, capsys, tmp_path):
    path = tmp_path / 'messages.log'
    path.write_text(HYPOCENTER + '\n', encoding='utf-8')
    with pytest.raises(SystemExit):
        _run(monkeypatch, capsys, path, '--english', option)
    assert '--english cannot be combined' in capsys.readouterr().err
