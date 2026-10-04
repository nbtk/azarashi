"""Wire semantics from the local CAMF Issue 1.2 and DCX-004 specifications.

Expected bit allocation, identifiers, reserved values and D26 endpoints are
written independently of the implementation's tables and numeric profiles.
"""
import copy

import pytest
from jsonschema import Draft202012Validator

import azarashi
from strict_schema import strict
from test_dcx_fields import RECEIVED, dcx


@pytest.fixture(scope='module')
def validator():
    return Draft202012Validator(strict(azarashi.json_schema()))


def _international(raw, version=0, country=10):
    return azarashi.decode(dcx(a1=1, a2=country, a3=2, a4=44, a9=0, a10=version,
                              a11=raw, a14=1), timestamp=RECEIVED)


@pytest.mark.parametrize('version', [0, 1])
def test_all_international_a11_bits_keep_both_lists_without_version_fallback(version, validator):
    # DCX-004 4.2.3.11(2), Table 4.2-16; CAMF Annex C 11, pp.63-65.
    # The schema permits reserved codes, so expected statuses are checked separately.
    for list_a in range(32):
        for list_b in range(32):
            raw = (list_a << 5) | list_b
            report = _international(raw, version)
            row = azarashi.to_json_dict(report)
            validator.validate(row)
            guidance = row['data']['instruction']
            assert guidance['source'] == {'a11': raw}
            for part, letter, number, reserved in (
                ('list_a', 'A', list_a, set()), ('list_b', 'B', list_b, {29, 30}),
            ):
                code = guidance['content'][part]
                assert code['code'] == str(number)
                assert code['table'] == f'camf.a11_instruction_library.international.version_{version}.{part}'
                assert code['identifier'] == (f'IC-{letter}-{number + 1:02d}' if version == 0 else None)
                if version or number in reserved:
                    expected_status = 'undefined'
                elif number == 0:  # the empty value of a list
                    expected_status = 'special'
                else:
                    expected_status = 'valid'
                assert code['status'] == expected_status
                assert bool(code['labels']) is (expected_status != 'undefined')
            if version:
                assert report.a11_international_library_code is None
                assert report.a11_international_library_a is None and report.a11_international_library_b is None
                assert 'A11 - Instruction' not in str(report)
            else:
                assert report.a11_international_library_a_code == f'IC-A-{list_a + 1:02d}'
                assert report.a11_international_library_b_code == f'IC-B-{list_b + 1:02d}'
                assert isinstance(report.a11_international_library_code, str)
                assert isinstance(report.a11_international_library, str)


@pytest.mark.parametrize('version', range(2, 8))
def test_every_other_library_version_keeps_raw_codes_but_has_no_known_instruction(version, validator):
    row = azarashi.to_json_dict(_international(97, version))
    validator.validate(row)
    assert row['data']['instruction']['source'] == {'a11': 97}
    for part, number in [('list_a', '3'), ('list_b', '1')]:
        code = row['data']['instruction']['content'][part]
        assert (code['code'], code['status'], code['identifier'], code['labels']) == (number, 'undefined', None, {})


def test_a_crc_valid_fixed_message_keeps_shelter_and_monitoring_instructions(validator):
    # A11=00011_00001. This fixed input does not use the message-building helper.
    sentence = '$QZQSM,55,9AB00041425982D100618000800028B00000000000000000000000002038B14*0F'
    report = azarashi.decode(sentence, timestamp=RECEIVED)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    assert report.camf.a11 == 97
    assert report.a11_international_library_a == \
        'Seek shelter in a building immediately. Stay under cover and stay informed.'
    assert report.a11_international_library_b == \
        'Check with the weather services and local authorities for additional information'
    for text in (str(report), report.get_text('en'), report.a11_international_library):
        assert report.a11_international_library_a in text and report.a11_international_library_b in text


@pytest.mark.parametrize('list_b,expected', [
    (1, 'Check with the weather services and local authorities for additional information'),
    (21, 'Leave the affected area immediately and seek higher ground or move to higher parts of the building. '
         'Listen to radio or media for directions and information'),
    (25, 'Have iodine tablets ready. DO NOT take the iodine tablets now. '
         'If this becomes necessary, we will inform you in good time.'),
    (26, 'Take the iodine tablets NOW according to the package insert.'),
    (28, 'Seek shelter if you cannot leave the area immediately.'),
    (31, 'This replaces the warning previously in effect for this area.'),
])
def test_list_b_actions_are_its_own_instructions(list_b, expected, validator):
    # CAMF Annex C 11, pp.64-65: in particular, prepare vs take iodine and update vs all clear.
    report = _international((3 << 5) | list_b)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    assert report.a11_international_library_b == expected
    assert row['data']['instruction']['content']['list_b']['labels'] == {'en': expected}
    assert expected in report.get_text('en')
    assert 'Conditions have improved' not in report.get_text('en')


