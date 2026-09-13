"""DCR (MT43, JMA Disaster Prevention Information) decoding tests."""
import pytest

import azarashi

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
# Same report, different satellite/sentence framing -> equal report
EEW_DUP = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'
# Hypocenter (training/test message)
HYPOCENTER = '$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A'


def _with_field(sentence, pos, size, value):
    """Return the sentence with one message field replaced and its CRC and checksum recomputed."""
    bits = int(sentence.split(',')[2].split('*')[0], 16) >> 2  # 250-bit message
    shift = 250 - pos - size
    bits = bits & ~(((1 << size) - 1) << shift) | value << shift
    crc = 0
    for i in range(226):  # CRC-24Q over everything but the CRC field
        crc ^= (bits >> (249 - i) & 1) << 23
        crc = (crc << 1) ^ 0x1864cfb if crc & 0x800000 else crc << 1
    bits = bits & ~0xffffff | crc & 0xffffff
    body = f'QZQSM,{sentence.split(",")[1]},{bits << 2:063X}'
    checksum = 0
    for c in body:
        checksum ^= ord(c)
    return f'${body}*{checksum:02X}'


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


def test_invalid_longitude_minute_names_the_minute():
    lon_m_pos = 122 + 29  # hypocenter coordinates start at bit 122; longitude minutes are 6 bits at +29
    coordinates = azarashi.decode(HYPOCENTER, 'nmea').coordinates_of_hypocenter
    assert coordinates['lon_d'] != 60
    assert _with_field(HYPOCENTER, lon_m_pos, 6, coordinates['lon_m']) == HYPOCENTER  # the helper round-trips
    with pytest.raises(azarashi.QzssDcrDecoderException) as e:
        azarashi.decode(_with_field(HYPOCENTER, lon_m_pos, 6, 60), 'nmea')
    assert e.value.message == 'Invalid Longitude: 60 as minute'
