"""The exceptions azarashi raises: hierarchy, messages and the sentence they show."""
import ast
import pathlib

import pytest

import azarashi
from azarashi import exceptions
from qzqsm import nmea_checksum
from qzqsm import sfrbx
from samples import EEW

PACKAGE = pathlib.Path(azarashi.__file__).parent
#: the classes that exist to be caught, not to be raised
GROUPING = ('AzarashiException', 'AzarashiReadOn', 'AzarashiDecodeError',
            'AzarashiReopenStream', 'AzarashiStopReading', 'AzarashiFixTheCall')
#: the names that existed before the classes were renamed
EARLIER = (azarashi.QzssDcrDecoderException,
           azarashi.QzssDcrDecoderNotImplementedError)
#: the failures that no earlier name catches. The released versions have no name of their own
#: for a stream that failed, for the end of the data, or for a read timeout. A mistake in the call
#: they did name as a decoder failure, and that is what a reading loop retried without end.
OUTSIDE_EARLIER = ('AzarashiDisconnectedError', 'AzarashiStreamClosedError', 'AzarashiNoMoreData',
                   'AzarashiTimeoutError', 'AzarashiUnsupportedFormatError', 'AzarashiArgumentTypeError')


def _built():
    """Where the package builds one of its own exceptions, whether it raises or returns it."""
    defined = {name for name, cls in vars(exceptions).items()
                  if isinstance(cls, type) and issubclass(cls, BaseException)
                  and cls.__module__ == exceptions.__name__}
    for path in sorted(PACKAGE.rglob('*.py')):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in defined:
                yield f'{path.relative_to(PACKAGE)}:{node.lineno}', node.func.id


class _Instance:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


@pytest.mark.parametrize('cls', [azarashi.AzarashiInvalidMessageError, azarashi.AzarashiNotImplementedError,
                                 azarashi.AzarashiReopenStream])
@pytest.mark.parametrize('instance, text', [
    (None, 'Bad'),
    (_Instance(), 'Bad'),
    (_Instance(sentence='$QZQSM,55'), 'Bad -> $QZQSM,55'),
    (_Instance(sentence='$QZQSM,55', nmea='$QZQSM,56'), 'Bad -> $QZQSM,56'),  # the NMEA form is preferred
    (_Instance(sentence='$QZQSM,55', nmea=''), 'Bad -> $QZQSM,55'),
    (_Instance(sentence=''), 'Bad'),  # a blank line read from a serial port
    (_Instance(sentence=b''), 'Bad'),
    (_Instance(sentence=b'\xB5\x62\x02'), "Bad -> b'\\xB5\\x62\\x02'"),
    (_Instance(sentence=bytearray(b'\xB5')), "Bad -> bytearray(b'\\xb5')"),
])
def test_str_shows_the_sentence(cls, instance, text):
    error = cls('Bad', instance)
    assert (error.message, error.instance, str(error)) == ('Bad', instance, text)
    assert error.args == ('Bad',)


#: what a layer that knows nothing of azarashi has to conclude from each class
STANDARD_BASES = {
    'AzarashiException': set(),
    'AzarashiReadOn': set(),
    # bad data, which is what json.JSONDecodeError and UnicodeDecodeError are too
    'AzarashiDecodeError': {ValueError},
    'AzarashiInvalidMessageError': {ValueError},
    # not NotImplementedError: that one, and the RuntimeError under it, mean code left unwritten
    'AzarashiNotImplementedError': {ValueError},
    # nothing: not an EOFError, which would end a live stream, and not a TimeoutError, which is
    # an OSError and would put it among the failures of the stream itself
    'AzarashiTimeoutError': set(),
    'AzarashiReopenStream': {OSError},
    'AzarashiDisconnectedError': {OSError},
    'AzarashiStreamClosedError': {OSError},
    'AzarashiStopReading': {EOFError},
    'AzarashiNoMoreData': {EOFError},
    # nothing of its own: its two kinds of mistake are each the one Python names for them
    'AzarashiFixTheCall': set(),
    # a value the call does not take, as int('x') raises
    'AzarashiUnsupportedFormatError': {ValueError},
    # an argument of the wrong kind, as Python's own calls raise; not a ValueError, which a layer
    # that knows nothing of azarashi would take for bad data to skip
    'AzarashiArgumentTypeError': {TypeError},
}
CANDIDATES = (OSError, EOFError, ValueError, TypeError, RuntimeError, NotImplementedError, TimeoutError,
              ArithmeticError)


def test_hierarchy():
    for name, expected in STANDARD_BASES.items():
        cls = getattr(azarashi, name)
        assert issubclass(cls, Exception), name  # never a bare BaseException, which would dodge 'except Exception'
        caught = {base for base in CANDIDATES if issubclass(cls, base)}
        assert caught == expected, name


def test_every_exception_is_covered_by_the_standard_bases_table():
    defined = {name for name, cls in vars(exceptions).items()
               if isinstance(cls, type) and issubclass(cls, BaseException) and cls.__module__ == exceptions.__name__}
    assert defined == set(STANDARD_BASES)


