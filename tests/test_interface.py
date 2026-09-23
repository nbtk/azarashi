"""decode() and decode_stream(): message types, how streams are read, filtering, callbacks and per-stream state."""
import gc
import io
import weakref

import pytest

import azarashi
from azarashi.streams import hex_qzss_dcr_message_extractor
from azarashi.streams import nmea_qzss_dcr_message_extractor
from azarashi.streams import ublox_qzss_dcr_message_extractor
from azarashi.streams.state import ReaderStore
from azarashi.streams.state import StreamKeyedDict
from qzqsm import hex_message
from qzqsm import sfrbx
from qzqsm import ubx
from qzqsm import with_fields
from samples import EEW
from samples import L_ALERT


class _Closable:  # cannot be weakly referenced, reports whether it is closed
    __slots__ = ('closed',)

    def __init__(self):
        self.closed = False


class _Nothing:
    pass


# decode()

@pytest.mark.parametrize('msg', ['', b''])
def test_decode_nothing_is_an_invalid_message(msg):
    # an empty message is a message that cannot be read. No stream ended, so this must not be an
    # EOFError: a reading loop would take that for the end of the data.
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(msg)
    assert str(excinfo.value) == 'Empty Message'
    assert not isinstance(excinfo.value, EOFError)


def test_decode_unknown_message_type():
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError) as excinfo:
        azarashi.decode(EEW, 'rtcm')
    assert str(excinfo.value) == 'Unknown Message Type: rtcm'


@pytest.mark.parametrize('fmt', ['hex', 'net', 'nmea'])
def test_decoders_take_nothing_as_an_invalid_message(fmt):
    from azarashi import decoders
    with pytest.raises(azarashi.AzarashiInvalidMessageError):
        getattr(decoders, fmt).Decoder('').decode()


# decode_stream(): how streams are read

def test_decode_stream_unknown_message_type():
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError) as excinfo:
        azarashi.decode_stream(io.BytesIO(), 'rtcm')
    assert str(excinfo.value) == 'Unknown Message Type: rtcm'


@pytest.mark.parametrize('operation', [azarashi.decode_stream, azarashi.reset_reading_state])
def test_net_is_not_a_stream_format_and_consumes_no_input(operation):
    stream = io.BytesIO(bytes((55,)) + azarashi.decode(EEW).message)
    with pytest.raises(azarashi.AzarashiUnsupportedFormatError) as error:
        operation(stream, 'net')
    assert str(error.value) == "Message Type net is not a stream format; use decode(data, 'net') for each datagram"
    assert stream.tell() == 0


@pytest.mark.parametrize('msg_type, message', [
    ('nmea', "readline() does not exist: <class 'test_interface._Nothing'>"),
    ('spresense', "readline() does not exist: <class 'test_interface._Nothing'>"),
    ('hex', "readline() does not exist: <class 'test_interface._Nothing'>"),
    ('ublox', "Neither read() nor read1() exists: <class 'test_interface._Nothing'>"),
])
def test_decode_stream_needs_a_reader(msg_type, message):
    with pytest.raises(azarashi.AzarashiArgumentTypeError) as excinfo:
        azarashi.decode_stream(_Nothing(), msg_type)
    assert str(excinfo.value) == message


def test_ublox_from_a_text_stream_reads_its_buffer():
    stream = io.TextIOWrapper(io.BytesIO(sfrbx(EEW)))
    assert not hasattr(stream, 'read1')
    assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW)


@pytest.mark.parametrize('msg_type, data', [
    ('nmea', f'{EEW}\r\n'.encode()),
    ('spresense', f'{EEW}\r\n'.encode()),
    ('hex', f'{hex_message(EEW)}\n'.encode()),
    ('ublox', sfrbx(EEW)),
])
def test_every_message_type_from_a_stream(msg_type, data):
    assert azarashi.decode_stream(io.BytesIO(data), msg_type) == azarashi.decode(EEW)


# decode_stream(): filtering and callbacks

@pytest.mark.parametrize('kwargs, expected', [
    ({}, ['DCR', 'DCR']),  # DCX is ignored by default
    ({'ignore_dcx': False}, ['DCR', 'DCX', 'DCR']),
    ({'ignore_dcr': True, 'ignore_dcx': False}, ['DCX']),
    ({'ignore_dcr': True}, []),
])
def test_message_type_filters(kwargs, expected):
    stream = io.StringIO(f'{EEW}\n{L_ALERT}\n{with_fields(EEW, [(0, 8, 0x9A)])}\n')
    received = []
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, callback=lambda report: received.append(report.message_type), **kwargs)
    assert received == expected


def test_callback_arguments():
    received = []

    def callback(report, *args, **kwargs):
        received.append((report, args, kwargs))

    with pytest.raises(EOFError):
        azarashi.decode_stream(io.StringIO(f'{EEW}\n'), callback=callback, callback_args=(1, 2),
                               callback_kwargs={'key': 'value'})
    assert received == [(azarashi.decode(EEW), (1, 2), {'key': 'value'})]


def test_decoder_errors_leave_the_stream_readable():
    stream = io.StringIO(f'{EEW[:-2]}00\n{EEW}\n')
    with pytest.raises(azarashi.AzarashiInvalidMessageError):
        azarashi.decode_stream(stream)
    assert azarashi.decode_stream(stream) == azarashi.decode(EEW)


# message extractors

def test_line_extractors_read_without_arguments():
    assert nmea_qzss_dcr_message_extractor(io.StringIO(f'$GPGGA,,*00\nnoise{EEW}\n').readline) == f'{EEW}\n'
    assert hex_qzss_dcr_message_extractor(io.BytesIO(b'\xffABC\n').readline) == '�ABC\n'


