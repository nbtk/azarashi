"""DCR (MT43, JMA Disaster Prevention Information) decoding tests."""
from datetime import datetime
from datetime import UTC

import pytest

import azarashi
from azarashi.decoders import nmea
from qzqsm import with_fields

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
# the same report with another preamble, and so another CRC
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


def _with_arrival_time(sentence, region, day, hour, minute):
    """Return the tsunami sentence with the expected arrival time of one forecast region replaced."""
    pos = 84 + region * 26  # expected arrival time: day (1 bit), hour (5 bits), minute (6 bits)
    return with_fields(sentence, [(pos, 1, day), (pos + 1, 5, hour), (pos + 6, 6, minute)])


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


def test_longitude_minute_out_of_range_makes_the_coordinates_a_code():
    lon_m_pos = 122 + 29  # hypocenter coordinates start at bit 122; longitude minutes are 6 bits at +29
    coordinates = azarashi.decode(HYPOCENTER, 'nmea').coordinates_of_hypocenter_raw
    assert coordinates['lon_m'] != 60
    assert with_fields(HYPOCENTER, [(lon_m_pos, 6, coordinates['lon_m'])]) == HYPOCENTER  # the helper round-trips
    report = azarashi.decode(with_fields(HYPOCENTER, [(lon_m_pos, 6, 60)]), 'nmea')
    assert report.coordinates_of_hypocenter == '緯度・経度(コード番号：280515596032)'
    assert report.coordinates_of_hypocenter_raw == {**coordinates, 'lon_m': 60}


@pytest.mark.parametrize('code, name', [  # added or renamed in IS-QZSS-DCR-017
    (880801000200, '石手川(愛媛県)'),
    (880802000103, '肱川水系肱川(菅田〜鹿野川)(愛媛県)'),
    (890907000103, '矢部川中流部(福岡県)'),
    (890907000100, '矢部川下流部(福岡県)'),
    (890917000100, '番匠川水系(大分県)'),
])
def test_flood_forecast_regions(code, name):
    report = azarashi.decode(with_fields(FLOOD, [(53 + 4, 40, code)]), 'nmea')  # the first flood warning region
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
    (1, 31, 63, '津波到達中と推測'),
    (1, 23, 59, '津波の到達予想時刻'),
    # only the combinations of IS-QZSS-DCR-017 are special values; the code is the whole field (12 bits)
    (0, 31, 0, '津波到達予想時刻(コード番号：1984)'),
    (1, 4, 63, '津波到達予想時刻(コード番号：2367)'),
    (0, 30, 0, '津波到達予想時刻(コード番号：1920)'),
    (0, 4, 62, '津波到達予想時刻(コード番号：318)'),
    (1, 30, 62, '津波到達予想時刻(コード番号：4030)'),  # no data is on day 0
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
    report = azarashi.decode(with_fields(TSUNAMI, [(84 + 12, 4, code)]), 'nmea')  # height of the first forecast region
    assert (report.tsunami_heights[0], report.tsunami_heights_raw[0]) == (height, code)


@pytest.mark.parametrize('hour, minute, code', [(24, 0, 1536), (29, 63, 1919), (4, 60, 316), (4, 61, 317)])
def test_tsunami_arrival_time_out_of_range(hour, minute, code):
    report = azarashi.decode(_with_arrival_time(TSUNAMI, 0, 0, hour, minute), 'nmea')
    assert report.expected_tsunami_arrival_times[0] is None
    assert report.expected_tsunami_arrival_times_raw[0] == {'day': 0, 'hour': hour, 'minute': minute}
    assert f'津波到達予想時刻: 津波到達予想時刻(コード番号：{code})\n' in str(report)


def _with_report_date(sentence, month, day):
    return with_fields(sentence, [(21, 4, month), (25, 5, day)])  # report time: month (4 bits), day (5 bits)


@pytest.mark.parametrize('month, day', [(4, 31), (2, 30)])
def test_nonexistent_report_date_is_a_decoder_error(month, day):
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as e:
        azarashi.decode(_with_report_date(EEW, month, day), 'nmea')
    assert e.value.message == f'Invalid Report Time: {day} as day of month {month}'


@pytest.mark.parametrize('received, year', [
    (datetime(2029, 9, 1, tzinfo=UTC), 2028),  # the closest leap day is in the past
    (datetime(2029, 1, 15, tzinfo=UTC), 2028),
    (datetime(2031, 6, 1, tzinfo=UTC), 2032),  # the closest leap day is ahead
    (datetime(2027, 12, 31, tzinfo=UTC), 2028),  # a leap year already
])
def test_report_on_a_leap_day_takes_the_closest_leap_year(received, year):
    report = nmea.Decoder(_with_report_date(EEW, 2, 29), timestamp=received).decode()
    assert (report.report_time.year, report.report_time.month, report.report_time.day) == (year, 2, 29)


@pytest.mark.parametrize('received, day, code', [
    (datetime(2029, 3, 5, tzinfo=UTC), 29, 59456),  # 2029 has no February 29th
    (datetime(2029, 3, 10, tzinfo=UTC), 31, 63552),
])
def test_nonexistent_occurrence_date_is_a_code(received, day, code):
    sentence = with_fields(_with_report_date(EEW, received.month, received.day), [(80, 5, day)])  # occurrence day
    report = nmea.Decoder(sentence, timestamp=received).decode()
    assert report.occurrence_time_of_earthquake is None
    assert report.occurrence_time_of_earthquake_raw == {'day': day, 'hour': 1, 'minute': 0}
    assert f'地震発生時刻: 地震発生時刻(コード番号：{code})\n' in str(report)


