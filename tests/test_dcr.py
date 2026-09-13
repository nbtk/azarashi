"""DCR (MT43, JMA Disaster Prevention Information) decoding tests."""
import pytest

import azarashi

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
# Same report, different satellite/sentence framing -> equal report
EEW_DUP = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'
# Hypocenter (training/test message)
HYPOCENTER = '$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A'
# Flood (training/test message)
FLOOD = '$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E'
# Tsunami (training/test message), three forecast regions arriving at 04:05 UTC
TSUNAMI = '$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F'
# Northwest Pacific tsunami (training/test messages): one region that has arrived or is unknown,
# and five coastal regions with arrival times (the first at 14:46 UTC)
NWP_ARRIVED_OR_UNKNOWN = '$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C'
NWP = '$QZQSM,56,9AAD3609E080023AE008D3D1008E449009D457009E3E5011F00000138B3E720*09'


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


def _with_arrival_time(sentence, region, day, hour, minute):
    """Return the tsunami sentence with the expected arrival time of one forecast region replaced."""
    pos = 84 + region * 26  # expected arrival time: day (1 bit), hour (5 bits), minute (6 bits)
    sentence = _with_field(sentence, pos, 1, day)
    sentence = _with_field(sentence, pos + 1, 5, hour)
    return _with_field(sentence, pos + 6, 6, minute)


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


@pytest.mark.parametrize('code, name', [  # added or renamed in IS-QZSS-DCR-017
    (880801000200, '石手川(愛媛県)'),
    (880802000103, '肱川水系肱川(菅田〜鹿野川)(愛媛県)'),
    (890907000103, '矢部川中流部(福岡県)'),
    (890907000100, '矢部川下流部(福岡県)'),
    (890917000100, '番匠川水系(大分県)'),
])
def test_flood_forecast_regions(code, name):
    report = azarashi.decode(_with_field(FLOOD, 53 + 4, 40, code), 'nmea')  # region of the first flood warning
    assert report.flood_forecast_regions_raw == [code]
    assert report.flood_forecast_regions == [name]


def test_tsunami_arrival_times():
    sentence = _with_arrival_time(TSUNAMI, 1, 0, 31, 63)  # the tsunami has arrived
    sentence = _with_arrival_time(sentence, 2, 0, 30, 62)  # no data (IS-QZSS-DCR-017)
    report = azarashi.decode(sentence, 'nmea')
    arrival = report.expected_tsunami_arrival_times[0]
    assert (arrival.hour, arrival.minute) == (4, 5)
    assert report.expected_tsunami_arrival_times[1:] == [None, None]
    assert report.expected_tsunami_arrival_times_raw == [{'day': 0, 'hour': 4, 'minute': 5},
                                                         {'day': 0, 'hour': 31, 'minute': 63},
                                                         {'day': 0, 'hour': 30, 'minute': 62}]
    assert report.expected_tsunami_arrival_time_types == ['津波の到達予想時刻', '津波到達中と推測', '該当情報なし']
    assert [line for line in str(report).splitlines() if line.startswith('津波到達予想時刻')] == [
        f'津波到達予想時刻: {report.convert_dt_to_str(arrival)}',
        '津波到達予想時刻: 津波到達中と推測',
        '津波到達予想時刻: 該当情報なし',
    ]


@pytest.mark.parametrize('day, hour, minute, time_type', [
    (0, 31, 0, '津波到達中と推測'),  # the hour decides first, as before
    (1, 4, 63, '津波到達中と推測'),
    (0, 30, 0, '該当情報なし'),
    (0, 4, 62, '該当情報なし'),
    (1, 23, 59, '津波の到達予想時刻'),
])
def test_tsunami_arrival_time_types(day, hour, minute, time_type):
    report = azarashi.decode(_with_arrival_time(TSUNAMI, 0, day, hour, minute), 'nmea')
    assert report.expected_tsunami_arrival_time_types[0] == time_type
    assert (report.expected_tsunami_arrival_times[0] is None) == (time_type != '津波の到達予想時刻')
    assert report.expected_tsunami_arrival_times_raw[0] == {'day': day, 'hour': hour, 'minute': minute}