def test_ublox_extractor_reads_without_arguments():
    assert ublox_qzss_dcr_message_extractor(io.BytesIO(sfrbx(EEW)).read1) == sfrbx(EEW)


@pytest.mark.parametrize('skipped', [
    sfrbx(EEW, gnss=0),  # GPS
    sfrbx(EEW, sig=0),  # not L1S
    sfrbx(with_fields(EEW, [(8, 6, 42)])),  # neither DCR nor DCX
    ubx(b'\x02\x13', bytes((5, 0, 1, 0, 0, 0, 2, 0))),  # no data words
])
def test_ublox_extractor_skips_other_frames(skipped):
    assert azarashi.decode_stream(io.BytesIO(skipped + sfrbx(EEW)), 'ublox') == azarashi.decode(EEW)


class _Parts:
    """read1() hands out the parts one by one, an empty part being an empty read."""

    def __init__(self, *parts):
        self._parts = list(parts)

    def read1(self, size=-1):
        return self._parts.pop(0) if self._parts else b''


def test_ublox_false_header_at_the_end_of_the_data():
    frame = sfrbx(EEW)
    false_header = b'\xB5\x62\x02\x13\x28\x00'  # a plausible length, but a real frame follows within it
    stream = _Parts(false_header + frame[:40], b'', b'', frame[40:])  # the first empty read only rescans
    with pytest.raises(EOFError):
        azarashi.decode_stream(stream, 'ublox')
    assert azarashi.decode_stream(stream, 'ublox') == azarashi.decode(EEW)


# per-stream state

def test_stream_keyed_dict_drops_closed_streams_that_cannot_be_weakly_referenced():
    values = StreamKeyedDict()
    stream, other = _Closable(), _Closable()
    values[stream] = 'cache'
    values[other] = 'other cache'
    assert values.get(stream) == 'cache'
    stream.closed = True
    assert values.get(other) == 'other cache'
    assert values.get(stream) is None


def test_stream_keyed_dict_clear():
    values = StreamKeyedDict()
    weak, strong = io.BytesIO(), _Closable()
    values[weak] = 1
    values[strong] = 2
    values.clear()
    assert (values.get(weak), values.get(strong)) == (None, None)


def test_stream_state_is_released_with_its_owner():
    values = StreamKeyedDict()
    stream, state = io.StringIO(), _Nothing()
    stream_ref, state_ref = weakref.ref(stream), weakref.ref(state)
    values[stream] = state
    del stream, state
    gc.collect()
    assert stream_ref() is None and state_ref() is None


def test_closed_weakly_referenced_stream_keeps_its_state():
    # Reopening the same serial object must retain its duplicate history.
    values = StreamKeyedDict()
    stream = io.StringIO()
    values[stream] = 'history'
    stream.close()
    assert values.get(stream) == 'history'


def test_reader_store_keeps_one_value_per_reader():
    store = ReaderStore(bytearray)
    stream = io.BytesIO()
    assert store.get(stream.read1) is store.get(stream.read1)
    assert store.get(stream.read1) is not store.get(stream.readline)
    assert store.get(len) is store.get(len)  # not a bound method
    store.get(stream.read1).extend(b'left over')
    store.clear()
    assert store.get(stream.read1) == bytearray() and store.get(len) == bytearray()


def test_reader_store_distinguishes_equal_unhashable_callables():
    class Reader:
        __hash__ = None

        def __eq__(self, other):
            return isinstance(other, Reader)

        def __call__(self):
            return b''

    store = ReaderStore(list)
    first, second = Reader(), Reader()
    store.get(first).append('pending')
    assert store.get(first) == ['pending']
    assert store.get(second) == []


def test_reader_store_keeps_none_factory_result():
    calls = []

    def factory():
        calls.append(1)
        return None

    def reader():
        return b''

    store = ReaderStore(factory)
    assert store.get(reader) is None
    assert store.get(reader) is None
    assert calls == [1]


@pytest.mark.parametrize('failure_at', ['property', 'truth_value'])
def test_closed_inspection_failure_keeps_state_and_does_not_poison_other_streams(failure_at):
    class BadTruth:
        def __bool__(self):
            raise ValueError('cannot tell whether closed')

    class Stream:
        __slots__ = ('fail',)

        def __init__(self):
            self.fail = True

        @property
        def closed(self):
            if self.fail:
                if failure_at == 'property':
                    raise RuntimeError('closed unavailable')
                return BadTruth()
            return True

    store = StreamKeyedDict()
    source, other = Stream(), _Closable()
    store[source], store[other] = 'retained', 'other'
    assert store.get(other) == 'other'
    assert store.get(source) == 'retained'
    source.fail = False
    assert store.get(source) is None
    assert store.get(other) == 'other'


def test_closed_inspection_does_not_swallow_process_interrupts():
    class Stream:
        __slots__ = ()

        @property
        def closed(self):
            raise KeyboardInterrupt

    store = StreamKeyedDict()
    source = Stream()
    store[source] = 'retained'
    with pytest.raises(KeyboardInterrupt):
        store.get(source)


@pytest.mark.parametrize('ignore, kept', [
    ({'ignore_dcx': 1}, ['DCR']),       # 1 is as true as True
    ({'ignore_dcx': 0}, ['DCR', 'DCX']),
    ({'ignore_dcr': 1, 'ignore_dcx': False}, ['DCX']),
])
def test_ignore_flags_take_any_truth_value(ignore, kept):
    reports = []
    with pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(io.StringIO(EEW + '\n' + L_ALERT + '\n'), callback=reports.append, **ignore)
    assert [report.message_type for report in reports] == kept
