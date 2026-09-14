"""DCX (MT44) tests on crafted messages: message types, every CAMF field group and the rendered report."""
import datetime

import pytest

from azarashi.qzss_dcr_lib.decoder import NmeaQzssDcrDecoder
from azarashi.qzss_dcr_lib.definition import qzss_dcx_camf_b4_lower_level_fields_tables as b4
from azarashi.qzss_dcr_lib.report import qzss_dc_report
from qzqsm import sentence

UTC = datetime.UTC
RECEIVED = datetime.datetime(2026, 9, 14, 3, 0, tzinfo=UTC)  # a Monday

CAMF = {  # field: (position, size)
    'sdmt': (14, 1), 'sdm': (15, 9),
    'a1': (24, 2), 'a2': (26, 9), 'a3': (35, 5), 'a4': (40, 7), 'a5': (47, 2), 'a6': (49, 1), 'a7': (50, 14),
    'a8': (64, 2), 'a9': (66, 1), 'a10': (67, 3), 'a11': (70, 10), 'a12': (80, 16), 'a13': (96, 17),
    'a14': (113, 5), 'a15': (118, 5), 'a16': (123, 6), 'a17': (129, 2), 'a18': (131, 15),
    'ex1': (146, 16), 'ex2': (162, 1), 'ex3': (163, 17), 'ex4': (180, 17), 'ex5': (197, 5), 'ex6': (202, 5),
    'ex7': (207, 7), 'ex8': (146, 1), 'ex9': (147, 64), 'vn': (214, 6),
}
JAPAN = {'a1': 1, 'a2': 111}


def dcx(fields=(), **camf):
    """A DCX message with the given CAMF fields, and any other (position, size, value) fields after them."""
    return sentence([(0, 8, 0x9A), (8, 6, 44), *((*CAMF[name], value) for name, value in camf.items()), *fields])


def _decode(msg):
    return NmeaQzssDcrDecoder(msg, timestamp=RECEIVED).decode()


# message types

@pytest.mark.parametrize('camf', [{}, {'a2': 111}, {'a2': 111, 'sdmt': 1, 'sdm': 0x1ff}])  # A2 and the mask may be set
def test_null_message(camf):
    report = _decode(dcx(**camf))
    assert type(report) is qzss_dc_report.QzssDcxNullMsg
    assert (report.message_type, report.dcx_message_type) == ('DCX', 'Null Message')
    assert str(report) == '### DCX Message - Null Message ###'
    assert not hasattr(report, 'a1_message_type')


@pytest.mark.parametrize('camf, report_type, dcx_message_type', [
    ({'a2': 111, 'a3': 1}, qzss_dc_report.QzssDcxLAlert, 'L-Alert'),
    ({'a2': 111, 'a3': 2}, qzss_dc_report.QzssDcxJAlert, 'J-Alert'),
    ({'a2': 111, 'a3': 3}, qzss_dc_report.QzssDcxJAlert, 'J-Alert'),
    ({'a2': 111, 'a3': 4}, qzss_dc_report.QzssDcxMTInfo, 'Information from Local Government'),
    ({'a2': 111, 'a3': 0, 'a1': 1}, qzss_dc_report.QzssDcxUnknown, 'Unknown DCX Message Type'),
    ({'a2': 111, 'a3': 5}, qzss_dc_report.QzssDcxUnknown, 'Unknown DCX Message Type'),
    ({'a2': 10, 'a3': 2}, qzss_dc_report.QzssDcxOutsideJapan, 'Information from Organizations outside Japan'),
    ({'a2': 0, 'a1': 1}, qzss_dc_report.QzssDcxOutsideJapan, 'Information from Organizations outside Japan'),
])
def test_message_types(camf, report_type, dcx_message_type):
    report = _decode(dcx(**camf))
    assert type(report) is report_type
    assert report.dcx_message_type == dcx_message_type


