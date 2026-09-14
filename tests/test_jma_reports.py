"""JMA-DC Report (MT43) tests on crafted messages: the common header, the shared fields and every category."""
from datetime import UTC
from datetime import datetime

import pytest

import azarashi
from azarashi.qzss_dcr_lib.decoder import NmeaQzssDcrDecoder
from azarashi.qzss_dcr_lib.report.qzss_dc_report import QzssDcReportJmaNankaiTroughEarthquake as Nankai
from qzqsm import jma

RECEIVED = datetime(2026, 3, 7, 6, 0, tzinfo=UTC)  # the crafted reports are issued at 05:10 UTC on March 7th
TRAINING = '*** これは訓練です ***'


def _decode(sentence, timestamp=RECEIVED):
    return NmeaQzssDcrDecoder(sentence, timestamp=timestamp).decode()


def _error(sentence, timestamp=RECEIVED):
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        _decode(sentence, timestamp)
    return excinfo.value.message


def _time(pos, day, hour, minute):
    return [(pos, 5, day), (pos + 5, 5, hour), (pos + 10, 6, minute)]


def _lat_lon(pos, lat, lon, south=0, west=0):
    return [(pos, 1, south), (pos + 1, 7, lat[0]), (pos + 8, 6, lat[1]), (pos + 14, 6, lat[2]),
            (pos + 20, 1, west), (pos + 21, 8, lon[0]), (pos + 29, 6, lon[1]), (pos + 35, 6, lon[2])]


# the common header

def test_header():
    report = _decode(jma(12, TYPHOON))
    assert (report.version, report.message_type, report.preamble) == (1, 'DCR', 'A')
    assert (report.disaster_category, report.disaster_category_en, report.disaster_category_no) == ('台風', 'Typhoon', 12)
    assert (report.report_classification, report.report_classification_en, report.report_classification_no) == \
        ('訓練/試験', 'Training/Test', 7)
    assert (report.information_type, report.information_type_en, report.information_type_no) == ('発表', 'Issue', 0)
    assert report.report_time == datetime(2026, 3, 7, 5, 10, tzinfo=UTC)
    assert report.get_report_time_str() == '3月7日14時10分'  # JST
    assert report.get_report_time_str_iso() == '--03-07T05:10Z'


@pytest.mark.parametrize('code, ja, en', [
    (1, '最優先', 'Maximum Priority'),
    (2, '優先', 'Priority'),
    (3, '通常', 'Regular'),
    (0, '通報区分(コード番号：0)', 'Undefined Report Classification (Code: 0)'),
])
def test_report_classification(code, ja, en):
    report = _decode(jma(12, TYPHOON, classification=code))
    assert (report.report_classification, report.report_classification_en) == (ja, en)
    assert report.get_header() == f'防災気象情報(台風)(発表)({ja})'
    assert report.get_header_en() == f'JMA-DC Report (Typhoon) (Issue) ({en})'


@pytest.mark.parametrize('code, ja, en', [
    (1, '訂正', 'Correction'),
    (3, '情報形態(コード番号：3)', 'Undefined Information Type (Code: 3)'),
])
def test_information_type(code, ja, en):
    report = _decode(jma(12, TYPHOON, classification=3, information_type=code))
    assert (report.information_type, report.information_type_en) == (ja, en)


def test_cancellation_header():
    report = _decode(jma(12, TYPHOON, classification=3, information_type=2))
    assert report.get_header() == '防災気象情報(台風)(取消)(通常)\n*** 取り消しされました ***'
    assert report.get_header_en() == 'JMA-DC Report (Typhoon) (Cancellation) (Regular)\n*** CANCELLATION ***'


def test_training_header_wins_over_cancellation():
    report = _decode(jma(12, TYPHOON, information_type=2))
    assert report.get_header() == f'防災気象情報(台風)(取消)(訓練/試験)\n{TRAINING}'
    assert report.get_header_en() == 'JMA-DC Report (Typhoon) (Cancellation) (Training/Test)\n*** TRAINING/TEST ***'


