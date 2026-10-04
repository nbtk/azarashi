"""Public JSON output, independent values, and caller errors."""
import copy
import json
from datetime import datetime

import pytest

import azarashi
from azarashi import reports
from samples import EEW
from test_declared_types import REPORTS


def test_ndjson_is_one_line_and_round_trips():
    report = azarashi.decode(EEW)
    line = azarashi.to_ndjson(report)
    assert line.endswith('\n') and line.count('\n') == 1
    value = json.loads(line)
    assert value == azarashi.to_json_dict(report)
    assert value['texts']['ja'] == str(report)
    assert '\n' in value['texts']['ja'] and '緊急地震速報' in line


def test_json_values_are_detached_in_both_directions():
    report = copy.deepcopy(next(r for r in REPORTS if type(r) is reports.dcr.Hypocenter))
    original = azarashi.to_json_dict(report)
    output = azarashi.to_json_dict(report)
    output['data']['position']['source']['latitude_degrees'] = 88
    output['data']['notifications'].clear()
    assert azarashi.to_json_dict(report) == original
    report.coordinates_of_hypocenter_raw['lat_d'] = 12
    assert original['data']['position']['source']['latitude_degrees'] != 12


def test_schema_is_a_fresh_copy():
    first = azarashi.json_schema()
    first['$defs'].clear()
    assert azarashi.json_schema()['$defs']


def test_code_tables_are_a_fresh_copy():
    first = azarashi.code_tables()
    first['tables'].clear()
    assert azarashi.code_tables()['tables']


def test_subclasses_use_the_supported_base_contract():
    class Custom(reports.dcr.EarthquakeEarlyWarning):
        pass
    original = azarashi.decode(EEW)
    custom = Custom(**original.get_params())
    custom.application_only = object()
    assert azarashi.to_json_dict(custom) == azarashi.to_json_dict(original)


def test_unsupported_objects_raise_type_error():
    with pytest.raises(TypeError, match='Unsupported report'):
        azarashi.to_json_dict(object())


def test_naive_datetime_is_rejected():
    report = azarashi.decode(EEW)
    report.timestamp = datetime(2026, 1, 1)
    with pytest.raises(ValueError, match='Naive'):
        azarashi.to_json_dict(report)


@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_numbers_are_rejected_by_both_apis(bad):
    report = copy.deepcopy(next(r for r in REPORTS if type(r) is reports.dcx.OutsideJapan))
    report.a12_ellipse_centre_latitude = bad
    for convert in (azarashi.to_json_dict, azarashi.to_ndjson):
        with pytest.raises(ValueError, match='finite'):
            convert(report)


def test_parallel_lists_are_not_silently_truncated():
    report = copy.deepcopy(next(r for r in REPORTS if type(r) is reports.dcr.Tsunami))
    report.tsunami_heights_raw.pop()
    with pytest.raises(ValueError):
        azarashi.to_json_dict(report)


def test_quantity_profiles_agree_with_the_code_tables():
    """The numeric profiles live beside the code tables they interpret, so tie them together."""
    import re

    from azarashi.json.model import PROFILES
    from azarashi.json.tables import TABLES

    for name, (scalar, ranges, _unit) in PROFILES.items():
        if not name.startswith('qzss.dcr.'):
            continue
        table = TABLES[name]
        for group in (scalar, ranges):
            undefined = [code for code in group if code not in table.codes]
            assert undefined == [], f'{name}: {undefined} carry a meaning no code table defines'
        for code, number in scalar.items():
            label = next(iter(table.labels(code).values()))
            shown = re.match(r'(\d+(?:\.\d+)?)', label)
            assert shown is not None, f'{name}[{code}]: {label!r} names no number'
            assert float(shown.group(1)) == float(number), f'{name}[{code}]: {label!r} is not {number}'
        for code, (lower, upper) in ranges.items():
            labels = ' '.join(table.labels(code).values())
            edges = [edge for edge in (lower, upper) if edge is not None]
            assert any(re.search(rf'(?<![\d.]){edge:g}(?![\d])', labels) for edge in edges), \
                f'{name}[{code}]: {labels!r} names none of {edges}'