@pytest.mark.parametrize('camf, ignored', [
    ({'a2': 10, 'a3': 2}, {'ex1', 'ex2_to_ex7', 'ex8_to_ex9'}),
    ({'a2': 111, 'a3': 1, 'a14': 1}, {'ex1', 'ex2_to_ex7', 'ex8_to_ex9'}),  # L-Alert with an ellipse
    ({'a2': 111, 'a3': 1, 'ex1': 1100}, {'a12_to_a16', 'ex2_to_ex7', 'ex8_to_ex9'}),  # L-Alert with a target area
    ({'a2': 111, 'a3': 2}, {'a12_to_a16', 'a17_to_a18', 'ex1', 'ex2_to_ex7'}),
    ({'a2': 111, 'a3': 4, 'ex5': 1}, {'ex8_to_ex9'}),  # with an additional ellipse
    ({'a2': 111, 'a3': 4}, {'ex2_to_ex7', 'ex8_to_ex9'}),
    ({'a2': 111, 'a3': 5}, {'ex1', 'ex2_to_ex7', 'ex8_to_ex9'}),
])
def test_ignored_field_groups(camf, ignored):
    report = _decode(dcx(**camf))
    groups = ('a12_to_a16', 'a17_to_a18', 'ex1', 'ex2_to_ex7', 'ex8_to_ex9')
    assert {group for group in groups if getattr(report, f'ignore_{group}')} == ignored


FOR_JAPAN, FOR_OUTSIDE = 'For Japan', 'For use outside Japan'
STOPPED, SENDING = 'Transmission stopped', 'Transmission in progress'


@pytest.mark.parametrize('sdmt, sdm, mask', [  # the examples of IS-QZSS-DCX-004 5.6.1, then Bit1 alone
    (0, 0b010000100,
     [FOR_JAPAN, FOR_OUTSIDE, FOR_JAPAN, FOR_JAPAN, FOR_JAPAN, FOR_JAPAN, FOR_OUTSIDE, FOR_JAPAN, FOR_JAPAN]),
    (1, 0b011100100, [STOPPED, SENDING, SENDING, SENDING, STOPPED, STOPPED, SENDING, STOPPED, STOPPED]),
    (0, 0b100000000, [FOR_OUTSIDE] + [FOR_JAPAN] * 8),  # Bit1 is PRN183
])
def test_satellite_designation_mask(sdmt, sdm, mask):
    report = _decode(dcx(sdmt=sdmt, sdm=sdm, **JAPAN, a3=2))
    mask_type = ['MT44 is for Japan or for use outside Japan', 'MT44 transmission status'][sdmt]
    assert (report.satellite_designation_mask_type, report.satellite_designation_mask) == (mask_type, mask)


# A1 to A11

def test_common_alert_message_fields():
    report = _decode(dcx(a1=2, a2=219, a3=2, a4=44, a5=3, a6=1, a7=721, a8=3, vn=5))
    assert report.a1_message_type == 'Update'
    assert report.a2_country_region_name == 'Thailand'
    assert report.a3_provider_identifier == 'Thai Meteorological Department'
    assert (report.a4_hazard_category, report.a4_hazard_type) == ('GEO', 'Tsunami')
    assert report.a5_severity == 'Extreme - Extraordinary threat to life or property'
    assert report.a6_hazard_onset_week == 'Next'
    assert report.a7_hazard_onset_time_of_week == 'MONDAY - 00:00 PM'
    assert report.a6a7_hazard_onset_datetime == datetime.datetime(2026, 9, 21, 12, 0, tzinfo=UTC)
    assert report.a8_hazard_duration == '12H <= Duration < 24H'
    assert report.dcx_version == 5


@pytest.mark.parametrize('a2, a3, provider', [
    (10, 12, 'Australian Broadcasting Corporation'),
    (71, 5, 'Fiji Broadcasting Corporation'),
    (111, 4, 'Local Government'),
    (10, 13, 'Undefined Provider Identifier of Australia (Code: 13)'),
    (1, 3, 'Undefined Provider Identifier (Code: 3)'),  # a country without a provider list
])
def test_provider_identifier(a2, a3, provider):
    assert _decode(dcx(a1=1, a2=a2, a3=a3)).a3_provider_identifier == provider


def test_international_library():
    report = _decode(dcx(a1=1, a2=10, a3=2, a9=0, a11=3))
    assert (report.a9_type_of_library, report.a10_library_version) == ('International library', '#1')
    assert report.a11_international_library_code == 'IC-A-04'
    assert report.a11_international_library == 'Seek shelter in a building immediately. Stay under cover and stay informed.'
    assert 'A11 - Instruction code: IC-A-04\n' \
           'A11 - Instruction: Seek shelter in a building immediately. Stay under cover and stay informed.\n' \
           in str(report)