@pytest.mark.parametrize('version', [0, 2, 63])
def test_unsupported_version(version):
    assert _error(jma(12, TYPHOON, version=version)) == f'Unsupported JMA-DC Report Version: {version}'


@pytest.mark.parametrize('category', [0, 7, 13, 15])
def test_undefined_disaster_category(category):
    assert _error(jma(category)) == f'Undefined Disaster Category: {category}'


@pytest.mark.parametrize('header, message', [
    ({'month': 0}, 'Invalid Report Time: 0 as month'),
    ({'month': 13}, 'Invalid Report Time: 13 as month'),
    ({'day': 0}, 'Invalid Report Time: 0 as day'),
    ({'hour': 24}, 'Invalid Report Time: 24 as hour'),
    ({'minute': 60}, 'Invalid Report Time: 60 as minute'),
])
def test_invalid_report_time(header, message):
    assert _error(jma(12, TYPHOON, **header)) == message


@pytest.mark.parametrize('received, month, year', [
    (datetime(2026, 3, 7, tzinfo=UTC), 9, 2026),  # six months apart: the same year
    (datetime(2026, 3, 7, tzinfo=UTC), 10, 2025),  # more than six months ahead: issued last year
    (datetime(2026, 1, 1, tzinfo=UTC), 12, 2025),
    (datetime(2026, 9, 7, tzinfo=UTC), 3, 2026),
    (datetime(2026, 10, 7, tzinfo=UTC), 3, 2027),  # more than six months behind: issued next year
    (datetime(2026, 12, 31, 23, 59, tzinfo=UTC), 1, 2027),
])
def test_report_year_is_the_closest_to_the_reception(received, month, year):
    report = _decode(jma(11, FLOOD, month=month, day=1, hour=0, minute=0), timestamp=received)
    assert report.report_time == datetime(year, month, 1, tzinfo=UTC)


# fields shared by the categories

@pytest.mark.parametrize('report_date, day, expected', [
    ((3, 7), 7, datetime(2026, 3, 7, 5, 2, tzinfo=UTC)),
    ((3, 7), 22, datetime(2026, 3, 22, 5, 2, tzinfo=UTC)),  # up to 15 days apart: the same month
    ((3, 7), 23, datetime(2026, 2, 23, 5, 2, tzinfo=UTC)),  # more than 15 days after the report: the month before
    ((1, 2), 31, datetime(2025, 12, 31, 5, 2, tzinfo=UTC)),
    ((3, 30), 14, datetime(2026, 4, 14, 5, 2, tzinfo=UTC)),  # more than 15 days before the report: the month after
    ((12, 31), 1, datetime(2027, 1, 1, 5, 2, tzinfo=UTC)),
])
def test_day_hour_minute_field_takes_the_nearest_month(report_date, day, expected):
    month, report_day = report_date
    received = datetime(2026, month, report_day, 6, tzinfo=UTC)
    report = _decode(jma(3, _time(53, day, 5, 2), month=month, day=report_day), timestamp=received)
    assert report.occurrence_time_of_earthquake == expected


@pytest.mark.parametrize('day, hour, minute, message', [
    (0, 5, 2, 'Invalid Time: 0 as day'),
    (7, 24, 2, 'Invalid Time: 24 as hour'),
    (7, 5, 60, 'Invalid Time: 60 as minute'),
])
def test_day_hour_minute_field_out_of_range(day, hour, minute, message):
    assert _error(jma(3, _time(53, day, hour, minute))) == message


@pytest.mark.parametrize('lat, lon, south, west, text', [
    ((35, 41, 0), (139, 45, 30), 0, 0, '北緯35度41分0秒 東経139度45分30秒'),
    ((89, 59, 59), (179, 59, 59), 1, 1, '南緯89度59分59秒 西経179度59分59秒'),
])
def test_coordinates(lat, lon, south, west, text):
    report = _decode(jma(2, HYPOCENTER[:-8] + _lat_lon(122, lat, lon, south, west)))
    assert report.coordinates_of_hypocenter == text
    assert report.coordinates_of_hypocenter_raw == {'lat_ns': south, 'lat_d': lat[0], 'lat_m': lat[1], 'lat_s': lat[2],
                                                    'lon_ew': west, 'lon_d': lon[0], 'lon_m': lon[1], 'lon_s': lon[2]}
    assert f'緯度・経度: {text}\n' in str(report)


