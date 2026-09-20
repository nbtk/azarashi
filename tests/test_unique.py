"""decode_stream(unique=...) deduplication behaviour.

unique=True  -> suppress duplicates indefinitely (released default behaviour)
unique=False -> no deduplication
unique=<sec> -> re-report a duplicate last seen more than <sec> seconds ago
"""
import datetime
import io

import pytest

import azarashi
from azarashi import api as DI

MSG = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05\n'


def _run(stream, unique):
    calls = []
    try:
        azarashi.decode_stream(stream, 'nmea', callback=calls.append,
                               unique=unique, ignore_dcr=False)
    except EOFError:
        pass
    return len(calls)


def _seeded_stale(seconds_old):
    """A stream of one message, with an identical cached report aged `seconds_old`."""
    DI.caches.clear()
    cached = azarashi.decode(MSG.strip(), 'nmea')
    cached.timestamp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=seconds_old)
    stream = io.StringIO(MSG)
    DI.caches[stream] = [cached]
    return stream


def test_unique_false_no_dedup():
    DI.caches.clear()
    assert _run(io.StringIO(MSG + MSG), False) == 2


def test_unique_true_suppresses_duplicates():
    DI.caches.clear()
    assert _run(io.StringIO(MSG + MSG), True) == 1


def test_unique_true_never_expires():
    assert _run(_seeded_stale(100000), True) == 0  # still suppressed regardless of age


def test_unique_seconds_expiry():
    assert _run(_seeded_stale(2.0), 1) == 1        # 2s old, threshold 1s -> re-fire
    assert _run(_seeded_stale(0.5), 1) == 0        # 0.5s old, threshold 1s -> suppress


def test_unique_accepts_float():
    assert _run(_seeded_stale(2.0), 1.5) == 1
    assert _run(_seeded_stale(1.0), 1.5) == 0


def test_unique_zero_and_negative_disable_dedup():
    DI.caches.clear()
    assert _run(io.StringIO(MSG + MSG), 0) == 2
    DI.caches.clear()
    assert _run(io.StringIO(MSG + MSG), -5) == 2


@pytest.mark.parametrize('offsets, delivered', [
    ([0, 30, 60, 120, 181], [0, 181]),  # every suppressed copy refreshes the last reception
    ([0, 0, 0], [0]),  # a fixed replay timestamp does not expire
    ([0, -10, 20, 81], [0, 81]),  # reception time, even when the clock moves backwards
])
def test_unique_seconds_uses_the_last_reception_time(monkeypatch, offsets, delivered):
    start = datetime.datetime(2026, 3, 10, tzinfo=datetime.UTC)
    times = iter(start + datetime.timedelta(seconds=offset) for offset in offsets)
    decode = DI.decode

    def at_reception(msg, msg_type, timestamp):
        return decode(msg, msg_type, timestamp=next(times))

    monkeypatch.setattr(DI, 'decode', at_reception)
    reports = []
    with pytest.raises(azarashi.AzarashiStopReading):
        azarashi.decode_stream(io.StringIO(MSG * len(offsets)), unique=60, callback=reports.append)
    assert [(report.timestamp - start).total_seconds() for report in reports] == delivered