def test_international_library_without_instruction():
    report = _decode(dcx(a1=1, a2=10, a3=2, a9=0, a11=0))
    assert (report.a11_international_library_code, report.a11_international_library) == ('IC-A-01', '')
    assert 'A11 - Instruction code: IC-A-01\nA12 - ' in str(report)


def test_japanese_library():
    report = _decode(dcx(**JAPAN, a3=2, a9=1, a11=126))
    assert (report.a11_japanese_library, report.a11_japanese_library_ja) == \
        ('This is a test message for DCX.', 'これは、DCX のテストです。')
    assert 'A11 - Instruction: This is a test message for DCX.\n' \
           'A11 - Instruction (ja): これは、DCX のテストです。\n' in str(report)


def test_japanese_library_without_instruction():
    report = _decode(dcx(**JAPAN, a3=2, a9=1, a11=0))
    assert 'A11 - Instruction' not in str(report)


def test_country_library_of_another_country_is_not_decoded():
    report = _decode(dcx(a1=1, a2=10, a3=2, a9=1, a11=126))
    assert report.a9_type_of_library == 'Country/region library'
    assert not hasattr(report, 'a11_japanese_library')


def test_unsupported_library_version():
    report = _decode(dcx(**JAPAN, a3=2, a9=1, a10=1, a11=126))
    assert report.a10_library_version == 'Unsupported Library Version (Code: 1)'
    assert not hasattr(report, 'a11_japanese_library')


def test_test_message_header():
    report = _decode(dcx(a1=0, a2=111, a3=2))
    assert str(report).startswith('### DCX Message - J-Alert ###\n*** This is a test message ***\nA1 - Message type: Test\n')


# A12 to A16

@pytest.mark.parametrize('camf, latitude, longitude, major, minor, azimuth', [
    ({'a12': 0, 'a13': 0, 'a14': 0, 'a15': 0, 'a16': 0}, -90.0, -180.0, 0.216, 0.216, -90.0),
    ({'a12': 0xFFFF, 'a13': 0x1FFFF, 'a14': 31, 'a15': 31, 'a16': 63}, 90.0, 180.0, 2500.0, 2500.0, 87.1875),
])
def test_main_ellipse_bounds(camf, latitude, longitude, major, minor, azimuth):
    report = _decode(dcx(a1=1, a2=10, a3=2, **camf))
    assert (report.a12_ellipse_centre_latitude, report.a13_ellipse_centre_longitude) == (latitude, longitude)
    assert (report.a14_ellipse_semi_major_axis, report.a15_ellipse_semi_minor_axis) == (major, minor)
    assert report.a16_ellipse_azimuth == azimuth


@pytest.mark.parametrize('code', range(8))
def test_b1_refines_by_an_eighth_of_a_grid_step(code):
    base = {**ELLIPSE, 'a12': 0x8000, 'a13': 0x10000}
    report = _decode(dcx([(131, 3, code), (134, 3, code), (137, 3, code), (140, 3, code)], **base, a17=0))
    assert report.c1_refined_latitude_of_centre_of_main_ellipse == round(-90 + 180 / 0xFFFF * (0x8000 + code / 8), 6)
    assert report.c2_refined_longitude_of_centre_of_main_ellipse == round(-180 + 360 / 0x1FFFF * (0x10000 + code / 8), 6)


def test_b1_longitude_is_refined_by_a_longitude_step():
    # EWSS CAMF Issue 1.2, 3.6.2 and 3.7.1.2: Refined longitude(i) = Longitude(k) + i * IntervalLongitude / 2^3,
    # where IntervalLongitude = 360 / (2^17 - 1), k is the A13 code and i the C2 code
    report = _decode(dcx([(134, 3, 7)], a1=1, a2=10, a3=2, a13=2, a14=1, a17=0))
    interval = 360 / (2 ** 17 - 1)
    assert report.c2_refined_longitude_of_centre_of_main_ellipse == round(-180 + 2 * interval + 7 * interval / 2 ** 3, 6)
    assert report.c2_refined_longitude_of_centre_of_main_ellipse == -179.992104  # not -179.992103 from a latitude step


