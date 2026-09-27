"""Validate JSON output and saved examples against the bundled wire contract and code tables."""
import copy
import json
import re
from pathlib import Path

import pytest

from azarashi.decoders import nmea

from azarashi import code_tables, json_schema, to_json_dict as example_record
from azarashi.json.model import PROFILES, TYPE_NAMES
from azarashi.json.tables import TABLES, code_tables as built_code_tables
from examples.generate import code_tables_text, fixtures
from strict_schema import strict
from test_declared_types import REPORTS
from test_golden import LOGS, TESTS

# skip this file alone, rather than stopping the whole suite at collection
jsonschema = pytest.importorskip('jsonschema', reason="pip install 'jsonschema[format]'")
Draft202012Validator, FormatChecker = jsonschema.Draft202012Validator, jsonschema.FormatChecker

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / 'docs/json'
PUBLISHED = json_schema()
SCHEMA = strict(PUBLISHED)  # azarashi's own output: nothing it has not defined
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
CODE_TABLES = code_tables()['tables']


def test_schema_is_valid_and_reproducible():
    Draft202012Validator.check_schema(PUBLISHED)
    Draft202012Validator.check_schema(SCHEMA)
    assert json_schema() == PUBLISHED


def test_the_published_schema_takes_keys_and_report_types_added_later():
    published = Draft202012Validator(PUBLISHED, format_checker=FormatChecker())
    row = record('Tsunami')
    row['added_later'] = 1
    row['data']['added_later'] = 1
    row['data']['forecasts'][0]['region']['added_later'] = 1
    assert published.is_valid(row)
    assert not VALIDATOR.is_valid(row)
    later = {**record('Tsunami'), 'type': 'galileo.ews.alert', 'message_id': 'galileo.ews:00', 'data': {'anything': 1}}
    assert published.is_valid(later)
    assert not VALIDATOR.is_valid(later)
    assert not published.is_valid({**later, 'type': 'Not A Type'})


def test_the_published_schema_closes_no_object():
    assert '"additionalProperties": false' not in json.dumps(PUBLISHED)


@pytest.mark.parametrize('report', REPORTS)
def test_real_and_crafted_reports_conform(report):
    VALIDATOR.validate(example_record(report))


def test_saved_examples_are_complete_reproducible_and_cover_all_types():
    rows = [json.loads(line) for line in (FOLDER / 'report-v2.examples.ndjson').read_text(encoding='utf-8').splitlines()]
    assert rows == json.loads((FOLDER / 'report-v2.examples.pretty.json').read_text(encoding='utf-8'))
    assert rows == [example_record(r) for r in fixtures()]
    assert {r['type'] for r in rows} == set(TYPE_NAMES.values())
    for row in rows:
        VALIDATOR.validate(row)


def record(name):
    return example_record(next(r for r in REPORTS if type(r).__name__ == name))


@pytest.mark.parametrize('field', ['schema_version', 'type', 'is_test', 'message_id', 'reception', 'texts', 'data'])
def test_envelope_fields_are_required(field):
    row = record('Tsunami')
    del row[field]
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('path,value', [
    (('schema_version',), 1), (('is_test',), 'yes'), (('unknown',), 1),
    (('message_id',), 'qzss.dcr:AF'), (('message_id',), 'qzss.dcr:a'), (('message_id',), 'af89'),
    (('reception', 'nmea'), ''), (('reception', 'nmea'), '$QZQSM,55,broken*00'),
    (('reception', 'at'), '2026-02-30T01:00:00.000Z'), (('reception', 'at'), '2026-03-01T01:00:00+09:00'),
    (('reception', 'at'), '2026-03-01T01:00:00Z'),
    (('reception', 'satellite'), {'system': 'qzss', 'prn': None}),
    (('texts', 'en'), 1), (('texts', 'ja'), ''), (('texts',), {}),
])
def test_invalid_envelope_rejected(path, value):
    row = record('Tsunami')
    node = row
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = value
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('name,language', [('Tsunami', 'ja'), ('NankaiTroughEarthquake', 'ja'),
                                           ('NorthwestPacificTsunami', 'en'), ('LAlert', 'en'), ('NullMsg', 'en')])
def test_the_language_a_report_is_written_in_is_always_there(name, language):
    row = record(name)
    assert language in row['texts']
    del row['texts'][language]
    row['texts'].setdefault('xx', 'text')
    assert not VALIDATOR.is_valid(row)


def test_the_texts_are_the_texts_of_the_report():
    for report in REPORTS:
        texts = example_record(report)['texts']
        assert texts == {language: report.get_text(language) for language in ('ja', 'en')
                         if report.get_text(language) is not None}
        assert report.get_text() in texts.values()


def test_the_message_id_names_the_message_and_not_its_reception():
    for report in REPORTS:
        row = example_record(report)
        system, content = row['message_id'].split(':')
        assert system == '.'.join(row['type'].split('.')[:2])
        assert content == report.raw.hex()
    # the same message from another satellite, received at another time
    import datetime
    from qzqsm import nmea_checksum
    from test_dcx_fields import JAPAN, dcx
    sentence = dcx(**JAPAN, a3=1, a14=1)
    body = sentence[1:].split('*')[0].replace('QZQSM,55,', 'QZQSM,57,')
    received = datetime.datetime(2026, 3, 7, 6, 0, tzinfo=datetime.UTC)
    one = example_record(nmea.Decoder(sentence, timestamp=received).decode())
    other = example_record(nmea.Decoder(f'${body}*{nmea_checksum(body)}',
                                        timestamp=received + datetime.timedelta(minutes=5)).decode())
    assert one['reception'] != other['reception']
    assert one['message_id'] == other['message_id']