@pytest.mark.parametrize('lat, lon, south, west, code', [  # the code is the whole LatLon field (41 bits)
    ((90, 0, 0), (139, 0, 0), 0, 0, 773094682624),
    ((35, 60, 0), (139, 0, 0), 0, 0, 308701343744),
    ((35, 0, 60), (139, 0, 0), 0, 0, 300774109184),
    ((35, 0, 0), (180, 0, 0), 0, 0, 300648448000),
    ((35, 0, 0), (139, 60, 0), 0, 0, 300648283904),
    ((35, 0, 0), (139, 0, 60), 0, 0, 300648280124),
    ((127, 63, 63), (255, 63, 63), 1, 1, 2199023255551),
])
def test_coordinates_out_of_range(lat, lon, south, west, code):
    report = _decode(jma(2, HYPOCENTER[:-8] + _lat_lon(122, lat, lon, south, west)))
    assert report.coordinates_of_hypocenter == f'緯度・経度(コード番号：{code})'
    assert report.coordinates_of_hypocenter_raw == {'lat_ns': south, 'lat_d': lat[0], 'lat_m': lat[1], 'lat_s': lat[2],
                                                    'lon_ew': west, 'lon_d': lon[0], 'lon_m': lon[1], 'lon_s': lon[2]}
    assert f'緯度・経度: 緯度・経度(コード番号：{code})\n' in str(report)


@pytest.mark.parametrize('category', [1, 2])  # earthquake early warning and hypocenter
@pytest.mark.parametrize('code, depth', [
    (0, '0km'), (500, '500km'), (501, '500kmより深い'), (511, '不明'),
    (502, '深さ(コード番号：502)'), (510, '深さ(コード番号：510)'),  # between the special codes: may be defined later
])
def test_depth(category, code, depth):
    report = _decode(jma(category, {1: EEW, 2: HYPOCENTER}[category] + [(96, 9, code)]))
    assert (report.depth_of_hypocenter, report.depth_of_hypocenter_raw) == (depth, code)


@pytest.mark.parametrize('code, magnitude', [
    (1, '0.1'), (72, '7.2'), (100, '10.0'), (101, '10.0より大きい'), (126, '不明(8.0より大きい)'), (127, '不明'),
    (0, 'マグニチュード(コード番号：0)'), (102, 'マグニチュード(コード番号：102)'), (125, 'マグニチュード(コード番号：125)'),
])
def test_hypocenter_magnitude(code, magnitude):
    report = _decode(jma(2, HYPOCENTER + [(105, 7, code)]))
    assert (report.magnitude, report.magnitude_raw) == (magnitude, code)


@pytest.mark.parametrize('code, magnitude', [
    (1, '0.1'), (72, '7.2'), (100, '10.0'), (101, '10.0より大きい'), (127, '不明'),
    (126, 'マグニチュード(コード番号：126)'),  # IS-QZSS-DCR-017 defines 126 for JMA-DC Report (Hypocenter) only
    (0, 'マグニチュード(コード番号：0)'), (102, 'マグニチュード(コード番号：102)'), (125, 'マグニチュード(コード番号：125)'),
])
def test_earthquake_early_warning_magnitude(code, magnitude):
    report = _decode(jma(1, EEW + [(105, 7, code)]))
    assert (report.magnitude, report.magnitude_raw) == (magnitude, code)
    assert f'マグニチュード: {magnitude}\n' in str(report)