# A17 and A18

ELLIPSE = {'a1': 1, 'a2': 10, 'a3': 2, 'a12': 0x8000, 'a13': 0x10000, 'a14': 10, 'a15': 5, 'a16': 32}


@pytest.mark.parametrize('c5, delta', [(0, -10.0), (63, -0.15625), (64, 0.15625), (127, 10.0)])  # no zero shift
def test_b2_position_of_the_centre_of_the_hazard(c5, delta):
    report = _decode(dcx([(131, 7, c5), (138, 7, 127 - c5)], **ELLIPSE, a17=1))
    assert report.a17_type_of_specific_settings == 'B2 - Position of the Centre of the Hazard'
    assert report.c5_latitude_of_centre_of_hazard == round(report.a12_ellipse_centre_latitude + delta, 6)
    assert report.c6_longitude_of_centre_of_hazard == round(report.a13_ellipse_centre_longitude - delta, 6)
    assert f'C5 - Latitude of centre of hazard: {report.c5_latitude_of_centre_of_hazard}\n' in str(report)


def test_b3_secondary_ellipse():
    report = _decode(dcx([(131, 2, 3), (133, 3, 7), (136, 5, 8), (141, 5, 31)], **ELLIPSE, a17=2))
    assert report.a17_type_of_specific_settings == 'B3 - Secondary Ellipse Definition'
    assert report.c7_shift_of_second_ellipse_centre == 3
    assert report.c8_homothetic_factor_of_second_ellipse == 2.0
    assert report.c9_bearing_angle_of_second_ellipse == 90.0
    assert report.c10_instruction_library_for_second_ellipse_code == 'IC-C-32'
    lines = str(report).splitlines()
    assert lines[lines.index('A17 - Type of specific settings: B3 - Secondary Ellipse Definition') + 1:][:4] == [
        'C7 - Shift of second ellipse centre: 3',
        'C8 - Homothetic factor of second ellipse: 2.0',
        'C9 - Bearing angle of second ellipse: 90.0',
        'C10 - Instruction library for second ellipse code: IC-C-32',
    ]


def test_b3_is_decoded_without_the_main_ellipse():
    report = _decode(dcx([(131, 2, 1)], **JAPAN, a3=1, ex1=1100, a17=2))
    assert report.ignore_a12_to_a16 is True
    assert report.c7_shift_of_second_ellipse_centre == 1


@pytest.mark.parametrize('a17', [0, 1])
def test_b1_and_b2_need_the_main_ellipse(a17):
    report = _decode(dcx(**JAPAN, a3=1, ex1=1100, a17=a17, a18=0x7fff))
    assert not hasattr(report, 'a17_type_of_specific_settings')
    assert 'A17 - ' not in str(report)