def test_one_clause_catches_every_decode_failure():
    for cls in (azarashi.AzarashiInvalidMessageError, azarashi.AzarashiNotImplementedError):
        assert issubclass(cls, azarashi.AzarashiDecodeError)
    assert not issubclass(azarashi.AzarashiNotImplementedError, azarashi.AzarashiInvalidMessageError)
    assert not issubclass(azarashi.AzarashiTimeoutError, azarashi.AzarashiDecodeError)  # nothing failed to decode
    for cls in (azarashi.AzarashiDecodeError, azarashi.AzarashiTimeoutError):
        assert issubclass(cls, azarashi.AzarashiReadOn)


def test_every_exception_is_built_and_read_the_same_way():
    # the hierarchy splits them, but the interface must not: the same constructor and the same
    # attributes, so one handler can report any of them
    for name, cls in sorted(vars(exceptions).items()):
        if not (isinstance(cls, type) and issubclass(cls, BaseException)
                and cls.__module__ == exceptions.__name__):
            continue
        error = cls('Bad')
        assert (error.message, error.instance, str(error), error.args) == ('Bad', None, 'Bad', ('Bad',)), name


def test_one_clause_catches_everything_azarashi_raises():
    # the base says only that azarashi is what failed, so it is safe to have every one under it:
    # nothing reads on because it caught this one
    for name, cls in sorted(vars(exceptions).items()):
        if (isinstance(cls, type) and issubclass(cls, BaseException)
                and cls.__module__ == exceptions.__name__ and cls is not azarashi.AzarashiException):
            assert issubclass(cls, azarashi.AzarashiException), name


def test_a_broken_stream_is_outside_the_classes_that_mean_read_on_and_stop():
    # AzarashiReadOn says the next message can be read, EOFError says the data ended. A broken
    # stream is neither, and being outside both is what keeps any clause order from taking it
    # for one of them.
    for cls in (azarashi.AzarashiReadOn, EOFError):
        assert not issubclass(azarashi.AzarashiReopenStream, cls)
    assert issubclass(azarashi.AzarashiReopenStream, OSError)  # what the streams themselves raise


def test_a_mistake_in_the_call_gets_past_every_reading_loop():
    # a reading loop catches what says how to go on; a wrong call has no way on, so nothing it
    # catches may take it, whatever the order of the clauses and whichever earlier name they use
    for cls in (azarashi.AzarashiReadOn, azarashi.AzarashiReopenStream, azarashi.AzarashiStopReading,
                EOFError, OSError, *EARLIER):
        assert not issubclass(azarashi.AzarashiFixTheCall, cls), cls
    for cls in (azarashi.AzarashiUnsupportedFormatError, azarashi.AzarashiArgumentTypeError):
        assert issubclass(cls, azarashi.AzarashiFixTheCall)


def test_the_package_builds_its_exceptions_somewhere():
    assert len(list(_built())) > 40  # the scan below proves nothing if it finds nothing


def test_the_grouping_classes_are_never_raised():
    # they say what to do next, so raising one would leave the caller unable to tell what happened
    assert [where for where, name in _built() if name in GROUPING] == []


def test_everything_raised_is_caught_by_the_earlier_names():
    # code written against the earlier names must keep catching every failure, so no leaf may sit outside them
    assert [f'{where} {name}' for where, name in _built()
            if name not in OUTSIDE_EARLIER and not issubclass(getattr(exceptions, name), EARLIER)] == []


def test_a_stream_failure_reaches_the_earlier_names_as_an_os_error():
    # the streams raise errors of their own, e.g. serial.SerialException, which are OSErrors:
    # staying an OSError is what keeps the handling written for those working
    assert not issubclass(azarashi.AzarashiReopenStream, EARLIER)
    assert issubclass(azarashi.AzarashiReopenStream, OSError)


def test_the_end_of_the_data_reaches_the_earlier_names_as_an_eof_error():
    # staying an EOFError is what keeps 'except EOFError' working
    assert not issubclass(azarashi.AzarashiNoMoreData, EARLIER)
    assert issubclass(azarashi.AzarashiNoMoreData, EOFError)


@pytest.mark.parametrize('earlier, current', [
    (azarashi.QzssDcrDecoderException, azarashi.AzarashiInvalidMessageError),
    (azarashi.QzssDcrDecoderNotImplementedError, azarashi.AzarashiNotImplementedError),
])
def test_the_earlier_names_are_the_same_classes(earlier, current):
    assert earlier is current


def test_decoder_errors_carry_the_decoder_and_the_cause():
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(EEW[:-2] + 'ZZ')
    assert excinfo.value.instance.sentence == EEW[:-2] + 'ZZ'
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert str(excinfo.value) == f'Invalid Checksum -> {EEW[:-2]}ZZ'


def test_frame_errors_show_the_frame():
    frame = sfrbx(EEW)[:-1] + b'\x00'
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(frame, 'ublox')
    shown = "b'" + ''.join(f'\\x{byte:02X}' for byte in frame) + "'"
    assert str(excinfo.value) == f'{excinfo.value.message} -> {shown}'
    assert shown.startswith("b'\\xB5\\x62\\x02\\x13")


def test_message_errors_show_the_message_as_nmea():
    broken = EEW[:-4] + '0*' + nmea_checksum(EEW[1:-4] + '0')  # the last message bits change: the CRC no longer matches
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(sfrbx(broken), 'ublox')
    assert str(excinfo.value) == f'CRC Mismatch -> {broken}'