def test_the_message_id_is_the_same_whatever_the_preamble_and_the_satellite_designation():
    from test_dcx_fields import JAPAN, _decode, dcx
    ids = {example_record(_decode(dcx([(0, 8, preamble)], **JAPAN, a3=1, a14=1, sdmt=1, sdm=mask)))['message_id']
           for preamble, mask in [(0x9A, 0), (0x53, 0x1ff), (0xC6, 0x0f0)]}
    assert len(ids) == 1


@pytest.mark.parametrize('name,lifecycle,key', [
    ('Tsunami', 'issue', None),
    ('NankaiTroughEarthquake', 'issue', r'\d{4}-\d\d-\d\dT\d\d:\d\dZ\.7\.0\.\d+\.\d+'),
    ('LAlert', 'all_clear', r'111\.1\.\d+\.\d+'),
    ('JAlert', None, r'111\.2\.\d+'),
])
def test_the_series_of_a_report(name, lifecycle, key):
    series = record(name).get('series', {})
    assert series.get('lifecycle') == lifecycle
    assert (key is None and 'key' not in series) or re.fullmatch(key, series['key'])


def test_the_pages_of_one_nankai_announcement_are_one_series_of_messages():
    pages = {}
    for report in REPORTS:
        if type(report).__name__ == 'NankaiTroughEarthquake':
            row = example_record(report)
            pages.setdefault(row['series']['key'], {})[report.page_number] = row['message_id']
    announcement = max(pages.values(), key=len)
    assert len(announcement) > 1  # the pages of one announcement, or the test proves nothing
    assert len(set(announcement.values())) == len(announcement)  # each page its own message


def test_an_alert_and_its_all_clear_are_one_series_and_another_area_another():
    # IS-QZSS-DCX-004 4.2.3.1: A2, A3, A4 and EX1 name an L-Alert
    from test_dcx_fields import _decode, dcx
    def row(a1, ex1):
        return example_record(_decode(dcx(a1=a1, a2=111, a3=1, a4=36, ex1=ex1)))
    alert, all_clear, elsewhere = row(1, 43213), row(3, 43213), row(1, 43214)
    assert (alert['series']['lifecycle'], all_clear['series']['lifecycle']) == ('issue', 'all_clear')
    assert alert['series']['key'] == all_clear['series']['key'] != elsewhere['series']['key']
    assert alert['message_id'] != all_clear['message_id']


def test_a_dcr_information_type_outside_the_table_has_a_null_lifecycle():
    from qzqsm import with_fields
    from test_dcr import TSUNAMI
    from azarashi import decode
    row = example_record(decode(with_fields(TSUNAMI, [(41, 2, 3)])))
    assert row['series']['lifecycle'] is None
    VALIDATOR.validate(row)


@pytest.mark.parametrize('name,lifecycle', [('Tsunami', 'update'), ('LAlert', 'cancellation'), ('LAlert', 'nothing')])
def test_a_lifecycle_word_belongs_to_one_family(name, lifecycle):
    row = record(name)
    row.setdefault('series', {})['lifecycle'] = lifecycle
    row['is_test'] = False
    assert not VALIDATOR.is_valid(row)


def test_a_test_message_has_no_lifecycle_and_an_alert_has_one():
    row = record('OutsideJapan')
    assert row['is_test'] is True and 'series' not in row
    row['series'] = {'lifecycle': 'issue'}
    assert not VALIDATOR.is_valid(row)
    row = record('LAlert')
    assert row['is_test'] is False
    del row['series']['lifecycle']
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('name', ['Tsunami', 'OutsideJapan', 'Unknown'])
def test_a_key_only_where_the_specification_says_what_belongs_together(name):
    row = record(name)
    row.setdefault('series', {})['key'] = 'anything'
    assert not VALIDATOR.is_valid(row)


def test_the_null_message_has_no_series_and_no_test():
    row = record('NullMsg')
    assert row['data'] == {} and 'series' not in row and row['is_test'] is False
    for change in ({'series': {}}, {'is_test': True}, {'data': {'onset': None}}):
        assert not VALIDATOR.is_valid({**row, **change})


def test_forecast_cannot_lose_its_region_or_height():
    for field in ('region', 'arrival', 'height'):
        row = record('Tsunami')
        del row['data']['forecasts'][0][field]
        assert not VALIDATOR.is_valid(row)


def test_tsunami_height_is_the_announced_range():
    height = record('Tsunami')['data']['forecasts'][0]['height']
    assert height['status'] == 'valid' and height['range'] == {'lower': 1, 'upper': 3} and height['unit'] == 'm'
    assert height['labels']['ja'] == '3m'