@pytest.mark.parametrize('codes, count', [((0, 201, 211), 0), ((201, 0, 211), 1), ((201, 211, 212), 3)])
def test_notifications_end_at_the_first_zero(codes, count):
    fields = [(53 + i * 9, 9, code) for i, code in enumerate(codes)]
    report = _decode(jma(2, HYPOCENTER + fields))
    assert report.notifications_on_disaster_prevention_raw == list(codes[:count])
    assert len(report.notifications_on_disaster_prevention) == count


@pytest.mark.parametrize('code, name', [
    (4620100, '鹿児島県鹿児島市'),
    (4699999, '鹿児島県のその他の市町村'),
    (4699998, '鹿児島県の市町村(コード番号：4699998)'),  # named after the prefecture in the code
    (8388607, '市町村(コード番号：8388607)'),
])
def test_local_government(code, name):
    report = _decode(jma(9, ASH_FALL[:-3] + [(83, 3, 1), (86, 3, 3), (89, 23, code)]))
    assert (report.local_governments, report.local_governments_raw) == ([name], [code])


# every category, rendered

# Earthquake Early Warning: assumed hypocenter, long-period ground motion, two forecast regions
EEW = [(47, 3, 3), (50, 3, 5), (53, 9, 201), *_time(80, 7, 5, 9), (96, 9, 10), (105, 7, 10), (112, 10, 341),
       (122, 4, 8), (126, 4, 11), (130, 1, 1), (134, 1, 1)]


def test_earthquake_early_warning():
    report = _decode(jma(1, EEW))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaEarthquakeEarlyWarning
    assert report.assumptive is True
    assert (report.eew_forecast_regions, report.eew_forecast_regions_raw) == (['北海道道央', '青森'], [1, 5])
    assert str(report) == f'''防災気象情報(緊急地震速報)(発表)(訓練/試験)
{TRAINING}
緊急地震速報
強い揺れに警戒してください。

発表時刻: 3月7日14時10分

震央地名: 千葉県北西部
地震発生時刻: 7日14時9分
深さ: 10km(仮定震源要素)
マグニチュード: 1.0(仮定震源要素)
震度(下限): 震度6弱
震度(上限): 〜程度以上
長周期地震動階級(下限): 長周期地震動階級2
長周期地震動階級(上限): 長周期地震動階級4
北海道道央、青森'''


@pytest.mark.parametrize('depth, magnitude, assumptive', [(10, 11, False), (11, 10, False), (10, 10, True)])
def test_earthquake_early_warning_assumed_hypocenter(depth, magnitude, assumptive):
    report = _decode(jma(1, EEW + [(96, 9, depth), (105, 7, magnitude)]))
    assert report.assumptive is assumptive
    assert ('(仮定震源要素)' in str(report)) is assumptive


def test_earthquake_early_warning_without_long_period_ground_motion():
    report = _decode(jma(1, EEW + [(47, 3, 0), (50, 3, 0)]))
    assert (report.long_period_ground_motion_lower_limit, report.long_period_ground_motion_upper_limit) == (None, None)
    assert '長周期地震動階級' not in str(report)
    assert str(report).endswith('震度(上限): 〜程度以上\n北海道道央、青森')


def test_earthquake_early_warning_every_forecast_region():
    report = _decode(jma(1, EEW + [(130 + i, 1, 1) for i in range(80)]))
    assert report.eew_forecast_regions_raw == list(range(1, 81))
    assert report.eew_forecast_regions[-1] == 'その他の府県予報区および地方予報区_緊急地震速報(警報)'
    assert report.eew_forecast_regions[74] == '府県予報区および地方予報区_緊急地震速報(警報)(地点：75)'  # an undefined point


HYPOCENTER = [(53, 9, 201), *_time(80, 7, 5, 2), (96, 9, 30), (105, 7, 65), (112, 10, 341),
              *_lat_lon(122, (35, 41, 0), (139, 45, 30))]


def test_hypocenter():
    report = _decode(jma(2, HYPOCENTER))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaHypocenter
    assert str(report) == f'''防災気象情報(震源)(発表)(訓練/試験)
{TRAINING}
7日14時2分ころ、地震がありました。
強い揺れに警戒してください。

発表時刻: 3月7日14時10分

震央地名: 千葉県北西部
緯度・経度: 北緯35度41分0秒 東経139度45分30秒
深さ: 30km
マグニチュード: 6.5'''


