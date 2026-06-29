"""DCR (MT43, JMA Disaster Prevention Information) decoding tests."""
import azarashi

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
# Same report, different satellite/sentence framing -> equal report
EEW_DUP = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'


def test_eew_fields():
    p = azarashi.decode(EEW, 'nmea').get_params()
    assert p['message_type'] == 'DCR'
    assert p['disaster_category'] == '緊急地震速報'
    assert p['magnitude'] == '7.2'
    assert p['depth_of_hypocenter'] == '10km'
    assert p['seismic_epicenter'] == '日向灘'
    assert p['seismic_intensity_lower_limit'] == '震度6弱'
    assert p['seismic_intensity_upper_limit'] == '〜程度以上'
    assert '福岡' in p['eew_forecast_regions']


def test_eew_str_renders():
    s = str(azarashi.decode(EEW, 'nmea'))
    assert '緊急地震速報' in s
    assert 'マグニチュード: 7.2' in s


def test_equal_reports_are_equal_and_hashable():
    a = azarashi.decode(EEW, 'nmea')
    b = azarashi.decode(EEW_DUP, 'nmea')
    assert a == b                       # same underlying raw payload
    assert hash(a) == hash(b)           # hashable, consistent with __eq__
    assert len({a, b}) == 1             # usable as set members
