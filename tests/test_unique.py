"""decode_stream(unique=...) deduplication behaviour.

unique=True  -> suppress duplicates indefinitely (released default behaviour)
unique=False -> no deduplication
unique=<sec> -> re-report a duplicate last seen more than <sec> seconds ago
"""
import datetime
import io

import azarashi
from azarashi.qzss_dcr_lib.interface import decoder_interface as DI

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
    cached.timestamp = datetime.datetime.now() - datetime.timedelta(seconds=seconds_old)
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