def test_a_code_defined_without_a_name_carries_no_label():
    from azarashi.json.tables import Table

    assert Table('x.y', {0: ''}, None, None).code(0) == {'status': 'valid', 'code': '0', 'table': 'x.y', 'labels': {}}


def test_an_ex9_prefecture_has_the_code_of_its_place_in_the_table():
    # IS-QZSS-DCX-004 Table 4.2-25 from the top, the codes of IS-QZSS-DCR-017 Table 4.1.2-16
    from azarashi.json.tables import TABLES, Table, _prefecture_names

    ex9, dcr = TABLES['qzss.dcx.ex9_target_area_code_list'], TABLES['qzss.dcr.prefecture']
    assert ex9.codes == dcr.codes == tuple(range(1, 48))
    assert all(ex9.labels(code) == dcr.labels(code) for code in ex9.codes)
    assert ex9.code(1)['labels'] == {'ja': '北海道', 'en': 'Hokkaido Prefecture'}
    assert ex9.code(13)['labels'] == {'ja': '東京都', 'en': 'Tokyo Metropolis'}
    assert ex9.code(47)['labels'] == {'ja': '沖縄県', 'en': 'Okinawa Prefecture'}
    unnamed = Table('qzss.dcx.ex9_target_area_code_list', _prefecture_names({}), _prefecture_names({}), None).code(13)
    assert unnamed == {'status': 'undefined', 'code': '13', 'table': 'qzss.dcx.ex9_target_area_code_list', 'labels': {}}


def _printed_numbers(field, label):
    """The numbers a CAMF B4 label prints, in the unit its JSON profile uses."""
    import re

    if field.startswith('d13_'):  # metres and kilometres, reported in metres
        return {float(n) * (1000 if unit == 'km' else 1) for n, unit in re.findall(r'(\d+)\s*(km|m)\b', label)}
    if field.startswith('d29_'):  # minutes, hours and days, reported in minutes
        found = {float(int(h) * 60 + int(m)) for h, m in re.findall(r'(\d+)\s*h\s+(\d+)\s*min', label)}
        rest = re.sub(r'(\d+)\s*h\s+(\d+)\s*min', '', label)
        found |= {float(int(n) * 60) for n in re.findall(r'(\d+)\s*h\b', rest)}
        found |= {float(n) for n in re.findall(r'(\d+)\s*min', rest)}
        found |= {float(int(n) * 1440) for n in re.findall(r'(\d+)\s*days?', rest)}
        if re.search(r'(?<![\d.])0\s*<', label):
            found.add(0.0)
        return found
    return {float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', label)}


def test_camf_profiles_are_transcribed_from_their_tables():
    """The ranges are written out by hand from the specification; the printed labels check the copy."""
    from itertools import pairwise

    from azarashi.definitions.camf import d_fields
    from azarashi.json.model import PROFILES

    for name, (scalar, ranges, _unit) in PROFILES.items():
        if not name.startswith('camf.d'):
            continue
        field = name.removeprefix('camf.')
        table = getattr(d_fields, field)
        assert set(scalar) | set(ranges) == set(table), f'{field}: not one row per defined code'
        if scalar:  # the numbers are the definition's own, and its names print them
            assert scalar is getattr(d_fields, field + '_value'), field
        rows = [ranges[code] for code in sorted(ranges)]
        for code, (lower, upper) in zip(sorted(ranges), rows, strict=True):
            edge = lower if lower is not None else upper
            assert float(edge) in _printed_numbers(field, table[code]), f'{field}[{code}]: {edge} not in {table[code]!r}'
        if field != 'd26_number_of_cases_per_100000_inhabitants':
            for (_, upper), (lower, _) in pairwise(rows):
                assert upper == lower, f'{field}: a gap or an overlap at {upper} / {lower}'
