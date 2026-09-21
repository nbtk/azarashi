"""Behaviour shared by every report: equality, hashing, parameters and the fallbacks of the base classes."""
import pytest

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


def test_get_params_leaves_out_absent_dcx_fields_and_copies_camf():
    report = azarashi.decode(L_ALERT)
    params = report.get_params()
    assert report.a11_international_library is None
    assert 'a11_international_library' not in params
    params['camf'].a2 = 0
    assert report.camf.a2 == 111


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


# Public construction/mutation/subclassing contracts, independent of decoder internals.
def _construction_samples():
    from qzqsm import jma, sentence
    return [jma(dc, []) for dc in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14)] + [
        sentence([(8, 6, 44)]), L_ALERT,
    ]


@pytest.mark.parametrize('sentence', _construction_samples())
def test_reports_can_be_constructed_from_their_declared_fields(sentence, monkeypatch):
    from datetime import UTC, datetime
    from azarashi.reports.dcr import NankaiTroughEarthquake

    monkeypatch.setattr(NankaiTroughEarthquake, 'reports', {})
    monkeypatch.setattr(NankaiTroughEarthquake, 'announcement', None)
    monkeypatch.setattr(NankaiTroughEarthquake, 'completed', False)
    original = azarashi.decode(sentence, timestamp=datetime(2026, 9, 21, tzinfo=UTC))
    supplied = original.get_params()
    restored = type(original)(**supplied)
    assert restored == original and hash(restored) == hash(original)
    assert str(restored) == str(original)
    left, right = original.get_params(), restored.get_params()
    if 'camf' in left:
        left['camf'], right['camf'] = vars(left['camf']), vars(right['camf'])
    assert left == right


def test_report_mutation_does_not_redecode_related_fields():
    report = azarashi.decode(EEW)
    raw, message, nmea, magnitude_code = report.raw, report.message, report.nmea, report.magnitude_raw
    report.magnitude = '9.9'
    report.eew_forecast_regions.append('利用者の追記')
    report.application_note = {'tags': ['reviewed']}
    snapshot = report.get_params()
    assert snapshot['magnitude'] == '9.9'
    assert snapshot['eew_forecast_regions'][-1] == '利用者の追記'
    snapshot['application_note']['tags'].append('copied')
    assert report.application_note == {'tags': ['reviewed']}
    assert (report.raw, report.message, report.nmea, report.magnitude_raw) == (raw, message, nmea, magnitude_code)


def test_report_subclasses_keep_methods_and_concrete_type_equality():
    from azarashi.reports.dcr import EarthquakeEarlyWarning

    class AnnotatedWarning(EarthquakeEarlyWarning):
        def summary(self):
            return f'M{self.magnitude}'

    original = azarashi.decode(EEW)
    first = AnnotatedWarning(**original.get_params())
    second = AnnotatedWarning(**original.get_params())
    assert first.summary() == 'M7.2'
    assert str(first) == str(original)
    assert first == second and hash(first) == hash(second)
    assert first != original and original != first