def test_seismic_intensity():
    report = _decode(jma(3, [*_time(53, 7, 5, 2), (69, 3, 5), (72, 6, 13), (78, 3, 3), (81, 6, 14)]))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaSeismicIntensity
    assert (report.seismic_intensities_raw, report.prefectures_raw) == ([5, 3], [13, 14])
    assert str(report) == f'''防災気象情報(震度)(発表)(訓練/試験)
{TRAINING}
7日14時2分ころ、地震による強い揺れを感じました。

発表時刻: 3月7日14時10分

震度: 6弱
東京都

震度: 5弱
神奈川県'''


def test_seismic_intensity_every_entry():
    entries = [field for i in range(16) for field in ((69 + i * 9, 3, 7), (72 + i * 9, 6, 47))]
    report = _decode(jma(3, [*_time(53, 7, 5, 2), *entries]))
    assert (report.seismic_intensities, report.prefectures) == (['7'] * 16, ['沖縄県'] * 16)


@pytest.fixture
def fresh_nankai_assembly(monkeypatch):
    monkeypatch.setattr(Nankai, 'reports', {})
    monkeypatch.setattr(Nankai, 'completed', False)
    monkeypatch.setattr(Nankai, 'announcement', None)


def test_nankai_trough_earthquake(fresh_nankai_assembly):
    text = '訓練の情報。'.encode()  # 18 bytes: one page
    fields = [(53, 4, 5), *((57 + i * 8, 8, byte) for i, byte in enumerate(text)), (201, 6, 1), (207, 6, 1)]
    report = _decode(jma(4, fields))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    assert (report.information_serial_code, report.text_information) == ('巨大地震注意', text)
    assert str(report) == f'''防災気象情報(南海トラフ地震)(発表)(訓練/試験)
{TRAINING}
南海トラフ地震に関連する情報が発表されました。

発表時刻: 3月7日14時10分
地震関連情報: 巨大地震注意
訓練の情報。'''


def test_nankai_trough_earthquake_while_receiving(fresh_nankai_assembly):
    report = _decode(jma(4, [(53, 4, 4), (201, 6, 2), (207, 6, 3)]))
    assert str(report).endswith('地震関連情報: 巨大地震警戒\n受信中 (2) [1/3]')


TSUNAMI = [(53, 9, 109), (62, 9, 111), (80, 4, 3),
           (84, 1, 0), (85, 5, 5), (90, 6, 30), (96, 4, 3), (100, 10, 100),
           (110, 1, 1), (111, 5, 0), (116, 6, 15), (122, 4, 14), (126, 10, 201)]


def test_tsunami():
    report = _decode(jma(5, TSUNAMI))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaTsunami
    assert report.expected_tsunami_arrival_times == [datetime(2026, 3, 7, 5, 30, tzinfo=UTC),
                                                     datetime(2026, 3, 8, 0, 15, tzinfo=UTC)]  # the next day
    assert str(report) == f'''防災気象情報(津波)(発表)(訓練/試験)
{TRAINING}
津波警報を発表しました。
津波と満潮が重なると、津波はより高くなりますので一層厳重な警戒が必要です。
場所によっては、観測した津波の高さよりさらに大きな津波が到達しているおそれがあります。

発表時刻: 3月7日14時10分

津波到達予想時刻: 7日14時30分
津波の高さ: 3m
北海道太平洋沿岸東部

津波到達予想時刻: 8日9時15分
津波の高さ: 不明
青森県太平洋沿岸'''


NORTHWEST_PACIFIC_TSUNAMI = [(53, 3, 1), (56, 1, 0), (57, 5, 6), (62, 6, 0), (68, 9, 1), (77, 7, 1)]