@pytest.mark.parametrize('table,code,expected', [
    ('qzss.dcr.depth_of_hypocenter', 10, {'status': 'valid', 'value': 10, 'unit': 'km'}),
    ('qzss.dcr.depth_of_hypocenter', 501, {'status': 'valid', 'range': {'lower': 500, 'upper': None}, 'unit': 'km'}),
    ('qzss.dcr.depth_of_hypocenter', 511, {'status': 'special', 'value': None}),
    ('qzss.dcr.depth_of_hypocenter', 502, {'status': 'undefined', 'value': None}),
    ('qzss.dcr.hypocenter_magnitude', 126, {'status': 'special', 'range': {'lower': 8, 'upper': None}, 'unit': '1'}),
    ('qzss.dcr.tsunami_height', 15, {'status': 'special', 'value': None}),  # その他: a height the table has no code for
    ('qzss.dcr.northwest_pacific_tsunami_height', 508,
     {'status': 'valid', 'range': {'lower': 10, 'upper': None}, 'unit': 'm'}),
    ('qzss.dcr.northwest_pacific_tsunami_height', 509, {'status': 'valid'}),
    ('qzss.dcr.northwest_pacific_tsunami_height', 511, {'status': 'special', 'value': None}),
])
def test_a_quantity_says_what_number_its_code_stands_for(table, code, expected):
    from azarashi.json.model import quantity
    result = quantity(TABLES[table], code)
    assert {k: v for k, v in result.items() if k not in ('code', 'table', 'labels')} == expected


def test_an_assumed_hypocenter_marks_its_depth_and_magnitude():
    from azarashi import decode
    from test_dcr import EEW
    report = decode(EEW)
    report.assumptive = True
    data = example_record(report)['data']
    assert data['depth']['status'] == data['magnitude']['status'] == 'assumed'
    assert data['epicenter']['status'] == 'valid'


def test_jalert_forbids_camf_and_ellipse_fields():
    for key in ('camf', 'main_ellipse', 'specific_settings', 'evacuation'):
        row = record('JAlert')
        row['data'][key] = {}
        assert not VALIDATOR.is_valid(row)


def test_ellipse_is_an_atomic_group():
    row = record('OutsideJapan')
    del row['data']['main_ellipse']['value']['semi_minor_axis_km']
    assert not VALIDATOR.is_valid(row)


def test_quantity_rejects_empty_ranges_and_wrong_units():
    for change in ({'range': {'lower': None, 'upper': None}}, {'unit': 'km'}, {'value': 3}):
        row = record('Tsunami')
        row['data']['forecasts'][0]['height'].update(change)
        assert not VALIDATOR.is_valid(row)


def test_no_input_report_is_mutated():
    r = next(r for r in REPORTS if type(r).__name__ == 'Tsunami')
    before = copy.deepcopy(r.get_params())
    example_record(r)
    assert r.get_params() == before


def test_every_dcr_source_field_has_a_mapping_or_explicit_omission():
    from azarashi.json.model import COMMON, DCR_TYPES, LISTS, SINGLES, TIMES
    from test_declared_types import _declared
    envelope = {'sentence', 'raw', 'timestamp', 'message', 'nmea', 'message_header', 'satellite_id',
                'satellite_prn', 'satellite_svid', 'preamble', 'message_type'}
    common = {'version', 'report_time', 'disaster_category', 'disaster_category_en', 'disaster_category_no'}
    for name in DCR_TYPES:
        r = next(r for r in REPORTS if type(r).__name__ == name)
        used = {src for _, src, _ in COMMON + SINGLES.get(name, [])}
        if name in LISTS:
            used.update(src for _, src, _ in LISTS[name][1])
        if name in TIMES:
            used.update([TIMES[name][1], TIMES[name][1] + '_raw'])
        used.update({'notifications_on_disaster_prevention_raw', 'eew_forecast_regions_raw', 'local_governments_raw',
                     'coordinates_of_hypocenter_raw', 'coordinates_of_typhoon_raw', 'expected_tsunami_arrival_times',
                     'expected_tsunami_arrival_times_raw', 'expected_tsunami_arrival_time_types',
                     'expected_tsunami_arrival_time_types_en', 'assumptive', 'ambiguity_of_activity_time_no',
                     'text_information', 'page_number', 'total_page'})
        # Display attributes are represented by labels from the same code table.
        for field in list(used):
            stem = field.removesuffix('_raw').removesuffix('_no')
            used.update([stem, stem + '_en'])
        assert set(_declared(type(r))) <= used | common | envelope, name


def test_every_ellipse_keeps_the_codes_it_was_built_from():
    report = next(r for r in REPORTS if type(r).__name__ == 'OutsideJapan')
    camf, groups = report.camf, {'main_ellipse': ('a12', 'a13', 'a14', 'a15', 'a16')}
    settings = example_record(report)['data']['specific_settings']
    assert settings['type']['code'] == '0'
    groups['refined_ellipse'] = ('c1', 'c2', 'c3', 'c4', 'a16')
    keys = ('centre_latitude', 'centre_longitude', 'semi_major_axis', 'semi_minor_axis', 'azimuth')
    for where, fields in groups.items():
        source = (example_record(report)['data'] if where == 'main_ellipse' else settings)[where]['source']
        assert source == {key: getattr(camf, field) for key, field in zip(keys, fields, strict=True)}, where


@pytest.mark.parametrize('key', ['centre_latitude', 'semi_major_axis', 'azimuth'])
def test_an_ellipse_may_not_drop_a_transmitted_code(key):
    row = record('OutsideJapan')
    del row['data']['main_ellipse']['source'][key]
    assert not VALIDATOR.is_valid(row)


