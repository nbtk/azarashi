"""The exceptions azarashi raises: hierarchy, messages and the sentence they show."""
import pytest

import azarashi
from qzqsm import nmea_checksum
from qzqsm import sfrbx

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'


class _Instance:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


@pytest.mark.parametrize('exception', [azarashi.QzssDcrDecoderException, azarashi.QzssDcrDecoderNotImplementedError])
@pytest.mark.parametrize('instance, text', [
    (None, 'Bad'),
    (_Instance(), 'Bad'),
    (_Instance(sentence='$QZQSM,55'), 'Bad -> $QZQSM,55'),
    (_Instance(sentence='$QZQSM,55', nmea='$QZQSM,56'), 'Bad -> $QZQSM,56'),  # the NMEA form is preferred
    (_Instance(sentence='$QZQSM,55', nmea=''), 'Bad -> $QZQSM,55'),
    (_Instance(sentence=b'\xB5\x62\x02'), "Bad -> b'\\xB5\\x62\\x02'"),
    (_Instance(sentence=bytearray(b'\xB5')), "Bad -> bytearray(b'\\xb5')"),
])
def test_str_shows_the_sentence(exception, instance, text):
    error = exception('Bad', instance)
    assert (error.message, error.instance, str(error)) == ('Bad', instance, text)
    assert error.args == ('Bad',)


def test_hierarchy():
    assert issubclass(azarashi.QzssDcrDecoderException, Exception)
    assert issubclass(azarashi.QzssDcrDecoderNotImplementedError, NotImplementedError)
    assert issubclass(azarashi.QzssDcrDecoderTimeoutError, EOFError)  # existing EOF handling keeps working
    assert not issubclass(azarashi.QzssDcrDecoderException, EOFError)


def test_decoder_errors_carry_the_decoder_and_the_cause():
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        azarashi.decode(EEW[:-2] + 'ZZ')
    assert excinfo.value.instance.sentence == EEW[:-2] + 'ZZ'
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert str(excinfo.value) == f'Invalid Checksum -> {EEW[:-2]}ZZ'


def test_frame_errors_show_the_frame():
    frame = sfrbx(EEW)[:-1] + b'\x00'
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        azarashi.decode(frame, 'ublox')
    shown = "b'" + ''.join(f'\\x{byte:02X}' for byte in frame) + "'"
    assert str(excinfo.value) == f'{excinfo.value.message} -> {shown}'
    assert shown.startswith("b'\\xB5\\x62\\x02\\x13")


def test_message_errors_show_the_message_as_nmea():
    broken = EEW[:-4] + '0*' + nmea_checksum(EEW[1:-4] + '0')  # the last message bits change: the CRC no longer matches
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        azarashi.decode(sfrbx(broken), 'ublox')
    assert str(excinfo.value) == f'CRC Mismatch -> {broken}'
