"""What decode_stream() reports when the device goes away, e.g. a USB serial adapter pulled out."""
import io
import os
import pathlib
import re
import socket
import sys
import threading
import time
import types

import pytest
import serial

import azarashi
from samples import EEW
from samples import FRAME

ROOT = pathlib.Path(__file__).resolve().parent.parent
#: the documents whose examples open a serial device
DOCUMENTS = ['README.md', 'docs/api.md']


@pytest.fixture
def pty():
    """A pySerial port on one end of a pty, and the other end to write to and then pull out."""
    master, slave = os.openpty()
    port = serial.Serial(os.ttyname(slave), 9600, timeout=None)
    try:
        yield master, port
    finally:
        port.close()
        os.close(slave)
        try:
            os.close(master)
        except OSError:  # the test pulled it out already
            pass


def test_a_device_pulled_out_is_a_stream_error(pty):
    master, port = pty
    os.write(master, EEW.encode() + b'\r\n')
    assert azarashi.decode_stream(port, msg_type='nmea').message_type == 'DCR'
    os.close(master)  # the device disappears
    time.sleep(0.1)
    with pytest.raises(azarashi.AzarashiReopenStream) as excinfo:
        azarashi.decode_stream(port, msg_type='nmea')
    assert isinstance(excinfo.value.__cause__, serial.SerialException)


def test_a_device_pulled_out_is_told_apart_from_a_stream_that_ended(pty):
    master, port = pty
    os.close(master)
    time.sleep(0.1)
    with pytest.raises(azarashi.AzarashiReopenStream):
        azarashi.decode_stream(port, msg_type='nmea')
    # a stream that ended raises EOFError, so the two do not need the same handling
    with pytest.raises(EOFError) as excinfo:
        azarashi.decode_stream(io.StringIO(''), msg_type='nmea')
    assert not isinstance(excinfo.value, azarashi.AzarashiReopenStream)


class _Unplugged:
    """A stream that fails the way pySerial does once the device is gone."""

    def __init__(self, error):
        self._error = error

    def readline(self, *args):
        raise self._error

    def read(self, *args):
        raise self._error

    read1 = read


@pytest.mark.parametrize('msg_type', ['nmea', 'hex', 'ublox'])
@pytest.mark.parametrize('error', [
    serial.SerialException('device reports readiness to read but returned no data'),
    serial.SerialException('read failed: [Errno 6] Device not configured'),
    OSError(5, 'Input/output error'),
])
def test_every_format_reports_a_failing_stream_the_same_way(msg_type, error):
    with pytest.raises(azarashi.AzarashiDisconnectedError) as excinfo:
        azarashi.decode_stream(_Unplugged(error), msg_type=msg_type)
    assert excinfo.value.__cause__ is error
    assert str(excinfo.value) == f'{type(error).__name__}: {error}'


@pytest.mark.parametrize('msg_type', ['nmea', 'hex', 'ublox'])
def test_no_clause_order_turns_a_failing_stream_into_something_else(msg_type):
    # AzarashiReadOn says the next message can be read and EOFError says the data ended, so a
    # pulled-out device must be taken for neither, whichever clause a caller happens to write first
    def caught(order):
        try:
            azarashi.decode_stream(_Unplugged(serial.SerialException('device disconnected')), msg_type=msg_type)
        except order[0]:
            return 'first'
        except order[1]:
            return 'second'
        except order[2]:
            return 'third'

    stream_error, read_on, ended = azarashi.AzarashiReopenStream, azarashi.AzarashiReadOn, EOFError
    assert caught((stream_error, read_on, ended)) == 'first'
    assert caught((read_on, ended, stream_error)) == 'third'
    assert caught((ended, read_on, stream_error)) == 'third'


@pytest.mark.parametrize('msg_type', ['nmea', 'hex', 'ublox'])
def test_handling_written_for_pyserial_still_catches_a_failing_stream(msg_type):
    # pySerial raises serial.SerialException, which is an OSError: handling written for that has to keep working
    with pytest.raises(OSError):
        azarashi.decode_stream(_Unplugged(serial.SerialException('device disconnected')), msg_type=msg_type)


