"""Validate JSON output and saved examples against the bundled wire contract."""
import copy
import json
from pathlib import Path

import pytest

from azarashi import json_schema, to_json_dict as example_record
from azarashi._serialization import TYPE_NAMES, dcr_value
from schema.generate import fixtures
from test_declared_types import REPORTS

# skip this file alone, rather than stopping the whole suite at collection
jsonschema = pytest.importorskip('jsonschema', reason="pip install 'jsonschema[format]'")
Draft202012Validator, FormatChecker = jsonschema.Draft202012Validator, jsonschema.FormatChecker

FOLDER = Path(__file__).resolve().parent.parent / 'docs/schemas'
SCHEMA = json_schema()
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def test_schema_is_valid_and_reproducible():
    Draft202012Validator.check_schema(SCHEMA)
    assert json_schema() == SCHEMA


@pytest.mark.parametrize('report', REPORTS)
def test_real_and_crafted_reports_conform(report):
    VALIDATOR.validate(example_record(report))


def test_saved_examples_are_complete_reproducible_and_cover_all_types():
    rows = [json.loads(line) for line in (FOLDER / 'report-v1.examples.ndjson').read_text(encoding='utf-8').splitlines()]
    assert rows == json.loads((FOLDER / 'report-v1.examples.pretty.json').read_text(encoding='utf-8'))
    assert rows == [example_record(r) for r in fixtures()]
    assert {r['type'] for r in rows} == set(TYPE_NAMES.values())
    for row in rows:
        VALIDATOR.validate(row)


def record(name):
    return example_record(next(r for r in REPORTS if type(r).__name__ == name))


@pytest.mark.parametrize('field', ['schema_version', 'type', 'received_at', 'satellite', 'nmea', 'text', 'data'])
def test_envelope_fields_are_required(field):
    row = record('Tsunami')
    del row[field]
    assert not VALIDATOR.is_valid(row)


@pytest.mark.parametrize('field,value', [('schema_version', 2), ('nmea', ''), ('nmea', '$QZQSM,55,broken*00'),
    ('received_at', '2026-02-30T01:00:00Z'), ('received_at', '2026-03-01T01:00:00+09:00'),
    ('satellite', {'system': 'qzss', 'prn': None}), ('unknown', 1)])
def test_invalid_envelope_rejected(field, value):
    row = record('Tsunami')
    row[field] = value
    assert not VALIDATOR.is_valid(row)


def test_forecast_cannot_lose_its_region_or_height():
    for field in ('region', 'arrival', 'height'):
        row = record('Tsunami')
        del row['data']['forecasts'][0][field]
        assert not VALIDATOR.is_valid(row)


def test_tsunami_height_is_the_announced_interval():
    height = record('Tsunami')['data']['forecasts'][0]['height']
    assert height['kind'] == 'bounds'
    assert height['lower'] == {'value': 1, 'inclusive': False}
    assert height['upper'] == {'value': 3, 'inclusive': True}
    assert height['code']['labels']['ja'] == '3m'


def test_quantity_special_values_are_not_zero_or_false():
    assert dcr_value('depth_of_hypocenter', 10)['value'] == 10
    assert dcr_value('depth_of_hypocenter', 501)['lower'] == {'value': 500, 'inclusive': False}
    assert dcr_value('depth_of_hypocenter', 511)['reason'] == 'unknown'
    unknown = dcr_value('depth_of_hypocenter', 502)
    assert unknown['reason'] == 'unrecognized_code'
    assert unknown['code'] == {'scheme': 'qzss.dcr.depth_of_hypocenter', 'code': '502', 'recognized': False, 'labels': {}}
    assert dcr_value('hypocenter_magnitude', 126)['qualifier'] == 'unknown_value'


def test_jalert_forbids_camf_and_ellipse_fields():
    for key in ('camf', 'main_ellipse', 'specific_settings', 'evacuation'):
        row = record('JAlert')
        row['data'][key] = {}
        assert not VALIDATOR.is_valid(row)


def test_ellipse_is_an_atomic_group():
    row = record('OutsideJapan')
    del row['data']['main_ellipse']['semi_minor_axis_km']
    assert not VALIDATOR.is_valid(row)


def test_quantity_rejects_empty_bounds_and_wrong_units():
    for change in ({'lower': None, 'upper': None}, {'unit': 'km'}):
        row = record('Tsunami')
        row['data']['forecasts'][0]['height'].update(change)
        assert not VALIDATOR.is_valid(row)


def test_null_message_carries_no_alert():
    row = record('NullMsg')
    assert row['data'] == {}
    row['data']['onset'] = None
    assert not VALIDATOR.is_valid(row)


def test_no_input_report_is_mutated():
    r = next(r for r in REPORTS if type(r).__name__ == 'Tsunami')
    before = copy.deepcopy(r.get_params())
    example_record(r)
    assert r.get_params() == before


def test_every_dcr_source_field_has_a_mapping_or_explicit_omission():
    from azarashi._serialization import COMMON, DCR_TYPES, LISTS, SINGLES, TIMES
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
            used.update([TIMES[name], TIMES[name] + '_raw'])
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
    assert settings['kind'] == 'refined_ellipse'
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