SETTINGS_TYPES = ['OutsideJapan', 'LAlert', 'MTInfo', 'Unknown']
SETTINGS = ['refined_ellipse', 'hazard_centre', 'second_ellipse', 'hazard_details']


@pytest.mark.parametrize('name', SETTINGS_TYPES)
def test_specific_settings_is_defined_once_for_every_type_that_carries_it(name):
    # one definition, so that a change cannot reach some report types and miss others
    assert SCHEMA['$defs'][name]['properties']['specific_settings'] == {'$ref': '#/$defs/specific_settings'}


@pytest.mark.parametrize('name', SETTINGS_TYPES)
@pytest.mark.parametrize('kind', ['hazard_centre', 'second_ellipse'])
def test_every_kind_of_specific_settings_is_accepted_under_every_type(name, kind):
    settings = next(s for r in REPORTS if hasattr(r, 'camf')
                    if (s := example_record(r)['data'].get('specific_settings')) and kind in s)
    row = record(name)
    row['data']['specific_settings'] = settings
    VALIDATOR.validate(row)


def test_the_type_of_specific_settings_names_the_group_it_carries():
    row = record('OutsideJapan')
    row['data']['specific_settings']['type']['code'] = '1'
    assert not VALIDATOR.is_valid(row)


def _codes(node):
    """Every code object and quantity in a record."""
    if isinstance(node, dict):
        if {'status', 'code', 'table', 'labels'} <= set(node):
            yield node
        for value in node.values():
            yield from _codes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _codes(value)


def test_the_bundled_schema_is_the_one_the_conversion_tables_build():
    from examples.schema import schema_text
    assert (ROOT / 'azarashi/json/schemas/report-v2.schema.json').read_text(encoding='utf-8') == schema_text()


def test_the_code_tables_are_the_catalogue_and_the_docs_file_is_the_same():
    assert code_tables() == built_code_tables()
    assert (FOLDER / 'code-tables-v2.json').read_text(encoding='utf-8') == code_tables_text(code_tables())
    assert json.loads((FOLDER / 'code-tables-v2.json').read_text(encoding='utf-8')) == code_tables()


def test_every_code_a_record_carries_is_in_the_code_tables_as_the_record_gives_it():
    checked = 0
    for report in REPORTS:
        for code in _codes(example_record(report)):
            table = CODE_TABLES.get(code['table'])
            entry = None if table is None else table['codes'].get(code['code'])
            if code['status'] == 'undefined':
                assert entry is None, code
                continue
            assert entry is not None, code
            assert code['labels'] == entry['labels'], code
            assert code['status'] in (entry['status'], 'assumed'), code
            checked += 1
    assert checked > 1000, checked


def test_a_code_table_gives_what_the_specification_does_and_no_order_of_its_own():
    for name, table in CODE_TABLES.items():
        assert set(table) == {'source', 'codes'}, name  # no order: no specification says a table is a scale
        for code, entry in table['codes'].items():
            assert set(entry) == {'status', 'labels'}, (name, code)
            assert entry['status'] in ('valid', 'special'), (name, code)  # a code the table lists is defined
            if entry['status'] == 'special':
                assert entry['labels'], (name, code)  # what a special value means is in its labels


def test_a_table_names_the_specification_that_defines_it():
    for name, table in CODE_TABLES.items():
        prefix = name.split('.')[0] if name.startswith('camf.') else '.'.join(name.split('.')[:2])
        spec = {'camf': 'CAMF', 'qzss.dcr': 'IS-QZSS-DCR', 'qzss.dcx': 'IS-QZSS-DCX'}[prefix]
        source = table['source']  # A3 and the Japanese library are CAMF fields whose codes DCX-004 lists
        assert source.startswith(spec) or (prefix == 'camf' and source.startswith('IS-QZSS-DCX')), name


def test_every_code_table_a_record_names_is_in_the_file_or_one_azarashi_has_no_codes_of():
    names = {code['table'] for report in REPORTS for code in _codes(example_record(report))}
    assert names - set(CODE_TABLES) <= {n for n in names if n.startswith(('camf.a3_', 'camf.a11_'))}
    assert set(PROFILES) <= set(CODE_TABLES)


def test_a_code_of_a_table_the_file_lacks_is_undefined_and_unnamed():
    # a country or library version azarashi has no codes of: nothing to look up, and no need to
    missing = [code for report in REPORTS for code in _codes(example_record(report)) if code['table'] not in CODE_TABLES]
    assert {code['table'] for code in missing} >= {'camf.a3_provider_identifier.country_103'}
    assert all(code['status'] == 'undefined' and code['labels'] == {} for code in missing), missing


def test_the_international_library_has_one_table_for_every_country():
    international = {code['table'] for report in REPORTS for code in _codes(example_record(report))
                     if code['table'].startswith('camf.a11_') and '.international.' in code['table']}
    assert international == {'camf.a11_instruction_library.international.version_0'}


def test_the_envelope_is_defined_once_and_every_type_requires_its_nmea():
    assert SCHEMA['$ref'] == '#/$defs/envelope'
    assert len(SCHEMA['allOf']) == len(TYPE_NAMES) + 1  # one data definition chosen per report type
    row = record('Tsunami')
    del row['reception']['nmea']
    assert not VALIDATOR.is_valid(row)  # every type of this version has a QZQSM sentence
    envelope = Draft202012Validator({'$ref': '#/$defs/envelope', '$defs': SCHEMA['$defs']},
                                    format_checker=FormatChecker())
    assert envelope.is_valid(row)  # but the shared envelope leaves room for a carrier without one
    assert not envelope.is_valid({**row, 'unknown': 1})