def test_occurrence_on_a_leap_day():
    received = datetime(2028, 3, 5, tzinfo=UTC)
    sentence = with_fields(_with_report_date(EEW, 3, 5), [(80, 5, 29)])
    report = nmea.Decoder(sentence, timestamp=received).decode()
    assert report.occurrence_time_of_earthquake.date() == datetime(2028, 2, 29).date()


def _with_nwp_arrival_time(sentence, region, day, hour, minute):
    """Return the Northwest Pacific tsunami sentence with the arrival time of one coastal region replaced."""
    pos = 56 + region * 28  # expected arrival time: day (1 bit), hour (5 bits), minute (6 bits)
    return with_fields(sentence, [(pos, 1, day), (pos + 1, 5, hour), (pos + 6, 6, minute)])


def test_northwest_pacific_tsunami_arrival_times():
    report = azarashi.decode(_with_nwp_arrival_time(NWP, 1, 0, 31, 63), 'nmea')
    first = report.expected_tsunami_arrival_times[0]
    assert (first.hour, first.minute) == (14, 46)
    assert report.expected_tsunami_arrival_times[1] is None
    assert [(r['hour'], r['minute']) for r in report.expected_tsunami_arrival_times_raw[:2]] == [(14, 46), (31, 63)]
    assert report.expected_tsunami_arrival_times_raw[1]['day'] == 0
    assert report.expected_tsunami_arrival_time_types_en == ['Expected Tsunami Arrival Time', 'Arrived or Unknown'] + \
        ['Expected Tsunami Arrival Time'] * 3
    lines = [line for line in str(report).splitlines() if line.startswith('Expected Tsunami Arrival Time')]
    assert lines[:2] == [f'Expected Tsunami Arrival Time: {report.convert_dt_to_str_iso(first)}',
                         'Expected Tsunami Arrival Time: Arrived or Unknown']


def test_northwest_pacific_tsunami_arrived_or_unknown_sample():
    report = azarashi.decode(NWP_ARRIVED_OR_UNKNOWN, 'nmea')
    assert report.expected_tsunami_arrival_times == [None]
    assert report.expected_tsunami_arrival_time_types_en == ['Arrived or Unknown']
    assert 'Expected Tsunami Arrival Time: Arrived or Unknown\n' in str(report)


@pytest.mark.parametrize('hour, minute, time_type', [
    (31, 63, 'Arrived or Unknown'),
    (23, 59, 'Expected Tsunami Arrival Time'),
    # only the combination of IS-QZSS-DCR-017 is a special value; the code is the whole field (12 bits)
    (31, 0, 'Undefined Expected Tsunami Arrival Time (Code: 1984)'),
    (4, 63, 'Undefined Expected Tsunami Arrival Time (Code: 319)'),
    (30, 62, 'Undefined Expected Tsunami Arrival Time (Code: 1982)'),  # "no data" is only for JMA-DC Report (Tsunami)
    (4, 62, 'Undefined Expected Tsunami Arrival Time (Code: 318)'),
    (24, 0, 'Undefined Expected Tsunami Arrival Time (Code: 1536)'),
])
def test_northwest_pacific_tsunami_arrival_time_types(hour, minute, time_type):
    report = azarashi.decode(_with_nwp_arrival_time(NWP, 0, 0, hour, minute), 'nmea')
    assert report.expected_tsunami_arrival_time_types_en[0] == time_type
    assert (report.expected_tsunami_arrival_times[0] is None) == (time_type != 'Expected Tsunami Arrival Time')
    assert report.expected_tsunami_arrival_times_raw[0] == {'day': 0, 'hour': hour, 'minute': minute}


def test_northwest_pacific_tsunami_arrival_time_code_is_shown():
    report = azarashi.decode(_with_nwp_arrival_time(NWP, 0, 0, 24, 0), 'nmea')
    assert 'Expected Tsunami Arrival Time: Undefined Expected Tsunami Arrival Time (Code: 1536)\n' in str(report)


def test_every_defined_disaster_category_has_a_decoder():
    # the decoder's last else raises Unsupported Disaster Category; it is there so that a category
    # added to the table without a decoder fails cleanly, and this keeps it unreachable
    from qzqsm import jma
    from azarashi.definitions.qzss.dcr.disaster_category import disaster_category
    decoded = {dc: type(azarashi.decode(jma(dc, []))) for dc in disaster_category}
    assert len(decoded) == 12
    assert all(cls.__module__.endswith('reports.dcr') for cls in decoded.values())
    assert len(set(decoded.values())) == len(decoded)  # one class each


def test_every_defined_message_type_has_a_decoder():
    # same idea for Unsupported Message Type, which the two decoders below keep out of reach
    from qzqsm import jma
    from test_dcx_fields import dcx
    from azarashi.definitions.qzss.l1s import message_types
    assert set(message_types) == {43, 44}
    assert azarashi.decode(jma(1, [])).message_type == message_types[43]
    assert azarashi.decode(dcx(a1=1, a2=111, a3=2)).message_type == message_types[44]
