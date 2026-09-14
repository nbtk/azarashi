"""Volcano (JMA-DC Report) activity time: ambiguity, validity and the inferred date."""
from datetime import datetime
from datetime import timezone

import pytest

import azarashi
from qzqsm import with_fields

# Volcano (training/test message): reported 2026-03-07 05:10 UTC, activity at the same time with no ambiguity
VOLCANO = '$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70'


def _with_activity_time(ambiguity, day, hour, minute, sentence=VOLCANO):
    return with_fields(sentence, [(50, 3, ambiguity), (53, 5, day), (58, 5, hour), (63, 6, minute)])


def _date_line(report):
    lines = [line for line in str(report).splitlines() if line.startswith('日時')]
    return lines[0] if lines else None


@pytest.mark.parametrize('ambiguity, hour, minute, valid_time, line', [
    (0, 20, 0, (20, 0), '日時: 3月7日5時0分'),
    (1, 20, 0, (20, 0), '日時: 3月7日5時0分頃'),
    (2, 20, 0, (20, 0), '日時: 3月7日5時0分頃'),
    (3, 20, 0, (20, 0), '日時: 3月7日5時0分頃'),
    (4, 20, 63, (20, 0), '日時: 3月7日5時頃'),  # the minute is not valid
    (5, 31, 63, (0, 0), '日時: 3月6日頃'),  # the hour and minute are not valid; the day is written as sent
])
def test_volcano_activity_time(ambiguity, hour, minute, valid_time, line):
    report = azarashi.decode(_with_activity_time(ambiguity, 6, hour, minute), 'nmea')
    assert report.activity_time == datetime(report.report_time.year, 3, 6, *valid_time, tzinfo=timezone.utc)
    assert report.activity_time_raw == {'day': 6, 'hour': hour, 'minute': minute}
    assert _date_line(report) == line


@pytest.mark.parametrize('ambiguity', [6, 7])
def test_volcano_activity_time_without_valid_values(ambiguity):
    report = azarashi.decode(_with_activity_time(ambiguity, 0, 31, 63), 'nmea')  # month or year: nothing is valid
    assert report.activity_time is None
    assert report.activity_time_raw == {'day': 0, 'hour': 31, 'minute': 63}
    assert _date_line(report) is None
    assert '火山名: 阿蘇山\n現象: 噴火\n' in str(report)


@pytest.mark.parametrize('report_month, report_day, day, years_before, month', [
    (3, 7, 7, 0, 3),  # the day of the report
    (3, 7, 6, 0, 3),
    (3, 7, 20, 0, 2),  # observed before the report, so the previous month
    (3, 7, 30, 0, 1),  # February has no 30th
    (1, 5, 20, 1, 12),  # the previous year
])
def test_volcano_activity_date_is_not_after_the_report(report_month, report_day, day, years_before, month):
    sentence = with_fields(VOLCANO, [(21, 4, report_month), (25, 5, report_day)])  # report time: month, day
    report = azarashi.decode(_with_activity_time(5, day, 0, 0, sentence), 'nmea')
    assert report.activity_time == datetime(report.report_time.year - years_before, month, day, tzinfo=timezone.utc)
    assert report.activity_time <= report.report_time


@pytest.mark.parametrize('ambiguity, day, hour, minute, code', [  # the code is the whole field (16 bits)
    (0, 6, 24, 0, 13824),
    (3, 6, 20, 60, 13628),
    (4, 6, 24, 63, 13887),
    (5, 0, 0, 0, 0),  # the day is valid for this ambiguity, but day 0 is not a day
    (5, 0, 31, 63, 2047),  # activity time unknown until IS-QZSS-DCR-015
])
def test_volcano_activity_time_out_of_range(ambiguity, day, hour, minute, code):
    report = azarashi.decode(_with_activity_time(ambiguity, day, hour, minute), 'nmea')
    assert report.activity_time is None
    assert report.activity_time_raw == {'day': day, 'hour': hour, 'minute': minute}
    assert _date_line(report) == f'日時: 日時(コード番号：{code})'