def test_a_label_is_never_an_empty_string():
    row = record('LAlert')
    row['data']['severity']['labels']['en'] = ''
    assert not VALIDATOR.is_valid(row)  # a defined code with no name carries no label at all


def test_an_undefined_code_has_no_label():
    row = record('LAlert')
    row['data']['severity']['status'] = 'undefined'
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('name,field,state', [
    # each time field takes only the states its own decoding can reach
    ('Hypocenter', 'report_time', {'status': 'special', 'value': None, 'labels': {'en': 'x'},
                                   'source': {'month': 1, 'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'report_time', {'status': 'undefined', 'value': None,
                                   'source': {'month': 1, 'day': 1, 'hour': 1, 'minute': 1}}),
    ('LAlert', 'onset', {'status': 'special', 'value': None, 'source': {'week': 0, 'minute_of_week': 0}}),
    ('LAlert', 'onset', {'status': 'assumed', 'value': None, 'source': {'week': 0, 'minute_of_week': 1}}),
    ('LAlert', 'onset', {'status': 'undefined', 'value': None, 'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'occurrence_time', {'status': 'special', 'value': None, 'labels': {'en': 'x'},
                                       'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'occurrence_time', {'status': 'undefined', 'value': None, 'source': {'week': 0, 'minute_of_week': 0}}),
    ('Hypocenter', 'occurrence_time', {'status': 'valid', 'value': '2026-01-01T00:00:00Z', 'precision': 'day',
                                       'basis': 'report_time', 'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'occurrence_time', {'status': 'valid', 'value': None, 'precision': 'minute',
                                       'basis': 'report_time', 'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'occurrence_time', {'status': 'undefined', 'value': None, 'basis': 'report_time',
                                       'source': {'day': 1, 'hour': 1, 'minute': 1}}),
])
def test_a_time_field_refuses_a_state_it_cannot_reach(name, field, state):
    row = record(name)
    assert field in row['data']  # a key the record has, or the test proves nothing
    row['data'][field] = state
    assert not VALIDATOR.is_valid(row)


def test_report_time_is_always_read_against_the_reception_time():
    row = record('Hypocenter')
    assert row['data']['report_time']['basis'] == 'received_at'
    row['data']['report_time']['basis'] = 'report_time'
    assert not VALIDATOR.is_valid(row)  # nothing is completed from itself


@pytest.mark.parametrize('hour,minute,day,labels', [
    (31, 63, 0, {'ja': '津波到達中と推測', 'en': 'Tsunami arrival expected'}),
    (30, 62, 0, {'ja': '該当情報なし', 'en': 'No data'}),
])
def test_a_tsunami_arrival_that_is_not_a_time_says_what_it_is(hour, minute, day, labels):
    from azarashi import decode
    from test_dcr import TSUNAMI, _with_arrival_time
    arrival = example_record(decode(_with_arrival_time(TSUNAMI, 0, day, hour, minute)))['data']['forecasts'][0]['arrival']
    assert arrival == {'status': 'special', 'value': None, 'labels': labels,
                       'source': {'day': day, 'hour': hour, 'minute': minute}}


def test_a_northwest_pacific_arrival_that_is_not_a_time_is_arrived_or_unknown():
    from azarashi import decode
    from qzqsm import with_fields
    from test_dcr import NWP
    row = example_record(decode(with_fields(NWP, [(57, 5, 31), (62, 6, 63)])))
    assert row['data']['forecasts'][0]['arrival'] == {'status': 'special', 'value': None,
                                                      'labels': {'en': 'Arrived or Unknown'},
                                                      'source': {'day': 0, 'hour': 31, 'minute': 63}}
    VALIDATOR.validate(row)


@pytest.mark.parametrize('du,expected', [
    (0, ('valid', 'minute')), (4, ('valid', 'hour')), (5, ('valid', 'day')), (6, ('special', None)),
    (7, ('special', None)),
])
def test_a_volcano_activity_time_is_as_precise_as_its_ambiguity(du, expected):
    from azarashi import decode
    from qzqsm import with_fields
    from test_english import VOLCANO
    row = example_record(decode(with_fields(VOLCANO, [(50, 3, du)])))
    activity = row['data']['activity_time']
    assert (activity['status'], activity.get('precision')) == expected
    assert (activity['value'] is None) is (expected[0] != 'valid')
    if expected[0] == 'special':  # the day, hour and minute are not valid, as the ambiguity says
        assert activity['labels'] == row['data']['activity_time_ambiguity']['labels']
    VALIDATOR.validate(row)


def test_a_wrong_report_type_points_at_the_field_that_is_wrong():
    row = record('Tsunami')
    row['type'] = 'qzss.dcr.hypocenter'  # the data belongs to another type
    errors = [e for e in VALIDATOR.iter_errors(row) if list(e.absolute_path)[:1] == ['data']]
    assert errors and any('depth' in e.message for e in errors)


DCX_SHARED = ['message_type', 'country', 'provider', 'hazard', 'severity', 'duration', 'onset', 'instruction']


@pytest.mark.parametrize('name', ['OutsideJapan', 'LAlert', 'JAlert', 'MTInfo', 'Unknown'])
def test_the_dcx_alert_fields_are_defined_once(name):
    # one definition per field, so a constraint cannot reach some report types and miss others
    for field in DCX_SHARED:
        assert SCHEMA['$defs'][name]['properties'][field] == {'$ref': f'#/$defs/dcx_{field}'}, field


@pytest.mark.parametrize('name,version,status', [
    ('LAlert', 1, 'valid'), ('JAlert', 0, 'undefined'), ('MTInfo', 2, 'undefined'), ('OutsideJapan', 0, 'valid'),
    ('OutsideJapan', 5, 'valid'), ('Unknown', 1, 'undefined'), ('Unknown', 0, 'undefined'), ('Tsunami', 1, 'valid'),
    ('Tsunami', 2, 'undefined'),
])
def test_a_version_is_valid_where_it_is_the_one_the_specification_gives(name, version, status):
    # DCX-004 fixes it to 1 for the messages of Japan, leaves it to the sender outside Japan, and gives
    # none for a kind it does not define
    report = copy.deepcopy(next(r for r in REPORTS if type(r).__name__ == name))
    setattr(report, 'version' if name == 'Tsunami' else 'dcx_version', version)
    row = example_record(report)
    assert row['data']['version'] == {'status': status, 'value': version}
    VALIDATOR.validate(row)
    row['data']['version'] = {'status': 'valid' if status == 'undefined' else 'undefined', 'value': version}
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('name,path,value', [
    ('JAlert', ('target_regions', 0, 'table'), 'anything'),
    ('LAlert', ('provider', 'table'), 'qzss.dcr.tsunami_height'),
    ('LAlert', ('hazard', 'type', 'table'), 'qzss.dcr.tsunami_height'),
    ('LAlert', ('hazard', 'category', 'table'), 'camf.a4_hazard_type'),
    ('LAlert', ('hazard', 'definition', 'labels'), {'en': ''}),
    ('LAlert', ('instruction', 'library', 'table'), 'camf.a5_severity'),
    ('LAlert', ('instruction', 'content', 'table'), 'qzss.dcx.instruction.oops'),
    ('LAlert', ('version', 'value'), -5),
    ('LAlert', ('severity', 'code'), '07'),
])
def test_a_dcx_field_is_as_tightly_bound_as_a_dcr_one(name, path, value):
    row = record(name)
    node = row['data']
    for step in path[:-1]:
        node = node[step]
    assert path[-1] in node  # a key the record has, or the test proves nothing
    node[path[-1]] = value
    assert not VALIDATOR.is_valid(row)


def test_only_the_international_library_names_its_instruction():
    row = record('LAlert')
    assert row['data']['instruction']['library']['code'] == '1' and 'identifier' not in row['data']['instruction']
    row['data']['instruction']['identifier'] = 'IC-A-02'
    assert not VALIDATOR.is_valid(row)
    row = record('OutsideJapan')
    assert row['data']['instruction']['library']['code'] == '0'
    del row['data']['instruction']['identifier']
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('path,value', [
    (('main_ellipse', 'value', 'centre', 'latitude_deg'), 500),
    (('main_ellipse', 'value', 'centre', 'longitude_deg'), 200),
    (('main_ellipse', 'value', 'semi_major_axis_km'), -1),
    (('main_ellipse', 'value', 'semi_minor_axis_km'), 0),
    (('main_ellipse', 'value', 'azimuth_deg'), 200),
])
def test_an_ellipse_number_stays_in_range(path, value):
    row = record('OutsideJapan')
    node = row['data']
    for step in path[:-1]:
        node = node[step]
    assert path[-1] in node  # a key the record has, or the test proves nothing
    node[path[-1]] = value
    assert not VALIDATOR.is_valid(row)


def test_an_ellipse_keeps_the_range_of_its_own_group():
    # a refinement can pass the pole, and the evacuation ellipse counts longitude from 45 east
    def centre(name):
        return SCHEMA['$defs'][name]['properties']['value']['properties']['centre']['properties']
    assert centre('refined_ellipse')['latitude_deg']['maximum'] > 90
    assert (centre('additional_ellipse')['longitude_deg']['minimum'],
            centre('additional_ellipse')['longitude_deg']['maximum']) == (45, 225)
    hazard = SCHEMA['$defs']['specific_settings']['properties']['hazard_centre']['properties']['value']['properties']
    assert hazard['latitude_deg']['maximum'] == 100  # C5 offsets the main centre by up to ten degrees


@pytest.mark.parametrize('page', [{'number': 64}, {'number': -1}, {'total': 64}])
def test_a_nankai_page_number_is_a_six_bit_field(page):
    row = record('NankaiTroughEarthquake')
    row['data']['page'].update(page)
    assert not VALIDATOR.is_valid(row)


def test_a_quantity_takes_only_the_shapes_its_own_field_can_produce():
    row = record('Tsunami')
    height = row['data']['forecasts'][0]['height']
    del height['range']
    height['value'] = 3
    assert not VALIDATOR.is_valid(row)  # a tsunami height is a range, never one number
    row = record('Hypocenter')
    row['data']['depth']['range'] = {'lower': 1, 'upper': 2}
    assert not VALIDATOR.is_valid(row)  # a value and a range at once
    row = record('Hypocenter')
    row['data']['depth']['relative_to'] = 'main_ellipse.semi_major_axis'
    assert not VALIDATOR.is_valid(row)  # only D4 and C7 to C9 are measured against the main ellipse


@pytest.mark.parametrize('field,table', [
    ('provider', 'qzss.dcx.provider.country_111'),              # the carrier is not part of the code system
    ('provider', 'camf.a3_provider_identifier.111'),
    ('content', 'camf.a11_instruction_library.version_0'),       # a national library belongs to a country
    ('content', 'camf.a11_instruction_library.international.country_111.version_0'),
    ('content', 'qzss.dcx.a11_instruction_library.country_111.version_0'),
])
def test_a_country_scoped_table_keeps_its_shape(field, table):
    row = record('LAlert')
    target = row['data']['provider'] if field == 'provider' else row['data']['instruction']['content']
    target['table'] = table
    assert not VALIDATOR.is_valid(row)


def test_every_code_a_numeric_b4_field_can_carry_converts_to_a_valid_record():
    # decode each field at every value its width allows, defined or not, and validate the JSON
    from test_dcx_fields import B4_FIELDS, ELLIPSE, _decode, dcx

    numeric = {name.removeprefix('camf.') for name in PROFILES if name.startswith('camf.d')}
    checked = set()
    for hazards, fields in B4_FIELDS:
        for name, position, size, _table in fields:
            if name not in numeric or name in checked:
                continue
            checked.add(name)
            for code in range(1 << size):
                others = [(p, s, 0) for n, p, s, _ in fields if n != name]
                row = example_record(_decode(dcx([(position, size, code), *others], **ELLIPSE, a4=hazards[0], a17=3)))
                details = row['data']['specific_settings']['hazard_details']
                assert details[name.split('_', 1)[1]]['code'] == str(code)
                VALIDATOR.validate(row)
    assert checked == numeric


@pytest.mark.parametrize('a4, status', [(0, 'special'), (44, 'valid'), (127, 'undefined')])
def test_the_hazard_is_three_codes_of_one_value(a4, status):
    # type, category and definition are three tables of A4, and an undefined code has no text in any
    from test_dcx_fields import JAPAN, _decode, dcx
    hazard = example_record(_decode(dcx(**JAPAN, a3=1, a4=a4, a14=1)))['data']['hazard']
    assert list(hazard) == ['type', 'category', 'definition']
    for part, code in hazard.items():
        assert code['table'] == 'camf.a4_hazard_' + part and code['code'] == str(a4)
        assert code['status'] == status and bool(code['labels']) is (status != 'undefined')


def test_no_target_area_is_an_empty_list():
    from test_dcx_fields import JAPAN, _decode, dcx
    row = example_record(_decode(dcx(**JAPAN, a3=1, ex1=0)))
    assert row['data']['target_regions'] == []
    VALIDATOR.validate(row)


AMERICAN = re.compile(r'center|[a-z]{3}iz(e|es|ed|ing|ation)(\b|_)|yze|meter|liter|color|behavior|gray|catalog|defense')
BRITISH = re.compile(r'centre|[a-z]{3}is(e|es|ed|ing|ation)(\b|_)|yse|metre|litre|colour|behaviour|grey|catalogue|defence')
CHOSEN = ('type', 'status', 'basis', 'precision', 'lifecycle', 'unit', 'relative_to')  # values azarashi names


def _record_words(node):
    """The keys of a record and the values azarashi names; not the text of a code table or a table name."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            if key in CHOSEN and isinstance(value, str):
                yield value
            elif key not in ('labels', 'table'):
                yield from _record_words(value)
    elif isinstance(node, list):
        for value in node:
            yield from _record_words(value)


def test_a_name_is_spelled_as_its_specification_spells_it():
    # the JMA reports write American English and CAMF British; the names both share keep one spelling
    rows = [example_record(r) for r in fixtures()]
    rows += [{'type': 'qzss.dcx.unknown', 'data': {'specific_settings': {
        'hazard_details': dict.fromkeys(SCHEMA['$defs']['hazard_details']['properties'])}}}]  # every B4 detail
    words = {service: {w for row in rows if row['type'].startswith(f'qzss.{service}.')
                       for w in _record_words({'type': row['type'], 'data': row['data']})}
             for service in ('dcr', 'dcx')}
    jma, camf = words['dcr'] - words['dcx'], words['dcx'] - words['dcr']
    assert {'epicenter', 'qzss.dcr.hypocenter'} <= jma and {'centre', 'hazard_centre'} <= camf
    assert 'status' in words['dcr'] & words['dcx']
    assert not sorted(w for w in jma if BRITISH.search(w))
    assert not sorted(w for w in camf if AMERICAN.search(w))


def test_the_sentences_azarashi_translated_say_so():
    # the note travels with the sentence; docs/english-translation-policy.md lists the rest of azarashi's English
    import importlib
    import pkgutil
    from azarashi.definitions.qzss import dcr
    note = ' (Translated by azarashi)'
    noted = {(name.name, code) for name in pkgutil.iter_modules(dcr.__path__)
             for code, text in getattr(importlib.import_module(f'{dcr.__name__}.{name.name}'),
                                        name.name + '_en', {}).items() if note in text}
    assert noted == {('notification_on_disaster_prevention', c) for c in (101, 102, 110, 112, 113, 114, 115, 216)}
    labels = TABLES['qzss.dcr.notification_on_disaster_prevention'].labels(115)
    assert labels['en'].endswith(note) and note not in labels['ja']


def test_the_test_flag_of_every_logged_report():
    seen = set()
    for log, received in LOGS.items():
        for line in open(f'{TESTS}/{log}', encoding='utf-8'):
            if not line.startswith('$QZQSM'):
                continue
            report = nmea.Decoder(line.strip(), timestamp=received).decode()
            record = example_record(report)
            data = record['data']
            if record['type'].startswith('qzss.dcr.'):
                expected = data['report_classification']['code'] == '7'
            elif record['type'] == 'qzss.dcx.null':
                expected = False
            else:
                expected = data['message_type']['code'] == '0'
            assert record['is_test'] is expected
            seen.add((record['type'].split('.')[1], record['is_test']))
    assert seen == {('dcr', True), ('dcr', False), ('dcx', True), ('dcx', False)}


def test_the_second_ellipse_gives_each_transform_in_the_terms_of_the_main_one():
    from test_dcx_fields import ELLIPSE, _decode, dcx
    report = _decode(dcx([(131, 2, 3), (133, 3, 7), (136, 5, 8), (141, 5, 0)], **ELLIPSE, a17=2))
    row = example_record(report)
    second = row['data']['specific_settings']['second_ellipse']
    assert list(second) == ['shift', 'scale_factor', 'bearing', 'instruction']
    assert {key: (value['value'], value['unit'], value['relative_to'], value['labels'])
            for key, value in second.items() if key != 'instruction'} == {
        'shift': (3, '1', 'main_ellipse.semi_major_axis', {'en': '3'}),  # CAMF 3.7.3.1
        'scale_factor': (2.0, '1', 'main_ellipse', {'en': '2'}),  # 3.7.3.2, both semi-axes
        'bearing': (90.0, 'deg', 'main_ellipse.azimuth', {'en': '90°'}),  # 3.7.3.3, turned from the azimuth
    }
    assert (second['scale_factor']['value'], second['bearing']['value']) == (
        report.c8_homothetic_factor_of_second_ellipse, report.c9_bearing_angle_of_second_ellipse)
    assert second['instruction'] == {'status': 'special', 'code': '0',
                                     'table': 'camf.c10_instruction_library_for_second_ellipse',
                                     'labels': {'en': 'No instruction'}}  # 3.7.3.4: the empty field
    VALIDATOR.validate(row)


def test_a_value_dcx_004_calls_not_used_is_special_and_says_so():
    # IS-QZSS-DCX-004 2.4: a value assigned to say there is none
    from test_dcx_fields import _decode, dcx
    data = example_record(_decode(dcx(a1=1, a2=10, a3=0, a4=0, a14=1)))['data']
    for code in (data['provider'], *data['hazard'].values()):
        assert (code['status'], code['code'], code['labels']) == ('special', '0', {'en': 'Not used'})
    assert (data['onset']['status'], data['onset']['labels']) == ('special', {'en': 'Not used'})


def test_a_code_dcx_004_calls_reserved_is_undefined():
    # IS-QZSS-DCX-004 2.4: a value not assigned yet, which a later edition may give a meaning
    from test_dcx_fields import _decode, dcx
    data = example_record(_decode(dcx(a1=1, a2=10, a3=2, a9=0, a11=0, a14=1)))['data']
    assert data['instruction']['content'] == {'status': 'undefined', 'code': '0',
                                              'table': 'camf.a11_instruction_library.international.version_0',
                                              'labels': {}}
    assert data['instruction']['identifier'] == 'IC-A-01'
    assert '0' not in CODE_TABLES['camf.a11_instruction_library.international.version_0']['codes']


def test_every_provider_table_is_that_of_dcx_004():
    providers = {name: table for name, table in CODE_TABLES.items() if name.startswith('camf.a3_provider_identifier.')}
    assert set(providers) == {f'camf.a3_provider_identifier.country_{n}' for n in (10, 71, 111, 219)}
    assert {table['source'] for table in providers.values()} == {'IS-QZSS-DCX-004 Table 4.2-6'}


def test_a_code_jma_sends_for_a_value_its_table_lacks_is_special():
    # IS-QZSS-DCR-017: "There is a case to transmit undefined codes due to revise the JMA system."
    expected = {('qzss.dcr.tsunami_warning_code', '15'), ('qzss.dcr.information_serial_code', '15'),
                ('qzss.dcr.local_government', '199999'), ('qzss.dcr.flood_forecast_region', '829999999999'),
                ('qzss.dcr.tsunamigenic_potential', '7'), ('qzss.dcr.coastal_region', '100')}
    for table, code in expected:
        assert CODE_TABLES[table]['codes'][code]['status'] == 'special', (table, code)
    assert CODE_TABLES['qzss.dcr.local_government']['codes']['199999']['labels']['ja'] == '北海道のその他の市町村'
    # a text that only uses the word, and CAMF's category named OTHER, are values of their own
    assert CODE_TABLES['qzss.dcr.information_serial_code']['codes']['3']['status'] == 'valid'
    assert CODE_TABLES['camf.a4_hazard_category']['codes']['113']['status'] == 'valid'
