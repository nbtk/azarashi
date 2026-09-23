"""Mistakes in a call: refused with AzarashiFixTheCall, and before anything is read.

A mistake in the call is decided by the arguments alone, so the same call can never succeed and a
reading loop must not retry it. Every check runs before the stream is touched, so a message
already waiting is still there for the next call made right. The one thing that cannot be known
before reading is whether a stream gives text or bytes, which shows at its first read.
"""
import datetime
import io
from decimal import Decimal
from fractions import Fraction

import pytest

import azarashi
from samples import EEW

FORMAT = azarashi.AzarashiUnsupportedFormatError
KIND = azarashi.AzarashiArgumentTypeError


class _Counting(io.StringIO):
    """A line source that counts the reads made from it."""

    def __init__(self, text):
        super().__init__(text)
        self.reads = 0

    def readline(self, *args):
        self.reads += 1
        return super().readline(*args)


class _Nothing:
    pass


class _Keys:
    """A mapping to ** without being registered as a Mapping."""

    def keys(self):
        return ['sep']

    def __getitem__(self, key):
        return '|'


def test_both_kinds_of_mistake_get_past_a_reading_loop():
    for error in (FORMAT, KIND):
        assert issubclass(error, azarashi.AzarashiFixTheCall)
        assert not issubclass(error, (azarashi.AzarashiReadOn, azarashi.AzarashiReopenStream, EOFError))
    assert issubclass(FORMAT, ValueError) and issubclass(KIND, TypeError)


# decode()

@pytest.mark.parametrize('msg_type, error', [('rtcm', FORMAT), ('', FORMAT), (0, KIND), (None, KIND)])
def test_decode_refuses_a_format_it_does_not_read(msg_type, error):
    with pytest.raises(error):
        azarashi.decode(EEW, msg_type)


@pytest.mark.parametrize('msg', [12345, None, memoryview(EEW.encode()), [EEW]], ids=type)
def test_decode_refuses_a_message_that_is_neither_text_nor_bytes(msg):
    with pytest.raises(KIND, match='msg must be str or bytes'):
        azarashi.decode(msg)


@pytest.mark.parametrize('timestamp', ['2026-01-01T00:00:00Z', 0, datetime.date(2026, 1, 1)], ids=type)
def test_decode_refuses_a_timestamp_that_is_not_a_datetime(timestamp):
    with pytest.raises(KIND, match='timestamp must be a datetime'):
        azarashi.decode(EEW, timestamp=timestamp)


def test_decode_still_takes_what_a_message_is():
    assert azarashi.decode(bytearray(EEW, 'ascii')) == azarashi.decode(EEW)
    with pytest.raises(azarashi.AzarashiInvalidMessageError):  # empty is a message that cannot be read
        azarashi.decode('')


# decode_stream()

@pytest.mark.parametrize('arguments, error', [
    ({'msg_type': 'rtcm'}, FORMAT),
    ({'msg_type': 'net'}, FORMAT),
    ({'msg_type': 0}, KIND),
    ({'callback': 123}, KIND),
    ({'callback': print, 'callback_args': 5}, KIND),
    ({'callback': print, 'callback_kwargs': ['sep']}, KIND),
    ({'callback': print, 'callback_kwargs': {1: '|'}}, KIND),
    ({'unique': 'yes'}, KIND),
    ({'unique': [60]}, KIND),
    ({'timestamp': 'now'}, KIND),
], ids=lambda value: str(value) if isinstance(value, dict) else '')
def test_decode_stream_refuses_a_wrong_call_before_it_reads(arguments, error):
    stream = _Counting(EEW + '\n')
    with pytest.raises(error):
        azarashi.decode_stream(stream, **arguments)
    assert stream.reads == 0
    assert azarashi.decode_stream(stream) == azarashi.decode(EEW)  # the waiting message was not lost


@pytest.mark.parametrize('msg_type', ['nmea', 'spresense', 'hex', 'ublox'])
def test_decode_stream_refuses_a_stream_without_its_reader(msg_type):
    with pytest.raises(KIND):
        azarashi.decode_stream(_Nothing(), msg_type)


def test_decode_stream_refuses_a_stream_that_gives_the_wrong_kind():
    with pytest.raises(KIND, match='open the stream in binary mode'):
        azarashi.decode_stream(io.StringIO('text'), 'ublox')

    class Numbers:
        def readline(self):
            return 5

    with pytest.raises(KIND, match='a line is read as str or bytes'):
        azarashi.decode_stream(Numbers(), 'nmea')


def test_decode_stream_takes_a_read_that_brought_nothing():
    class Idle:  # a non-blocking raw stream with nothing to give yet
        def read(self, size):
            return None

    with pytest.raises(azarashi.AzarashiStopReading):
        azarashi.decode_stream(Idle(), 'ublox')


@pytest.mark.parametrize('arguments', [
    {'unique': None}, {'unique': 1}, {'unique': 60.0}, {'unique': Decimal('60')}, {'unique': Fraction(1, 2)},
    {'callback': lambda report, *extra: None, 'callback_args': ['x']},
    {'callback': lambda report, *extra: None, 'callback_args': iter(['x'])},
    {'callback': lambda report, **extra: None, 'callback_kwargs': _Keys()},
], ids=lambda value: str(value))
def test_decode_stream_still_takes_what_worked(arguments):
    with pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(io.StringIO(EEW + '\n'), **{'callback': lambda report: None, **arguments})


# reset_reading_state()

@pytest.mark.parametrize('stream, msg_type, error', [
    (io.StringIO(), 'rtcm', FORMAT),
    (io.StringIO(), 'net', FORMAT),
    (io.StringIO(), 0, KIND),
    (_Nothing(), 'nmea', KIND),
])
def test_reset_refuses_a_wrong_call(stream, msg_type, error):
    with pytest.raises(error):
        azarashi.reset_reading_state(stream, msg_type)


# the JSON conversion

@pytest.mark.parametrize('convert', [azarashi.to_json_dict, azarashi.to_ndjson])
def test_the_json_conversion_refuses_what_is_not_a_report(convert):
    with pytest.raises(KIND, match='Unsupported report type'):
        convert(object())