def test_northwest_pacific_tsunami():
    report = _decode(jma(6, NORTHWEST_PACIFIC_TSUNAMI, classification=3, information_type=2))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaNorthwestPacificTsunami
    assert report.tsunami_heights_raw == [1]
    assert str(report) == f'''JMA-DC Report (Northwest Pacific Tsunami) (Cancellation) (Regular)
*** CANCELLATION ***
There is a Possibility of a Destructive Ocean-Wide Tsunami.

Time of Issue: --03-07T05:10Z

Expected Tsunami Arrival Time: ---07T06:00Z
Tsunami Height: {report.tsunami_heights_en[0]}
Coastal Region: {report.coastal_regions_en[0]}'''


VOLCANO = [(50, 3, 1), *_time(53, 7, 4, 58), (69, 7, 13), (76, 12, 506), (88, 23, 4620100), (111, 23, 4621400)]


def test_volcano():
    report = _decode(jma(8, VOLCANO))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaVolcano
    assert str(report) == f'''防災気象情報(火山)(発表)(訓練/試験)
{TRAINING}
火山に関連する情報をお知らせします。

発表時刻: 3月7日14時10分

火山名: 桜島
日時: 3月7日13時58分頃
現象: レベル3(入山規制)

鹿児島県鹿児島市、鹿児島県垂水市'''


def test_ambiguity_beyond_the_table():
    report = _decode(jma(8, VOLCANO))
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        report.convert_dt_to_ambiguous_time_str(report.activity_time, 8)
    assert excinfo.value.message == 'Undefined JMA Ambiguity of Activity Time: 8'


ASH_FALL = [*_time(53, 7, 4, 30), (69, 2, 1), (71, 12, 506),
            (83, 3, 1), (86, 3, 3), (89, 23, 4620100), (112, 3, 2), (115, 3, 1), (118, 23, 4621400)]


def test_ash_fall():
    report = _decode(jma(9, ASH_FALL))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaAshFall
    assert (report.expected_ash_fall_times, report.expected_ash_fall_times_raw) == (['1時間', '2時間'], [1, 2])
    assert report.ash_fall_warning_codes_raw == [3, 1]
    assert str(report) == f'''防災気象情報(降灰)(発表)(訓練/試験)
{TRAINING}
降灰に関連する情報をお知らせします。

発表時刻: 3月7日14時10分

速報
火山名: 桜島
日時: 7日13時30分

基点時刻からの時間: 1時間
現象: 多量の降灰
鹿児島県鹿児島市

基点時刻からの時間: 2時間
現象: 少量の降灰
鹿児島県垂水市'''


@pytest.mark.parametrize('code, warning_type', [
    (1, '速報'), (2, '詳細'),
    (0, '降灰予報(コード番号：0)'), (3, '降灰予報(コード番号：3)'),  # not an error: a later edition may define them
])
def test_ash_fall_warning_type(code, warning_type):
    report = _decode(jma(9, ASH_FALL + [(69, 2, code)]))
    assert (report.ash_fall_warning_type, report.ash_fall_warning_type_raw) == (warning_type, code)
    assert f'発表時刻: 3月7日14時10分\n\n{warning_type}\n火山名: 桜島\n' in str(report)


@pytest.mark.parametrize('code, hours', [
    (1, '1時間'), (6, '6時間'),
    (0, '基点時刻からの時間(コード番号：0)'), (7, '基点時刻からの時間(コード番号：7)'),  # may be defined later
])
def test_ash_fall_expected_time(code, hours):
    report = _decode(jma(9, ASH_FALL + [(83, 3, code)]))
    assert (report.expected_ash_fall_times, report.expected_ash_fall_times_raw) == ([hours, '2時間'], [code, 2])
    assert f'基点時刻からの時間: {hours}\n' in str(report)


def test_ash_fall_every_entry():
    entries = [field for i in range(4) for field in ((83 + i * 29, 3, 6), (86 + i * 29, 3, 7), (89 + i * 29, 23, 4620100))]
    report = _decode(jma(9, ASH_FALL[:5] + entries))
    assert (report.expected_ash_fall_times, report.expected_ash_fall_times_raw) == (['6時間'] * 4, [6] * 4)
    assert report.ash_fall_warning_codes == ['その他の防災気象情報要素2'] * 4


