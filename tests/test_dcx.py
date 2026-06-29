"""DCX (MT44) decoding regression tests.

These lock in behaviour that regressed in the 0.16.3 line:
- EX9 J-Alert prefecture bitmask (must list the actual target prefectures)
- B1 refined ellipse values computed at full precision, rounded once at the end
- spec display precision (lat/lon 6dp, angle 5dp, distance 3dp)
"""
import azarashi

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
