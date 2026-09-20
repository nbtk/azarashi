"""Behaviour shared by every report: equality, hashing, parameters and the fallbacks of the base classes."""
import azarashi
from azarashi.reports.base import Base
from azarashi.reports.base import MessagePartial
from qzqsm import with_fields
from samples import EEW
from samples import L_ALERT


def test_reports_of_the_same_message_are_equal():
    a = azarashi.decode(EEW)
    b = azarashi.decode(with_fields(EEW.replace(',55,', ',58,'), [(0, 8, 0x53)]))  # another satellite and preamble
    assert (a == b, hash(a) == hash(b), a != b) == (True, True, False)


def test_reports_of_other_messages_are_not_equal():
    a = azarashi.decode(EEW)
    assert a != azarashi.decode(with_fields(EEW, [(35, 6, 11)]))  # another report minute
    assert a != azarashi.decode(L_ALERT)
    assert a != a.raw and a != str(a) and a is not None


def test_the_raw_message_leaves_out_what_differs_between_satellites():
    dcr = azarashi.decode(EEW)
    assert dcr.raw == dcr.message[1:27] + bytes((dcr.message[27] & 0xF0,))  # without the preamble and the CRC
    dcx = azarashi.decode(L_ALERT)
    assert dcx.raw == dcx.message[3:27] + bytes((dcx.message[27] & 0xF0,))  # from the CAMF, without the designation mask


def test_get_params_is_a_copy():
    report = azarashi.decode(EEW)
    params = report.get_params()
    params['eew_forecast_regions'].append('どこか')
    params['magnitude'] = '9.9'
    assert report.magnitude == '7.2' and 'どこか' not in report.eew_forecast_regions


def test_base_report():
    report = Base('sentence', raw=b'raw')
    assert str(report) == str(report.__dict__)
    assert (report.sentence, report.raw) == ('sentence', b'raw')
    assert report.timestamp.utcoffset().total_seconds() == 0
    assert Base('sentence').raw == b''


def test_message_is_the_sentence_when_there_is_none():
    message = azarashi.decode(EEW).message
    report = MessagePartial(message=message, nmea=EEW)
    assert report.sentence is message


def test_dcx_camf_fields():
    report = azarashi.decode(L_ALERT)
    assert report.camf.get_params() == report.camf.__dict__
    assert report.camf.get_params() is not report.camf.__dict__  # a copy, as a report's get_params() gives
    assert str(report.camf) == str(report.camf.__dict__)
    assert repr(report.camf).startswith('CAMF(sdmt=')  # an address would say nothing and never repeat
    assert report.camf.a2 == 111