@pytest.mark.parametrize('code, height', [
    (13, '該当情報なし'),  # added in IS-QZSS-DCR-017
    (14, '不明'),
    (12, '津波の高さ(コード番号：12)'),
])
def test_tsunami_heights(code, height):
    report = azarashi.decode(_with_field(TSUNAMI, 84 + 12, 4, code), 'nmea')  # height of the first forecast region
    assert (report.tsunami_heights[0], report.tsunami_heights_raw[0]) == (height, code)


@pytest.mark.parametrize('hour, minute, message', [
    (24, 0, 'Invalid JMA Expected Tsunami Arrivale Time: 24 as hour'),
    (29, 63, 'Invalid JMA Expected Tsunami Arrivale Time: 29 as hour'),
    (4, 60, 'Invalid JMA Expected Tsunami Arrivale Time: 60 as minute'),
    (4, 61, 'Invalid JMA Expected Tsunami Arrivale Time: 61 as minute'),
])
def test_tsunami_arrival_time_out_of_range(hour, minute, message):
    with pytest.raises(azarashi.QzssDcrDecoderException) as e:
        azarashi.decode(_with_arrival_time(TSUNAMI, 0, 0, hour, minute), 'nmea')
    assert e.value.message == message


def _with_nwp_arrival_time(sentence, region, day, hour, minute):
    """Return the Northwest Pacific tsunami sentence with the arrival time of one coastal region replaced."""
    pos = 56 + region * 28  # expected arrival time: day (1 bit), hour (5 bits), minute (6 bits)
    sentence = _with_field(sentence, pos, 1, day)
    sentence = _with_field(sentence, pos + 1, 5, hour)
    return _with_field(sentence, pos + 6, 6, minute)


def test_northwest_pacific_tsunami_arrival_times():
    report = azarashi.decode(_with_nwp_arrival_time(NWP, 1, 0, 31, 63), 'nmea')
    first = report.expected_tsunami_arrival_times[0]
    assert (first.hour, first.minute) == (14, 46)
    assert report.expected_tsunami_arrival_times[1] is None
    assert [(r['hour'], r['minute']) for r in report.expected_tsunami_arrival_times_raw[:2]] == [(14, 46), (31, 63)]
    assert report.expected_tsunami_arrival_times_raw[1]['day'] == 0
    assert report.expected_tsunami_arrival_time_types == ['Expected Tsunami Arrival Time', 'Arrived or Unknown'] + \
        ['Expected Tsunami Arrival Time'] * 3
    lines = [line for line in str(report).splitlines() if line.startswith('Expected Tsunami Arrival Time')]
    assert lines[:2] == [f'Expected Tsunami Arrival Time: {report.convert_dt_to_str_iso(first)}',
                         'Expected Tsunami Arrival Time: Arrived or Unknown']


def test_northwest_pacific_tsunami_arrived_or_unknown_sample():
    report = azarashi.decode(NWP_ARRIVED_OR_UNKNOWN, 'nmea')
    assert report.expected_tsunami_arrival_times == [None]
    assert report.expected_tsunami_arrival_time_types == ['Arrived or Unknown']
    assert 'Expected Tsunami Arrival Time: Arrived or Unknown\n' in str(report)


@pytest.mark.parametrize('hour, minute, time_type', [
    (31, 0, 'Arrived or Unknown'),  # the hour decides first, as for JMA-DC Report (Tsunami)
    (4, 63, 'Arrived or Unknown'),
    (23, 59, 'Expected Tsunami Arrival Time'),
])
def test_northwest_pacific_tsunami_arrival_time_types(hour, minute, time_type):
    report = azarashi.decode(_with_nwp_arrival_time(NWP, 0, 0, hour, minute), 'nmea')
    assert report.expected_tsunami_arrival_time_types[0] == time_type
    assert report.expected_tsunami_arrival_times_raw[0] == {'day': 0, 'hour': hour, 'minute': minute}


@pytest.mark.parametrize('hour, minute, message', [
    (30, 62, 'Invalid JMA Expected Tsunami Arrivale Time: 30 as hour'),  # "no data" is only for JMA-DC Report (Tsunami)
    (4, 62, 'Invalid JMA Expected Tsunami Arrivale Time: 62 as minute'),
])
def test_northwest_pacific_tsunami_arrival_time_out_of_range(hour, minute, message):
    with pytest.raises(azarashi.QzssDcrDecoderException) as e:
        azarashi.decode(_with_nwp_arrival_time(NWP, 0, 0, hour, minute), 'nmea')
    assert e.value.message == message
