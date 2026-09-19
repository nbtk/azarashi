"""Every datetime the library returns carries a UTC timezone."""
import datetime
import io
import os

import azarashi
from azarashi.decoders import NmeaQzssDcrDecoder
from samples import EEW

TESTS = os.path.dirname(os.path.realpath(__file__))
UTC = datetime.UTC


def _datetimes(value, path):
    if isinstance(value, datetime.datetime):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _datetimes(item, f'{path}.{key}')
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _datetimes(item, f'{path}[]')


def test_every_datetime_is_utc():
    fields = set()
    for log in ('qzqsm_220307.log', 'qzqsm_dcx_240604.log'):
        with open(os.path.join(TESTS, log), encoding='utf-8') as f:
            for line in f:
                if not line.startswith('$QZQSM'):
                    continue
                report = azarashi.decode(line.strip())
                for path, value in _datetimes(report.get_params(), type(report).__name__):
                    assert value.tzinfo is not None and value.utcoffset() == datetime.timedelta(0), (path, value)
                    fields.add(path.split('.', 1)[1])
    assert {'timestamp', 'report_time', 'occurrence_time_of_earthquake', 'expected_tsunami_arrival_times[]',
            'activity_time', 'a6a7_hazard_onset_datetime'} <= fields


def test_default_timestamp_is_now_in_utc():
    before = datetime.datetime.now(UTC)
    report = azarashi.decode(EEW)
    assert report.timestamp.tzinfo is UTC
    assert before <= report.timestamp <= datetime.datetime.now(UTC)


def test_a_replayed_message_is_dated_from_the_given_time():
    received = datetime.datetime(2019, 5, 1, tzinfo=UTC)  # a message kept in a recording since 2019
    report = azarashi.decode(EEW, 'nmea', received)
    assert (report.timestamp, report.report_time.year) == (received, 2019)
    from_stream = azarashi.decode_stream(io.StringIO(EEW + '\r\n'), 'nmea', timestamp=received)
    assert (from_stream.timestamp, from_stream.report_time.year) == (received, 2019)


def test_given_timestamp_is_normalized_to_utc():
    naive = datetime.datetime(2026, 9, 13, 21, 0)  # taken as local time, like datetime.now()
    assert NmeaQzssDcrDecoder(EEW, timestamp=naive).decode().timestamp == naive.astimezone(UTC)
    jst = datetime.datetime(2026, 9, 13, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    report = NmeaQzssDcrDecoder(EEW, timestamp=jst).decode()
    assert (report.timestamp, report.timestamp.tzinfo) == (datetime.datetime(2026, 9, 13, 12, 0, tzinfo=UTC), UTC)
