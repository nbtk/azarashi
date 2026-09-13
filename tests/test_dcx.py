"""DCX (MT44) decoding regression tests.

These lock in behaviour that regressed in the 0.16.3 line:
- EX9 J-Alert prefecture bitmask (must list the actual target prefectures)
- B1 refined ellipse values computed at full precision, rounded once at the end
- spec display precision (lat/lon 6dp, angle 5dp, distance 3dp)
"""
import datetime
import locale

import pytest

import azarashi
from azarashi.qzss_dcr_lib.decoder import NmeaQzssDcrDecoder
from test_dcr import _with_field

UTC = datetime.timezone.utc

# DCX message (L-Alert), B1 with no refinement (c1..c4 = 0)
L_ALERT = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E'
# DCX message (L-Alert), B1 with non-zero refinement (c1=c2=c3=c4 != 0)
L_ALERT_B1 = '$QZQSM,53,53B08408E0588979E00066AFFE8E6F700912000000000000000001000A1B690*08'
# DCX message (J-Alert), EX9 prefecture list = the seven Kyushu prefectures
J_ALERT = '$QZQSM,57,C6B0840DE3E21171208800000000000000000FE00000000000000000B8C7F50*72'


def test_l_alert_basic():
    p = azarashi.decode(L_ALERT, 'nmea').get_params()
    assert p['message_type'] == 'DCX'
    assert p['dcx_message_type'] == 'L-Alert'
    assert p['a12_ellipse_centre_latitude'] == 35.688258      # lat, 6dp
    assert p['a13_ellipse_centre_longitude'] == 139.690855    # lon, 6dp
    assert p['a14_ellipse_semi_major_axis'] == 10.933         # km, 3dp
    assert p['a15_ellipse_semi_minor_axis'] == 5.979          # km, 3dp
    assert p['a16_ellipse_azimuth'] == 45.0                   # deg, 5dp


def test_l_alert_precision_matches_spec_digits():
    p = azarashi.decode(L_ALERT, 'nmea').get_params()
    # latitude / longitude: 10^-6 deg
    for k in ('a12_ellipse_centre_latitude', 'a13_ellipse_centre_longitude'):
        assert p[k] == round(p[k], 6)
    # angle: 10^-5 deg
    assert p['a16_ellipse_azimuth'] == round(p['a16_ellipse_azimuth'], 5)
    # distance: 1 m (3dp in km)
    for k in ('a14_ellipse_semi_major_axis', 'a15_ellipse_semi_minor_axis'):
        assert p[k] == round(p[k], 3)


def test_b1_refined_values_round_at_end():
    # c1=c2=2, c3=c4=1. Refined values are computed from the unrounded grid
    # position/length and rounded once at the end (not from the 3dp/6dp display
    # values). These ground-truth values fail if intermediate rounding creeps back.
    p = azarashi.decode(L_ALERT_B1, 'nmea').get_params()
    assert p['a17_type_of_specific_settings'].startswith('B1')
    assert p['c1_refined_latitude_of_centre_of_main_ellipse'] == -17.79881
    assert p['c2_refined_longitude_of_centre_of_main_ellipse'] == 177.970947
    assert p['c3_refined_length_of_semi_major_axis'] == 723.258
    assert p['c4_refined_length_of_semi_minor_axis'] == 723.258


def test_b1_no_refinement_equals_base():
    # L_ALERT has c1..c4 = 0, so the refined centre/axes equal the base A12-A15.
    p = azarashi.decode(L_ALERT, 'nmea').get_params()
    assert p['c1_refined_latitude_of_centre_of_main_ellipse'] == p['a12_ellipse_centre_latitude']
    assert p['c2_refined_longitude_of_centre_of_main_ellipse'] == p['a13_ellipse_centre_longitude']
    assert p['c3_refined_length_of_semi_major_axis'] == p['a14_ellipse_semi_major_axis']
    assert p['c4_refined_length_of_semi_minor_axis'] == p['a15_ellipse_semi_minor_axis']