@pytest.mark.parametrize('msg_type', ['nmea', 'hex', 'ublox'])
def test_a_stream_closed_under_azarashi_is_a_stream_error(tmp_path, msg_type):
    # an io object raises ValueError, not OSError, once it is closed; reopening a device does that
    path = tmp_path / 'closed.nmea'
    path.write_bytes(EEW.encode() + b'\r\n')
    stream = path.open('rb')
    stream.close()
    with pytest.raises(azarashi.AzarashiStreamClosedError) as excinfo:
        azarashi.decode_stream(stream, msg_type=msg_type)
    assert isinstance(excinfo.value.__cause__, ValueError)


def test_a_value_error_from_elsewhere_is_left_alone():
    # only a closed stream turns a ValueError into a stream error, so a bug in a reader still shows
    class Broken:
        closed = False

        def readline(self, *args):
            raise ValueError('a bug in the reader')

    with pytest.raises(ValueError) as excinfo:
        azarashi.decode_stream(Broken(), msg_type='nmea')
    assert not isinstance(excinfo.value, azarashi.AzarashiReadOn)


def _replug(port, slave):
    """Close and open the same port object on a new pty, the way a replugged device comes back."""
    port.close()
    os.close(slave)
    master, slave = os.openpty()
    port.port = os.ttyname(slave)
    port.open()
    return master, slave


def test_the_first_sentence_after_a_replug_is_not_lost():
    # a read timeout keeps the part of a line it managed to read. Once the device is gone the rest
    # can never arrive, so keeping it would corrupt the first sentence that follows the replug.
    master, slave = os.openpty()
    port = serial.Serial(os.ttyname(slave), 9600, timeout=0.2)
    try:
        os.write(master, EEW[:20].encode())  # no newline, so the read times out with a part in hand
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(port, msg_type='nmea')
        os.close(master)
        with pytest.raises(azarashi.AzarashiReopenStream):
            azarashi.decode_stream(port, msg_type='nmea')

        master, slave = _replug(port, slave)
        os.write(master, EEW.encode() + b'\r\n')
        assert azarashi.decode_stream(port, msg_type='nmea').message_type == 'DCR'
    finally:
        port.close()
        os.close(slave)
        os.close(master)


def test_the_first_frame_after_a_replug_is_not_lost():
    master, slave = os.openpty()
    port = serial.Serial(os.ttyname(slave), 9600, timeout=0.2)
    try:
        os.write(master, FRAME[:14])  # the header and part of the payload, then the cable goes
        with pytest.raises((azarashi.AzarashiReopenStream, azarashi.AzarashiTimeoutError)):
            azarashi.decode_stream(port, msg_type='ublox')
        os.close(master)
        with pytest.raises(azarashi.AzarashiReopenStream):
            azarashi.decode_stream(port, msg_type='ublox')

        master, slave = _replug(port, slave)
        os.write(master, FRAME)
        assert azarashi.decode_stream(port, msg_type='ublox').message_type == 'DCR'
    finally:
        port.close()
        os.close(slave)
        os.close(master)


def test_a_stream_that_fails_midway_through_a_frame_is_a_stream_error():
    class HalfFrame:
        def __init__(self):
            self._sent = False

        def read1(self, *args):
            if self._sent:
                raise serial.SerialException('device reports readiness to read but returned no data')
            self._sent = True
            return FRAME[:10]  # the header and part of the payload, then the cable goes

    with pytest.raises(azarashi.AzarashiReopenStream):
        azarashi.decode_stream(HalfFrame(), msg_type='ublox')


class _Spun(BaseException):
    """Raised at the read that proves an example kept reading a device that is gone.

    A BaseException so that an example catching Exception cannot swallow it and read on.
    """


class _Enough(BaseException):
    """Raised to end an example that reconnects, which would otherwise run forever.

    A BaseException for the same reason as _Spun: no example may catch it and carry on.
    """


class _Pulled:
    """A device that hands over one frame, is pulled out, and comes back when it is opened again."""

    #: reads to allow before deciding the example is spinning on a device that is gone
    READS_ALLOWED = 100
    #: reconnects to allow before ending an example that reconnects
    REOPENS_ALLOWED = 3

    def __init__(self, timeout=None):
        self.timeout = timeout
        self._frame = FRAME
        self.reads = 0
        self.reopens = 0

    def read1(self, *args):
        self.reads += 1
        if self.reads > self.READS_ALLOWED:
            raise _Spun(f'still reading after {self.reads} reads')
        if self._frame:
            frame, self._frame = self._frame, b''
            return frame
        raise serial.SerialException('device reports readiness to read but returned no data')

    read = read1

    def close(self):
        pass

    def open(self):
        self.reopens += 1
        if self.reopens > self.REOPENS_ALLOWED:
            raise _Enough(f'reconnected {self.reopens - 1} times')
        self._frame = FRAME  # the device is back, sending again
        self.reads = 0  # and the reads that follow are not a spin

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _device_examples():
    """Every documented example that opens a serial device and reads it in a loop."""
    found = {}
    for document in DOCUMENTS:
        text = (ROOT / document).read_text(encoding='utf-8')
        for i, (language, body) in enumerate(re.findall(r'```(\w*)\n(.*?)```', text, re.S)):
            if language == 'python' and 'serial.Serial' in body and 'while ' in body:
                found[f'{document} block {i}'] = body
    return found


