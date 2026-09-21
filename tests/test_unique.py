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
    """Deliver the first copy through the public API at an earlier reception time."""
    received = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=seconds_old)
    stream = io.StringIO(MSG * 2)
    azarashi.decode_stream(stream, unique=True, timestamp=received)
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


def test_mutating_a_delivered_report_does_not_change_duplicate_history():
    stream = io.StringIO(MSG * 2)
    report = azarashi.decode_stream(stream, unique=True)
    report.raw = b'edited'
    report.timestamp += datetime.timedelta(days=1)
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, unique=True)


def test_callback_mutation_does_not_change_reception_time_or_reservation(monkeypatch):
    start = datetime.datetime(2026, 9, 21, tzinfo=datetime.UTC)
    times = iter([start, start + datetime.timedelta(seconds=61), start + datetime.timedelta(seconds=62)])
    decode = DI.decode
    monkeypatch.setattr(DI, 'decode', lambda msg, msg_type, timestamp: decode(msg, msg_type, next(times)))
    seen = []

    def callback(report):
        seen.append(report)
        report.raw = b'edited'
        report.timestamp += datetime.timedelta(days=1)

    with pytest.raises(EOFError):
        azarashi.decode_stream(io.StringIO(MSG * 3), unique=60, callback=callback)
    assert len(seen) == 2


def test_mutating_failed_callback_does_not_leave_a_reservation():
    stream = io.StringIO(MSG * 2)

    def fail(report):
        report.raw = b'edited'
        raise ValueError('delivery failed')

    with pytest.raises(ValueError, match='delivery failed'):
        azarashi.decode_stream(stream, unique=True, callback=fail)
    assert azarashi.decode_stream(stream, unique=True) == azarashi.decode(MSG.strip())


def test_history_does_not_keep_the_delivered_report_alive():
    import gc
    import weakref

    stream = io.StringIO(MSG)
    report = azarashi.decode_stream(stream, unique=True)
    ref = weakref.ref(report)
    del report
    gc.collect()
    assert ref() is None


def test_callback_mutation_keeps_inflight_suppression():
    import threading

    stream = io.StringIO(MSG * 2)
    entered, release = threading.Event(), threading.Event()
    errors, completed = [], []

    def callback(report):
        report.raw = b'edited'
        entered.set()
        completed.append(release.wait(5))

    def deliver():
        try:
            azarashi.decode_stream(stream, unique=True, callback=callback)
        except EOFError:
            pass
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=deliver)
    thread.start()
    try:
        assert entered.wait(5)
        with pytest.raises(EOFError):
            azarashi.decode_stream(stream, unique=True)
    finally:
        release.set()
        thread.join(5)
    assert not thread.is_alive() and errors == [] and completed == [True]


def test_report_reference_to_its_stream_does_not_leak_through_history():
    import gc
    import weakref

    stream = io.StringIO(MSG)
    report = azarashi.decode_stream(stream, unique=True)
    report.application_stream = stream
    ref = weakref.ref(stream)
    del report, stream
    gc.collect()
    assert ref() is None