def test_jalert_ex9_prefecture_list():
    # Regression for the EX9 prefecture bitmask: this J-Alert targets the seven
    # Kyushu prefectures. A wrong bit alignment yields a different list or [].
    p = azarashi.decode(J_ALERT, 'nmea').get_params()
    assert p['dcx_message_type'] == 'J-Alert'
    assert p['ex8_target_area_list_type'] == 'Prefecture code'
    assert p['ex9_target_area_list_ja'] == [
        '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県']
    assert p['ex9_target_area_list'] == [
        'Fukuoka', 'Saga', 'Nagasaki', 'Kumamoto', 'Oita', 'Miyazaki', 'Kagoshima']


def test_str_does_not_crash():
    for m in (L_ALERT, L_ALERT_B1, J_ALERT):
        assert isinstance(str(azarashi.decode(m, 'nmea')), str)


def _decode_at(sentence, timestamp):
    """Decode as if the sentence had been received at `timestamp`."""
    return NmeaQzssDcrDecoder(sentence, timestamp=timestamp).decode()


def _with_hazard_onset(sentence, week, time_of_week):
    return _with_field(_with_field(sentence, 49, 1, week), 50, 14, time_of_week)  # A6: 1 bit, A7: 14 bits


@pytest.mark.parametrize('week, code, time_of_week, minutes', [
    (0, 1, 'MONDAY - 00:00 AM', 0),
    (0, 2, 'MONDAY - 00:01 AM', 1),
    (0, 720, 'MONDAY - 11:59 AM', 719),
    (0, 721, 'MONDAY - 00:00 PM', 720),
    (0, 9421, 'SUNDAY - 01:00 PM', 9420),
    (0, 10080, 'SUNDAY - 11:59 PM', 10079),
    (1, 3, 'MONDAY - 00:02 AM', 7 * 24 * 60 + 2),  # the example in the spec: next week, 2 minutes after midnight
])
def test_hazard_onset(week, code, time_of_week, minutes):
    received = datetime.datetime(2026, 9, 13, 23, 59, tzinfo=UTC)  # a Sunday: the week started on Monday the 7th
    p = _decode_at(_with_hazard_onset(L_ALERT, week, code), received).get_params()
    assert p['a7_hazard_onset_time_of_week'] == time_of_week
    assert p['a6a7_hazard_onset_datetime'] == datetime.datetime(2026, 9, 7, tzinfo=UTC) + datetime.timedelta(minutes=minutes)


def test_hazard_onset_is_written_in_utc_with_z():
    report = _decode_at(L_ALERT, datetime.datetime(2026, 9, 13, tzinfo=UTC))
    assert 'A6A7 - Hazard onset: 2026-09-13T13:00:00Z\n' in str(report)


def test_hazard_onset_week_follows_the_reception_time():
    received = datetime.datetime(2024, 6, 21, 15, 9, 5, tzinfo=UTC)  # the README example
    p = _decode_at(L_ALERT, received).get_params()
    assert p['a6a7_hazard_onset_datetime'] == datetime.datetime(2024, 6, 23, 13, 0, tzinfo=UTC)
    report = azarashi.decode(L_ALERT)  # with the default timestamp: the time of decoding
    week_start = report.timestamp.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    week_start -= datetime.timedelta(days=week_start.weekday())
    assert report.a6a7_hazard_onset_datetime == week_start + datetime.timedelta(minutes=9420)


@pytest.mark.parametrize('code, time_of_week', [
    (0, 'NOT USED'),
    (10081, 'RESERVED (Code: 10081)'),
    (16383, 'RESERVED (Code: 16383)'),
])
def test_hazard_onset_not_used_or_reserved(code, time_of_week):
    p = azarashi.decode(_with_hazard_onset(L_ALERT, 0, code), 'nmea').get_params()
    assert (p['a7_hazard_onset_time_of_week'], p['a6a7_hazard_onset_datetime']) == (time_of_week, None)


def test_hazard_onset_does_not_depend_on_the_locale():
    saved = locale.setlocale(locale.LC_TIME)
    try:
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    except locale.Error:
        pytest.skip('the ja_JP.UTF-8 locale is not available')
    try:
        p = _decode_at(L_ALERT, datetime.datetime(2026, 9, 13, tzinfo=UTC)).get_params()
    finally:
        locale.setlocale(locale.LC_TIME, saved)
    assert p['a7_hazard_onset_time_of_week'] == 'SUNDAY - 01:00 PM'