DEVICE_EXAMPLES = _device_examples()


def _run_example(where, body, monkeypatch):
    """Run a documented example against a device that is pulled out, and return the device."""
    devices = []
    fake = types.ModuleType('serial')
    fake.Serial = lambda *args, **kwargs: devices.append(_Pulled(kwargs.get('timeout'))) or devices[-1]
    fake.SerialException = serial.SerialException
    monkeypatch.setitem(sys.modules, 'serial', fake)  # the examples import serial themselves
    clock = types.ModuleType('time')  # an example that waits for the device must not make the test wait
    clock.sleep = lambda seconds: None
    monkeypatch.setitem(sys.modules, 'time', clock)
    try:
        exec(compile(body, where, 'exec'), {'__name__': '__main__'})
    except (SystemExit, _Enough):  # the examples that end in exit(example()), and the ones that reconnect
        pass
    assert devices, f'{where} did not open the device'
    return devices[0]


def test_the_documented_examples_that_open_a_device_are_all_found():
    # the README loop, and the Minimal Loop, pySerial, Reconnect, Timeout and Field Receiver examples
    assert len(DEVICE_EXAMPLES) == 6, list(DEVICE_EXAMPLES)


@pytest.mark.parametrize('where', list(DEVICE_EXAMPLES))
def test_a_documented_example_handles_the_device_being_pulled_out(where, monkeypatch, capsys):
    # an example that keeps reading a device that is gone spins at full speed, so none may:
    # it either stops, or opens the device again
    try:
        device = _run_example(where, DEVICE_EXAMPLES[where], monkeypatch)
    except _Spun as e:
        pytest.fail(f'{where} kept reading the device that was pulled out: {e}')
    assert device.reads > 1  # the example really did read the device


def test_the_documented_reconnect_example_reopens_the_same_device(monkeypatch, capsys):
    where = next(w for w in DEVICE_EXAMPLES if 'ser.open()' in DEVICE_EXAMPLES[w])
    device = _run_example(where, DEVICE_EXAMPLES[where], monkeypatch)
    # the same object is reopened, which is what keeps the dedup memory across the reconnect
    assert device.reopens == _Pulled.REOPENS_ALLOWED + 1


def test_the_guard_notices_an_example_that_keeps_reading(monkeypatch, capsys):
    # a loop that swallows everything and reads on: the shape the guard above exists to catch
    spinning = ("import azarashi\n"
                "import serial\n"
                "with serial.Serial('/dev/ttyS0', 9600) as ser:\n"
                "    while True:\n"
                "        try:\n"
                "            azarashi.decode_stream(ser, msg_type='ublox', callback=print)\n"
                "        except EOFError:\n"
                "            break\n"
                "        except Exception:\n"
                "            pass\n")
    with pytest.raises(_Spun):
        _run_example('a spinning example', spinning, monkeypatch)


def test_a_failing_callback_is_not_turned_into_a_stream_error():
    # only reading the stream is wrapped: an OSError the callback raises has to reach the caller as it is
    error = OSError('Network is unreachable')

    def callback(report):
        raise error

    with pytest.raises(OSError) as excinfo:
        azarashi.decode_stream(io.StringIO(f'{EEW}\n'), msg_type='nmea', callback=callback)
    assert excinfo.value is error


def test_the_two_reasons_to_reopen_are_told_apart_and_caught_together():
    # a log line wants to know which happened; a reading loop only wants to know to reopen
    def raised(stream):
        try:
            azarashi.decode_stream(stream, msg_type='nmea')
        except azarashi.AzarashiReopenStream as e:  # the one clause covers both reasons
            return type(e)

    gone = _Unplugged(serial.SerialException('device disconnected'))
    closed = io.StringIO(f'{EEW}\n')
    closed.close()
    assert raised(gone) is azarashi.AzarashiDisconnectedError
    assert raised(closed) is azarashi.AzarashiStreamClosedError