WEATHER = [(53, 3, 1), (56, 5, 2), (61, 19, 130010), (80, 5, 23), (85, 19, 140000)]


def test_weather():
    report = _decode(jma(10, WEATHER))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaWeather
    assert str(report) == f'''防災気象情報(気象)(発表)(訓練/試験)
{TRAINING}
気象に関連する情報をお知らせします。

発表時刻: 3月7日14時10分

警報等情報要素: 大雨特別警報(発表)
東京地方

警報等情報要素: 土砂災害警戒情報(発表)
神奈川県'''


def test_weather_every_entry():
    entries = [field for i in range(6) for field in ((56 + i * 24, 5, 31), (61 + i * 24, 19, 11000))]
    report = _decode(jma(10, [(53, 3, 2), *entries]))
    assert report.weather_warning_state == '解除'
    assert report.weather_related_disaster_sub_categories == ['その他の警報等情報要素'] * 6
    assert report.weather_forecast_regions == ['宗谷地方'] * 6


FLOOD = [(53, 4, 2), (57, 40, 830303020300)]


def test_flood():
    report = _decode(jma(11, FLOOD + [(97, 4, 4), (101, 40, 890907000100)]))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaFlood
    assert str(report) == f'''防災気象情報(洪水)(発表)(訓練/試験)
{TRAINING}
河川の氾濫に関連する情報をお知らせします。

発表時刻: 3月7日14時10分

警報レベル: 氾濫警戒情報
鬼怒川(栃木県・茨城県)

警報レベル: 氾濫発生情報
矢部川下流部(福岡県)'''


@pytest.mark.parametrize('code, name', [
    (830399999998, '関東地方の河川(コード番号：830399999998)'),  # named after the region in the code
    (990000000000, '河川(コード番号：990000000000)'),
])
def test_flood_undefined_region(code, name):
    report = _decode(jma(11, [(53, 4, 15), (57, 40, code)]))
    assert (report.flood_warning_levels, report.flood_forecast_regions) == (['その他の警戒レベル'], [name])


def test_flood_every_entry():
    entries = [field for i in range(3) for field in ((53 + i * 44, 4, 1), (57 + i * 44, 40, 830303020300))]
    report = _decode(jma(11, entries))
    assert report.flood_warning_levels == ['警報解除'] * 3


TYPHOON = [*_time(53, 7, 3, 0), (69, 3, 1), (80, 7, 24), (87, 7, 5), (94, 4, 1), (98, 4, 2),
           *_lat_lon(102, (25, 30, 0), (130, 15, 45)), (143, 11, 950), (154, 7, 45), (161, 7, 0)]


def test_typhoon():
    report = _decode(jma(12, TYPHOON))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaTyphoon
    assert report.reference_time == datetime(2026, 3, 7, 3, 0, tzinfo=UTC)
    assert (report.typhoon_number_raw, report.central_pressure_raw, report.maximum_wind_speed_raw,
            report.maximum_gust_wind_speed_raw) == (5, 950, 45, 0)
    assert report.coordinates_of_typhoon_raw == {'lat_ns': 0, 'lat_d': 25, 'lat_m': 30, 'lat_s': 0,
                                                 'lon_ew': 0, 'lon_d': 130, 'lon_m': 15, 'lon_s': 45}
    assert str(report) == f'''防災気象情報(台風)(発表)(訓練/試験)
{TRAINING}
台風解析・予報情報が発表されました。

発表時刻: 3月7日14時10分

台風番号: 5号
基点時刻: 7日12時0分
基点時刻分類: 実況
情報の基点時刻(実況)からの経過時間: 24時間後
大きさ: 大型
強さ: 非常に強い
緯度・経度: 北緯25度30分0秒 東経130度15分45秒
中心気圧: 950hPa
最大風速: 45m/s
最大瞬間風速: 不明'''


