"""Code written for v0.16.4 keeps working: the examples of its README, and every attribute its reports had.

Reading a report stays compatible (docs/reports.md); these tests hold azarashi to that against the
last release before the reports were renamed. v0_16_4_reports.json lists, for every report class
of v0.16.4, the attributes and methods its reports had when it decoded the logs in tests/, and the
fields of its CAMF object. v0.16.4 does not change, so the list was written once, on 2026-09-27, and
the tests only read it: they never install or run v0.16.4. It came of decoding those logs with a
checkout of the tag, taking vars(report), the public callables of its class and vars(report.camf):

    git worktree add --detach /tmp/v0164 v0.16.4
    cd /tmp && PYTHONPATH=/tmp/v0164 python3 ...

The values need not match: IS-QZSS-DCR-017 and 0.17.0 changed some of them. The names must be there.

The README examples below are copied from v0.16.4 as they were, but for the device they open,
/dev/ttyS0, which a test has not got: a file or a stand-in for the serial port takes its place.
"""
import datetime
import gzip
import io
import json
import pathlib
from contextlib import redirect_stderr, redirect_stdout

import pytest

import azarashi
from test_declared_types import REPORTS

HERE = pathlib.Path(__file__).resolve().parent
EARLIER = json.loads((HERE / 'v0_16_4_reports.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name', sorted(EARLIER['reports']))
def test_a_report_has_every_attribute_and_method_it_had(name):
    cls = getattr(azarashi.qzss_dc_report, name)
    reports = [report for report in REPORTS if type(report) is cls]
    assert reports, name  # reports of the class, or the test proves nothing
    names = EARLIER['reports'][name]['attributes'] + EARLIER['reports'][name]['methods']
    missing = sorted({attribute for report in reports for attribute in names if not hasattr(report, attribute)})
    assert missing == [], name


def test_the_camf_object_has_every_field_it_had():
    reports = [report for report in REPORTS if hasattr(report, 'camf')]
    missing = sorted({field for report in reports for field in EARLIER['camf'] if not hasattr(report.camf, field)})
    assert reports and missing == []


EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'


def test_the_readme_decodes_a_report():
    # README, decode(): the call, and the text it showed
    report = azarashi.decode(EEW, msg_type='nmea')
    assert azarashi.decode(EEW, 'nmea') == report
    assert str(report) == (
        '防災気象情報(緊急地震速報)(発表)(訓練/試験)\n*** これは訓練です ***\n緊急地震速報\n強い揺れに警戒してください。\n\n'
        '発表時刻: 3月10日10時0分\n\n震央地名: 日向灘\n地震発生時刻: 10日10時0分\n深さ: 10km\nマグニチュード: 7.2\n'
        '震度(下限): 震度6弱\n震度(上限): 〜程度以上\n'
        '島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州')
    shown = {'assumptive', 'depth_of_hypocenter', 'depth_of_hypocenter_raw', 'disaster_category',
             'disaster_category_en', 'disaster_category_no', 'eew_forecast_regions', 'eew_forecast_regions_raw',
             'information_type', 'information_type_en', 'information_type_no',
             'long_period_ground_motion_lower_limit', 'long_period_ground_motion_lower_limit_raw',
             'long_period_ground_motion_upper_limit', 'long_period_ground_motion_upper_limit_raw', 'magnitude',
             'magnitude_raw', 'message', 'message_header', 'message_type', 'nmea',
             'notifications_on_disaster_prevention', 'notifications_on_disaster_prevention_raw',
             'occurrence_time_of_earthquake', 'preamble', 'raw', 'report_classification',
             'report_classification_en', 'report_classification_no', 'report_time', 'satellite_id',
             'satellite_prn', 'seismic_epicenter', 'seismic_epicenter_raw', 'seismic_intensity_lower_limit',
             'seismic_intensity_lower_limit_raw', 'seismic_intensity_upper_limit',
             'seismic_intensity_upper_limit_raw', 'sentence', 'timestamp', 'version'}
    assert shown <= set(report.get_params())
    assert report.long_period_ground_motion_lower_limit is None  # as the README printed it


def test_the_readme_finds_the_same_message_equal():
    # README: the same message with another preamble is the same report
    msg2 = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'
    report = azarashi.decode(EEW, 'nmea')
    report2 = azarashi.decode(msg2, 'nmea')
    assert report == report2


def test_the_readme_decodes_an_l_alert():
    msg = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E'  # l-alert
    report = azarashi.decode(msg, 'nmea')
    print(report)
    shown = {'sentence', 'timestamp', 'message', 'nmea', 'message_header', 'satellite_id', 'satellite_prn', 'raw',
             'preamble', 'message_type', 'camf', 'ignore_a12_to_a16', 'ignore_a17_to_a18', 'ignore_ex1',
             'ignore_ex2_to_ex7', 'ignore_ex8_to_ex9', 'satellite_designation_mask_type',
             'satellite_designation_mask', 'dcx_message_type', 'a1_message_type', 'a2_country_region_name',
             'a3_provider_identifier', 'a4_hazard_category', 'a4_hazard_type', 'a4_hazard_definition',
             'a5_severity', 'a6_hazard_onset_week', 'a7_hazard_onset_time_of_week', 'a6a7_hazard_onset_datetime',
             'a8_hazard_duration', 'a9_type_of_library', 'a10_library_version', 'a11_japanese_library',
             'a11_japanese_library_ja', 'a12_ellipse_centre_latitude', 'a13_ellipse_centre_longitude',
             'a14_ellipse_semi_major_axis', 'a15_ellipse_semi_minor_axis', 'a16_ellipse_azimuth',
             'a17_type_of_specific_settings', 'c1_refined_latitude_of_centre_of_main_ellipse',
             'c2_refined_longitude_of_centre_of_main_ellipse', 'c3_refined_length_of_semi_major_axis',
             'c4_refined_length_of_semi_minor_axis', 'dcx_version'}
    assert shown <= set(report.get_params())
    assert (report.a11_japanese_library, report.a11_japanese_library_ja) == ('Keep away from Water area.', '離れろ。水場。')
    assert set(report.camf.get_params()) >= {
        'sdmt', 'sdm', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11', 'a12', 'a13', 'a14',
        'a15', 'a16', 'a17', 'a18', 'ex1', 'ex2', 'ex3', 'ex4', 'ex5', 'ex6', 'ex7', 'ex8', 'ex9', 'ex10', 'vn',
        'c1', 'c2', 'c3', 'c4'}


@pytest.fixture
def recording(tmp_path):
    """Some u-blox frames the logs were received as, in place of the device."""
    path = tmp_path / 'ttyS0'
    path.write_bytes(gzip.decompress((HERE / 'ublox_260924.ubx.gz').read_bytes())[:200_000])
    return path


def test_the_readme_stream_example_reads_to_the_end(recording):
    # README, decode_stream(): the loop that catches the earlier exceptions, and returns 0 at the end
    source = '''
import azarashi
import sys

def example():
    with open('/dev/ttyS0', mode='r') as f:
        while True:
            try:
                azarashi.decode_stream(f, msg_type='ublox', callback=print)
            except azarashi.QzssDcrDecoderException as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.QzssDcrDecoderNotImplementedError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except EOFError as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
'''.replace("'/dev/ttyS0'", repr(str(recording)))
    exits = []
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(io.StringIO()):
        exec(source, {'exit': exits.append})
    assert exits == [0]
    assert '防災気象情報' in out.getvalue()


def test_the_readme_serial_example_reads_to_the_end(recording, monkeypatch):
    # README, pySerial: the port opened by serial.Serial, reports printed with pprint and unique=True
    serial = pytest.importorskip('serial')
    monkeypatch.setattr(serial, 'Serial', lambda port, baudrate: io.BytesIO(recording.read_bytes()))
    source = '''
import azarashi
import sys
import serial
import pprint

def handler(report):
    pprint.pprint(report.get_params())

def example():
    with serial.Serial('/dev/ttyS0', 9600) as ser:
        while True:
            try:
                azarashi.decode_stream(ser, 'ublox', handler, unique=True)
            except azarashi.QzssDcrDecoderException as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except azarashi.QzssDcrDecoderNotImplementedError as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
            except EOFError as e:
                print(f'{e}', file=sys.stderr)
                return 0
            except Exception as e:
                print(f'# [{type(e).__name__}] {e}', file=sys.stderr)
                return 1

exit(example())
'''
    exits = []
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(io.StringIO()):
        exec(source, {'exit': exits.append})
    assert exits == [0]
    assert "'disaster_category'" in out.getvalue()


def test_the_readme_times_were_naive_and_are_now_utc():
    # 0.17.0 made every time aware, in UTC, and said so; the values are what they were, read as UTC
    report = azarashi.decode(EEW, 'nmea', timestamp=datetime.datetime(2026, 3, 10, 2, 0, tzinfo=datetime.UTC))
    assert report.report_time == datetime.datetime(2026, 3, 10, 1, 0, tzinfo=datetime.UTC)