@pytest.fixture
def idle_socket():
    """A socket with a read timeout that no data ever reaches, and a peer that stays connected."""
    server = socket.socket()
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    held = []
    thread = threading.Thread(target=lambda: held.append(server.accept()), daemon=True)
    thread.start()
    client = socket.create_connection(server.getsockname())
    thread.join(5)
    client.settimeout(0.2)
    try:
        yield client, held[0][0]
    finally:
        client.close()
        for conn, _ in held:
            conn.close()
        server.close()


@pytest.mark.parametrize('msg_type', ['nmea', 'hex', 'ublox'])
@pytest.mark.parametrize('buffering', [-1, 0], ids=['buffered', 'unbuffered'])
def test_a_file_over_a_socket_that_timed_out_needs_a_new_stream(idle_socket, msg_type, buffering):
    """A read timeout on socket.makefile() leaves the file unusable, so a new stream is the way on.

    Python says as much of makefile() with a timeout, and it holds: the TimeoutError is followed by
    OSError('cannot read from timed out object') however long the caller waits, even once the data
    it was waiting for has arrived. Reporting it as a read to try again would be a promise azarashi
    cannot keep.
    """
    client, conn = idle_socket
    stream = client.makefile('rb', buffering=buffering)
    with pytest.raises(azarashi.AzarashiReopenStream):
        azarashi.decode_stream(stream, msg_type=msg_type)

    conn.sendall(EEW.encode() + b'\r\n')  # the data it was waiting for, now that it is there
    time.sleep(0.1)
    with pytest.raises(azarashi.AzarashiReopenStream):
        azarashi.decode_stream(stream, msg_type=msg_type)


def test_a_socket_read_with_a_timeout_resumes_through_pyserial(idle_socket):
    """The way to read a socket with a timeout, which does keep what it read.

    pySerial's socket:// handler is a stream with a timeout attribute that hands over what it has
    instead of raising, which is the read timeout AzarashiTimeoutError stands for.
    """
    _, conn = idle_socket
    server = socket.socket()
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    accepted = []
    thread = threading.Thread(target=lambda: accepted.append(server.accept()), daemon=True)
    thread.start()
    port = serial.serial_for_url(f'socket://{server.getsockname()[0]}:{server.getsockname()[1]}', timeout=0.4)
    thread.join(5)
    peer = accepted[0][0]
    try:
        sentence = EEW.encode() + b'\r\n'
        peer.sendall(sentence[:30])
        with pytest.raises(azarashi.AzarashiTimeoutError):
            azarashi.decode_stream(port, msg_type='nmea')

        peer.sendall(sentence[30:])
        assert azarashi.decode_stream(port, msg_type='nmea').message_type == 'DCR'

        with pytest.raises(azarashi.AzarashiTimeoutError):  # and it can be read again after that
            azarashi.decode_stream(port, msg_type='nmea')
    finally:
        port.close()
        peer.close()
        server.close()


@pytest.mark.parametrize('mistake', ['unknown_format', 'net', 'missing_reader'])
def test_minimal_loop_stops_at_once_on_a_mistake_in_the_call(mistake, monkeypatch, capsys):
    # the documented loop catches the three classes that say how to go on, so a wrong call gets
    # through on the first try instead of being retried; counting calls catches a relapse into that
    section = (ROOT / 'docs/api.md').read_text().split('### Minimal Loop\n', 1)[1]
    body = re.search(r'```python\n(.*?)```', section, re.S).group(1)
    decode_stream = azarashi.decode_stream
    calls, devices = [], []

    def guarded(stream, *args, **kwargs):
        if len(calls) == 5:
            raise _Spun('configuration retried without consuming input')
        calls.append(1)
        devices.append(stream)
        fmt = {'unknown_format': 'invalid', 'net': 'net', 'missing_reader': 'nmea'}[mistake]
        return decode_stream(stream, fmt, *args[1:], **kwargs)

    monkeypatch.setattr(azarashi, 'decode_stream', guarded)
    with pytest.raises(azarashi.AzarashiFixTheCall):
        _run_example('Minimal Loop with configuration error', body, monkeypatch)
    assert len(calls) == 1
    assert all(device.reads == 0 and device.reopens == 0 for device in devices)