B4_FIELDS = [  # hazard types (A4) and their lower level fields: (attribute, position, size, table)
    ([36], [('d1_magnitude_on_richter_scale', 131, 4, b4.qzss_dcx_camf_d1_magnitude_on_richter_scale),
            ('d2_seismic_coefficient', 135, 3, b4.qzss_dcx_camf_d2_seismic_coefficient),
            ('d3_azimuth_from_centre_of_main_ellipse_to_epicentre', 138, 4,
             b4.qzss_dcx_camf_d3_azimuth_from_centre_of_main_ellipse_to_epicentre),
            ('d4_vector_length_between_centre_of_main_ellipse_and_epicentre', 142, 4,
             b4.qzss_dcx_camf_d4_vector_length_between_centre_of_main_ellipse_and_epicentre)]),
    ([43, 44], [('d5_wave_height', 131, 3, b4.qzss_dcx_camf_d5_wave_height)]),
    ([63, 71], [('d6_temperature_range', 131, 4, b4.qzss_dcx_camf_d6_temperature_range)]),
    ([80], [('d7_hurricane_category', 131, 3, b4.qzss_dcx_camf_d7_hurricane_category),
            ('d8_wind_speed', 134, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d9_rainfall_amounts', 138, 3, b4.qzss_dcx_camf_d9_rainfall_amounts)]),
    ([82], [('d36_typhoon_category', 131, 3, b4.qzss_dcx_camf_d36_typhoon_category),
            ('d8_wind_speed', 134, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d9_rainfall_amounts', 138, 3, b4.qzss_dcx_camf_d9_rainfall_amounts)]),
    ([79], [('d8_wind_speed', 131, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d9_rainfall_amounts', 135, 3, b4.qzss_dcx_camf_d9_rainfall_amounts),
            ('d11_tornado_probability', 138, 3, b4.qzss_dcx_camf_d11_tornado_probability)]),
    ([77], [('d8_wind_speed', 131, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d9_rainfall_amounts', 135, 3, b4.qzss_dcx_camf_d9_rainfall_amounts),
            ('d10_damage_category', 138, 3, b4.qzss_dcx_camf_d10_damage_category),
            ('d16_lightning_intensity', 141, 3, b4.qzss_dcx_camf_d16_lightning_intensity)]),
    ([70], [('d12_hail_scale', 131, 4, b4.qzss_dcx_camf_d12_hail_scale)]),
    ([74], [('d9_rainfall_amounts', 131, 3, b4.qzss_dcx_camf_d9_rainfall_amounts),
            ('d13_visibility', 134, 4, b4.qzss_dcx_camf_d13_visibility)]),
    ([76], [('d14_snow_depth', 131, 5, b4.qzss_dcx_camf_d14_snow_depth),
            ('d13_visibility', 136, 4, b4.qzss_dcx_camf_d13_visibility)]),
    ([68], [('d15_flood_severity', 131, 2, b4.qzss_dcx_camf_d15_flood_severity)]),
    ([72], [('d16_lightning_intensity', 131, 3, b4.qzss_dcx_camf_d16_lightning_intensity)]),
    ([81], [('d8_wind_speed', 131, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d6_temperature_range', 135, 4, b4.qzss_dcx_camf_d6_temperature_range)]),
    ([64], [('d8_wind_speed', 131, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d9_rainfall_amounts', 135, 3, b4.qzss_dcx_camf_d9_rainfall_amounts),
            ('d16_lightning_intensity', 138, 3, b4.qzss_dcx_camf_d16_lightning_intensity),
            ('d11_tornado_probability', 141, 3, b4.qzss_dcx_camf_d11_tornado_probability)]),
    ([69], [('d17_fog_level', 131, 3, b4.qzss_dcx_camf_d17_fog_level),
            ('d13_visibility', 134, 4, b4.qzss_dcx_camf_d13_visibility)]),
    ([75], [('d13_visibility', 131, 4, b4.qzss_dcx_camf_d13_visibility),
            ('d8_wind_speed', 135, 4, b4.qzss_dcx_camf_d8_wind_speed)]),
    ([65], [('d18_drought_level', 131, 2, b4.qzss_dcx_camf_d18_drought_level)]),
    ([33], [('d19_avalanche_warning_level', 131, 3, b4.qzss_dcx_camf_d19_avalanche_warning_level)]),
    ([32], [('d20_ash_fall_amount_and_impact', 131, 3, b4.qzss_dcx_camf_d20_ash_fall_amount_and_impact)]),
    ([47], [('d8_wind_speed', 131, 4, b4.qzss_dcx_camf_d8_wind_speed),
            ('d5_wave_height', 135, 3, b4.qzss_dcx_camf_d5_wave_height)]),
    ([37], [('d21_geomagnetic_scale', 131, 3, b4.qzss_dcx_camf_d21_geomagnetic_scale)]),
    ([103], [('d22_terrorism_threat_level', 131, 3, b4.qzss_dcx_camf_d22_terrorism_threat_level)]),
    ([27, 30], [('d23_fire_risk_level', 131, 3, b4.qzss_dcx_camf_d23_fire_risk_level)]),
    ([16, 18, 21], [('d24_water_quality', 131, 3, b4.qzss_dcx_camf_d24_water_quality)]),
    ([23], [('d25_uv_index', 131, 4, b4.qzss_dcx_camf_d25_uv_index)]),
    ([51, 53], [('d26_number_of_cases_per_100000_inhabitants', 131, 5,
                 b4.qzss_dcx_camf_d26_number_of_cases_per_100000_inhabitants),
                ('d35_infection_type', 136, 6, b4.qzss_dcx_camf_d35_infection_type)]),
    ([19], [('d27_noise_range', 131, 4, b4.qzss_dcx_camf_d27_noise_range)]),
    ([15], [('d28_air_quality_index', 131, 3, b4.qzss_dcx_camf_d28_air_quality_index)]),
    ([55, 56, 57, 58, 60], [('d29_outage_estimated_duration', 131, 5, b4.qzss_dcx_camf_d29_outage_estimated_duration)]),
    ([5], [('d31_chemical_hazard_type', 131, 4, b4.qzss_dcx_camf_d31_chemical_hazard_type)]),
    ([9, 10, 11], [('d30_nuclear_event_scale', 131, 4, b4.qzss_dcx_camf_d30_nuclear_event_scale)]),
    ([4], [('d32_biohazard_level', 131, 2, b4.qzss_dcx_camf_d32_biohazard_level),
           ('d33_biohazard_type', 133, 2, b4.qzss_dcx_camf_d33_biohazard_type)]),
    ([6], [('d34_explosive_hazard_type', 131, 2, b4.qzss_dcx_camf_d34_explosive_hazard_type)]),
]


@pytest.mark.parametrize('a4, fields', [(a4, fields) for hazards, fields in B4_FIELDS for a4 in hazards])
def test_b4_lower_level_fields(a4, fields):
    codes = [(pos, size, (i + 1) % (1 << size)) for i, (_, pos, size, _) in enumerate(fields)]
    report = _decode(dcx(codes, **ELLIPSE, a4=a4, a17=3))
    assert report.a17_type_of_specific_settings == 'B4 - Quantitative and detailed information about the Hazard'
    decoded = {name: value for name, value in report.get_params().items() if name[0] == 'd' and name[1].isdigit()}
    assert decoded == {name: table[code] for (name, _, _, table), (_, _, code) in zip(fields, codes, strict=True)}
    lines = str(report).splitlines()
    for name, value in decoded.items():
        ident, title = name.split('_', 1)
        assert f"{ident.upper()} - {title.replace('_', ' ').capitalize()}: {value}" in lines


@pytest.mark.parametrize('hazards, fields', B4_FIELDS)
def test_b4_lower_level_fields_follow_each_other(hazards, fields):
    # EWSS CAMF Issue 1.2, 3.7.4: the fields are packed from the first bit of A18 (bit 131 of the message)
    assert [pos for _, pos, _, _ in fields] == [131 + sum(size for _, _, size, _ in fields[:i]) for i in range(len(fields))]
    assert sum(size for _, _, size, _ in fields) <= 15


@pytest.mark.parametrize('table, codes', [
    (b4.qzss_dcx_camf_d25_uv_index, 10),  # 4 bits: the indexes 10/11 and 11/11 as well
    (b4.qzss_dcx_camf_d8_wind_speed, 13),
])
def test_b4_tables_fit_their_fields(table, codes):
    assert sorted(table) == list(range(codes))


def test_b4_every_hazard_type_is_listed():
    listed = {a4 for hazards, _ in B4_FIELDS for a4 in hazards}
    for a4 in range(128):
        report = _decode(dcx(**ELLIPSE, a4=a4, a17=3))
        has_fields = any(name[0] == 'd' and name[1].isdigit() for name in report.get_params())
        assert has_fields is (a4 in listed), a4


@pytest.mark.parametrize('table, name', [
    (b4.qzss_dcx_camf_d12_hail_scale, 'hail scale'),
    (b4.qzss_dcx_camf_d22_terrorism_threat_level, 'terrorism threat level'),
])
def test_b4_undefined_codes_name_their_field(table, name):
    assert table[15] == f'Undefined {name} (Code: 15)'


# EX1 to EX9

def test_ex1_target_area():
    report = _decode(dcx(**JAPAN, a3=1, ex1=1100))
    assert (report.ex1_target_area, report.ex1_target_area_ja) == ('Sapporo-shi, Hokkaido', '北海道札幌市')
    assert str(report).endswith('EX1 - Target area: Sapporo-shi, Hokkaido\nEX1 - Target area (ja): 北海道札幌市')


@pytest.mark.parametrize('ex2, direction', [
    (0, 'Leave the additional target area range.'),
    (1, 'Head to the additional target area range.'),
])
def test_ex2_to_ex7_additional_ellipse(ex2, direction):
    report = _decode(dcx(**JAPAN, a3=4, ex1=1100, ex2=ex2, ex3=0x1FFFF, ex4=0, ex5=31, ex6=0, ex7=127))
    assert report.ex2_evacuate_direction_type == direction
    assert (report.ex3_additional_ellipse_centre_latitude, report.ex4_additional_ellipse_centre_longitude) == (90.0, 45.0)
    assert (report.ex5_additional_ellipse_semi_major_axis, report.ex6_additional_ellipse_semi_minor_axis) == (2500.0, 0.216)
    assert report.ex7_additional_ellipse_azimuth == 88.59375
    assert str(report).endswith(f'EX2 - Evacuate direction type: {direction}\n'
                                'EX3 - Additional ellipse centre latitude: 90.0\n'
                                'EX4 - Additional ellipse centre longitude: 45.0\n'
                                'EX5 - Additional ellipse semi major axis: 2500.0\n'
                                'EX6 - Additional ellipse semi minor axis: 0.216\n'
                                'EX7 - Additional ellipse azimuth: 88.59375')


def test_ex8_ex9_prefectures():
    report = _decode(dcx(**JAPAN, a3=2, ex8=0, ex9=(1 << 46 | 1) << 17))  # the first and last prefectures
    assert report.ex8_target_area_list_type == 'Prefecture code'
    assert (report.ex9_target_area_list, report.ex9_target_area_list_ja) == (['Hokkaido', 'Okinawa'], ['北海道', '沖縄県'])


def test_ex8_ex9_cities():
    codes = [(147, 16, 1100), (163, 16, 0), (179, 16, 1101), (195, 16, 0)]
    report = _decode(dcx(codes, **JAPAN, a3=2, ex8=1))
    assert report.ex8_target_area_list_type == 'Cities, towns and villages code'
    assert report.ex9_target_area_list == ['Sapporo-shi, Hokkaido', 'Chuo-ku, Sapporo-shi']
    assert report.ex9_target_area_list_ja == ['北海道札幌市', '札幌市中央区']
    assert str(report).endswith("EX8 - Target area list type: Cities, towns and villages code\n"
                                "EX9 - Target area list: ['Sapporo-shi, Hokkaido', 'Chuo-ku, Sapporo-shi']\n"
                                "EX9 - Target area list (ja): ['北海道札幌市', '札幌市中央区']")


# the whole report

def test_outside_japan_report():
    report = _decode(dcx(a1=1, a2=10, a3=2, a4=82, a5=2, a6=0, a7=1, a8=1, a9=0, a11=1,
                         a12=0x8000, a13=0x10000, a14=10, a15=5, a16=32, a17=2, vn=1))
    assert str(report) == '''### DCX Message - Information from Organizations outside Japan ###
A1 - Message type: Alert
A2 - Country/region name: Australia
A3 - Provider identifier: Bureau of Meteorology
A4 - Hazard category and type: MET - Tropical cyclone (typhoon)
A4 - Hazard definition: %s
A5 - Severity: Severe - Significant threat to life or property
A6A7 - Hazard onset: 2026-09-14T00:00:00Z
A8 - Hazard duration: Duration < 6H
A11 - Instruction code: IC-A-02
A11 - Instruction: You are in the danger zone, leave the area immediately. Listen to radio or media for directions and information.
A12 - Ellipse centre latitude: 0.001373
A13 - Ellipse centre longitude: 0.001373
A14 - Ellipse semi - major axis: 4.421
A15 - Ellipse semi - minor axis: 0.978
A16 - Ellipse azimuth: 0.0
A17 - Type of specific settings: B3 - Secondary Ellipse Definition
C7 - Shift of second ellipse centre: 0
C8 - Homothetic factor of second ellipse: 0.25
C9 - Bearing angle of second ellipse: 0.0
C10 - Instruction library for second ellipse code: IC-C-01
C10 - Instruction library for second ellipse: ''' % report.a4_hazard_definition