@pytest.mark.parametrize('name', SETTINGS_TYPES)
def test_specific_settings_is_defined_once_for_every_type_that_carries_it(name):
    # one definition, so that a change cannot reach some report types and miss others
    assert SCHEMA['$defs'][name]['properties']['specific_settings'] == {'$ref': '#/$defs/specific_settings'}


@pytest.mark.parametrize('name', SETTINGS_TYPES)
@pytest.mark.parametrize('kind', ['hazard_centre', 'second_ellipse'])
def test_every_kind_of_specific_settings_is_accepted_under_every_type(name, kind):
    settings = next(s for r in REPORTS if hasattr(r, 'camf')
                    if (s := example_record(r)['data'].get('specific_settings')) and s['kind'] == kind)
    row = record(name)
    row['data']['specific_settings'] = settings
    VALIDATOR.validate(row)


def _codes(node):
    """Every code object in a record."""
    if isinstance(node, dict):
        if {'scheme', 'code', 'recognized', 'labels'} <= set(node):
            yield node
        for value in node.values():
            yield from _codes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _codes(value)


def test_a_scheme_names_the_specification_that_defines_its_table():
    # camf for what CAMF defines, the service's own name for what the service assigns itself
    import importlib
    import pkgutil

    def tables(package):
        """Every code table the package holds, by the name the scheme uses for it."""
        root = importlib.import_module(package)
        found = set()
        for module in pkgutil.iter_modules(root.__path__):
            for name, value in vars(importlib.import_module(f'{package}.{module.name}')).items():
                if isinstance(value, dict) and not name.startswith('_'):
                    found.add(name)
        return found

    owner = {'camf': tables('azarashi.definitions.camf'),
             'qzss.dcx': tables('azarashi.definitions.qzss.dcx'),
             'qzss.dcr': tables('azarashi.definitions.qzss.dcr')}
    schemes = {code['scheme'] for report in REPORTS for code in _codes(example_record(report))}
    assert schemes, 'no code objects to check'
    checked = 0
    for scheme in schemes:
        root, table = scheme.rsplit('.', 1)
        holders = [name for name, names in owner.items() if table in names]
        if not holders:
            continue  # provider, instruction and the bit or area codes carry transmitted values
        assert holders == [root], f'{scheme}: {table} is defined by {holders}'
        checked += 1
    assert checked > 40, checked


def test_the_international_library_has_one_scheme_for_every_country():
    international = {code['scheme'] for report in REPORTS for code in _codes(example_record(report))
                     if '.instruction.' in code['scheme'] and '.library_0.' in code['scheme']}
    assert international == {'camf.instruction.library_0.version_0'}


def test_the_envelope_is_defined_once_and_every_type_requires_its_nmea():
    assert len([b for b in SCHEMA['oneOf'] if {'$ref': '#/$defs/envelope'} in b['allOf']]) == len(SCHEMA['oneOf'])
    row = record('Tsunami')
    del row['nmea']
    assert not VALIDATOR.is_valid(row)  # every type of this version has a QZQSM sentence
    envelope = Draft202012Validator({**SCHEMA, 'oneOf': [{'$ref': '#/$defs/envelope'}]},
                                    format_checker=FormatChecker())
    assert envelope.is_valid(row)  # but the shared envelope leaves room for a carrier without one
    assert not envelope.is_valid({**row, 'unknown': 1})


def test_a_label_is_never_an_empty_string():
    row = record('LAlert')
    row['data']['severity']['labels']['en'] = ''
    assert not VALIDATOR.is_valid(row)  # a defined code with no name carries no label at all


@pytest.mark.parametrize('name,field,state', [
    # each time field takes only the states its own decoding can reach
    ('Hypocenter', 'report_time', {'status': 'not_used', 'value': None, 'basis': None}),
    ('Hypocenter', 'report_time', {'status': 'unrecognized_code', 'value': None, 'basis': None,
                                   'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('LAlert', 'onset', {'status': 'no_information', 'value': None, 'basis': None}),
    ('LAlert', 'onset', {'status': 'unrecognized_code', 'value': None, 'basis': None,
                         'source': {'day': 1, 'hour': 1, 'minute': 1}}),
    ('Hypocenter', 'occurrence_time_of_earthquake', {'status': 'not_used', 'value': None, 'basis': None}),
    ('Hypocenter', 'occurrence_time_of_earthquake', {'status': 'unrecognized_code', 'value': None,
                                                     'basis': None, 'source': {'week': 0, 'minute_of_week': 0}}),
])
def test_a_time_field_refuses_a_state_it_cannot_reach(name, field, state):
    row = record(name)
    row['data'][field] = state
    assert not VALIDATOR.is_valid(row)


def test_report_time_is_always_read_against_the_reception_time():
    row = record('Hypocenter')
    assert row['data']['report_time']['basis'] == 'received_at'
    row['data']['report_time']['basis'] = 'report_time'
    assert not VALIDATOR.is_valid(row)  # nothing is completed from itself


@pytest.mark.parametrize('name,other', [('Tsunami', 'arrived_or_unknown'),
                                        ('NorthwestPacificTsunami', 'arrival_estimated')])
def test_an_arrival_refuses_the_other_sea_area_state(name, other):
    row = record(name)
    row['data']['forecasts'][0]['arrival'] = {'status': other, 'value': None, 'basis': None}
    assert not VALIDATOR.is_valid(row)