@pytest.mark.parametrize('list_b', [29, 30])
def test_a_reserved_secondary_code_never_selects_a_primary_action(list_b, validator):
    report = _international((3 << 5) | list_b)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    assert row['data']['instruction']['content']['list_a']['status'] == 'valid'
    assert row['data']['instruction']['content']['list_b']['status'] == 'undefined'
    assert row['data']['instruction']['content']['list_b']['labels'] == {}
    assert 'Seek shelter in a building immediately' in str(report)
    assert 'This is only a test' not in str(report)
    assert 'This replaces the warning' not in str(report)


def test_null_primary_code_cannot_turn_a_warning_update_into_an_all_clear(validator):
    report = _international(31)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    content = row['data']['instruction']['content']
    assert content['list_a']['status'] == 'special' and content['list_a']['labels'] == {'en': 'No instruction'}
    assert content['list_b']['status'] == 'valid' and content['list_b']['identifier'] == 'IC-B-32'
    assert 'This replaces the warning previously in effect for this area.' in str(report)
    assert 'Conditions have improved' not in str(report)


@pytest.mark.parametrize('country', [0, 10, 71, 111, 219, 511])
def test_the_international_lists_do_not_depend_on_country(country, validator):
    row = azarashi.to_json_dict(_international(97, country=country))
    validator.validate(row)
    assert row['data']['instruction']['content']['list_a']['identifier'] == 'IC-A-04'
    assert row['data']['instruction']['content']['list_b']['identifier'] == 'IC-B-02'


@pytest.mark.parametrize('country,version,raw', [(111, 0, 126), (111, 0, 1023), (111, 1, 126), (10, 0, 126)])
def test_country_libraries_keep_the_full_ten_bit_code(country, version, raw, validator):
    report = azarashi.decode(dcx(a1=1, a2=country, a3=2, a9=1, a10=version, a11=raw), timestamp=RECEIVED)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    content = row['data']['instruction']['content']
    assert content['code'] == str(raw) and 'list_a' not in content and 'list_b' not in content
    assert 'source' not in row['data']['instruction']
    assert report.a11_international_library_a is None and report.a11_international_library_b is None
    if country == 111 and version == 0 and raw == 126:
        assert report.a11_japanese_library == 'This is a test message for DCX.'
    else:
        assert content['status'] == 'undefined'


@pytest.mark.parametrize('change', ['missing_list', 'single_code', 'wrong_list_table', 'out_of_field', 'missing_source'])
def test_international_schema_rejects_loss_or_misidentification_of_a_list(change, validator):
    row = copy.deepcopy(azarashi.to_json_dict(_international(97)))
    guidance = row['data']['instruction']
    if change == 'missing_list':
        del guidance['content']['list_b']
    elif change == 'single_code':
        guidance['content'] = guidance['content']['list_a']
    elif change == 'wrong_list_table':
        guidance['content']['list_b']['table'] = guidance['content']['list_a']['table']
    elif change == 'out_of_field':
        guidance['content']['list_a']['code'] = '32'
    else:
        del guidance['source']
    assert not validator.is_valid(row)


# CAMF Annex C 18.4.35.26, pp.112-113. These are the printed endpoints,
# including its overlapping lower-only ranges, not a contiguous partition.
D26_RANGES = [
    (0, 9), (10, 20), (21, 50), (51, 70), (71, 100), (101, 125), (126, 150),
    (151, 175), (176, 200), (201, 250), (251, 300), (301, 350), (351, 400),
    (401, 450), (451, 500), (501, 750), (751, 1000),
    (1000, None), (2000, None), (3000, None), (5000, None),
]


@pytest.mark.parametrize('hazard', [51, 53])
@pytest.mark.parametrize('code', range(32))
def test_d26_retains_specification_endpoints_and_reserved_values(hazard, code, validator):
    report = azarashi.decode(dcx([(131, 5, code)], a1=1, a2=10, a3=2, a4=hazard,
                                a9=1, a14=1, a17=3), timestamp=RECEIVED)
    row = azarashi.to_json_dict(report)
    validator.validate(row)
    quantity = row['data']['specific_settings']['hazard_details']['number_of_cases_per_100000_inhabitants']
    assert quantity['code'] == str(code)
    if code < len(D26_RANGES):
        lower, upper = D26_RANGES[code]
        assert quantity['status'] == 'valid' and quantity['unit'] == '1'
        assert quantity['range'] == {'lower': lower, 'upper': upper}
    else:
        assert quantity['status'] == 'undefined' and quantity['value'] is None
        assert quantity['labels'] == {} and 'range' not in quantity