@pytest.mark.parametrize('fields, attribute, value', [
    ([(87, 7, 1)], 'typhoon_number', '1号'),
    ([(87, 7, 99)], 'typhoon_number', '99号'),
    ([(143, 11, 0)], 'central_pressure', '0hPa'),
    ([(143, 11, 1100)], 'central_pressure', '1100hPa'),
    ([(154, 7, 15)], 'maximum_wind_speed', '15m/s'),
    ([(154, 7, 105)], 'maximum_wind_speed', '105m/s'),
    ([(154, 7, 0)], 'maximum_wind_speed', '不明'),
    ([(161, 7, 15)], 'maximum_gust_wind_speed', '15m/s'),
    ([(161, 7, 105)], 'maximum_gust_wind_speed', '105m/s'),
    ([(87, 7, 0)], 'typhoon_number', '台風番号(コード番号：0)'),
    ([(87, 7, 100)], 'typhoon_number', '台風番号(コード番号：100)'),
    ([(143, 11, 1101)], 'central_pressure', '中心気圧(コード番号：1101)'),
    ([(143, 11, 2047)], 'central_pressure', '中心気圧(コード番号：2047)'),
    ([(154, 7, 14)], 'maximum_wind_speed', '最大風速(コード番号：14)'),
    ([(154, 7, 106)], 'maximum_wind_speed', '最大風速(コード番号：106)'),
    ([(161, 7, 0)], 'maximum_gust_wind_speed', '不明'),
    ([(161, 7, 14)], 'maximum_gust_wind_speed', '最大瞬間風速(コード番号：14)'),
    ([(161, 7, 106)], 'maximum_gust_wind_speed', '最大瞬間風速(コード番号：106)'),
    ([(69, 3, 3)], 'reference_time_type', '予報'),
    ([(69, 3, 0)], 'reference_time_type', '基点時刻分類(コード番号：0)'),
    ([(94, 4, 15)], 'typhoon_scale_category', 'その他の大きさ階級分類'),
    ([(98, 4, 3)], 'typhoon_intensity_category', '猛烈な'),
])
def test_typhoon_fields(fields, attribute, value):
    report = _decode(jma(12, TYPHOON + fields))
    assert getattr(report, attribute) == value
    assert getattr(report, f'{attribute}_raw') == fields[0][2]


def test_typhoon_coordinates_out_of_range():
    report = _decode(jma(12, TYPHOON + _lat_lon(102, (25, 30, 0), (180, 15, 45))))
    assert report.coordinates_of_typhoon == '緯度・経度(コード番号：218775634925)'
    assert report.coordinates_of_typhoon_raw['lon_d'] == 180


def test_marine():
    report = _decode(jma(14, [(53, 5, 22), (58, 14, 1030), (72, 5, 11), (77, 14, 1120)]))
    assert type(report) is azarashi.qzss_dc_report.QzssDcReportJmaMarine
    assert (report.marine_warning_codes_raw, report.marine_forecast_regions_raw) == ([22, 11], [1030, 1120])
    assert str(report) == f'''防災気象情報(海上)(発表)(訓練/試験)
{TRAINING}
海上警報が発表されました。

発表時刻: 3月7日14時10分

警報等情報要素: 海上暴風警報
網走沖

警報等情報要素: 海上濃霧警報
釧路沖'''


def test_marine_entries_end_where_both_fields_are_zero():
    report = _decode(jma(14, [(53, 5, 0), (58, 14, 1030), (72, 5, 0), (77, 14, 0), (91, 5, 22), (96, 14, 1120)]))
    assert report.marine_warning_codes == ['海上警報解除']  # a lifted warning still names its region
    assert report.marine_forecast_regions == ['網走沖']


def test_marine_every_entry():
    entries = [field for i in range(8) for field in ((53 + i * 19, 5, 31), (58 + i * 19, 14, 10000))]
    report = _decode(jma(14, entries))
    assert report.marine_warning_codes == ['その他の警報等情報要素_海上警報'] * 8
    assert report.marine_forecast_regions == ['その他の地方海上予報区'] * 8
