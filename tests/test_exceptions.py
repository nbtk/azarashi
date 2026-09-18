"""The exceptions azarashi raises: hierarchy, messages and the sentence they show."""
import pytest

import azarashi
from qzqsm import nmea_checksum
from qzqsm import sfrbx
from samples import EEW


class _Instance:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


@pytest.mark.parametrize('exception', [azarashi.AzarashiInvalidMessageError, azarashi.AzarashiNotImplementedError])
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
def test_str_shows_the_sentence(exception, instance, text):
    error = exception('Bad', instance)
    assert (error.message, error.instance, str(error)) == ('Bad', instance, text)
    assert error.args == ('Bad',)


def test_hierarchy():
    assert issubclass(azarashi.AzarashiInvalidMessageError, Exception)
    assert issubclass(azarashi.AzarashiNotImplementedError, NotImplementedError)
    assert issubclass(azarashi.AzarashiTimeoutError, EOFError)  # existing EOF handling keeps working
    assert not issubclass(azarashi.AzarashiInvalidMessageError, EOFError)


def test_one_clause_catches_every_decode_failure():
    for exception in (azarashi.AzarashiInvalidMessageError, azarashi.AzarashiNotImplementedError):
        assert issubclass(exception, azarashi.AzarashiDecodeError)
    assert not issubclass(azarashi.AzarashiNotImplementedError, azarashi.AzarashiInvalidMessageError)
    assert not issubclass(azarashi.AzarashiTimeoutError, azarashi.AzarashiDecodeError)  # nothing failed to decode
    for exception in (azarashi.AzarashiDecodeError, azarashi.AzarashiTimeoutError):
        assert issubclass(exception, azarashi.AzarashiError)


@pytest.mark.parametrize('earlier, current', [
    (azarashi.QzssDcrDecoderException, azarashi.AzarashiInvalidMessageError),
    (azarashi.QzssDcrDecoderNotImplementedError, azarashi.AzarashiNotImplementedError),
    (azarashi.QzssDcrDecoderTimeoutError, azarashi.AzarashiTimeoutError),
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
