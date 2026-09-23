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
    assert value['text'] == str(report)
    assert '\n' in value['text'] and '緊急地震速報' in line


def test_json_values_are_detached_in_both_directions():
    report = copy.deepcopy(next(r for r in REPORTS if type(r) is reports.dcr.Hypocenter))
    original = azarashi.to_json_dict(report)
    output = azarashi.to_json_dict(report)
    output['data']['position']['source']['lat_d'] = 88
    output['data']['notifications'].clear()
    assert azarashi.to_json_dict(report) == original
    report.coordinates_of_hypocenter_raw['lat_d'] = 12
    assert original['data']['position']['source']['lat_d'] != 12


def test_schema_is_a_fresh_copy():
    first = azarashi.json_schema()
    first['$defs'].clear()
    assert azarashi.json_schema()['$defs']


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
    import importlib
    import re

    from azarashi.json.model import PROFILES

    for table_name, (scalar, bounds, _missing, _unit) in PROFILES.items():
        module = importlib.import_module(f'azarashi.definitions.qzss.dcr.{table_name}')
        table = getattr(module, table_name, None) or getattr(module, table_name + '_en')
        for group in (scalar, bounds, _missing):
            undefined = [code for code in group if code not in table]
            assert undefined == [], f'{table_name}: {undefined} carry a meaning no code table defines'
        for code, number in scalar.items():
            shown = re.match(r'(\d+(?:\.\d+)?)', table[code])
            assert shown is not None, f'{table_name}[{code}]: {table[code]!r} names no number'
            assert float(shown.group(1)) == float(number), f'{table_name}[{code}]: {table[code]!r} is not {number}'
        for code, (lower, upper) in bounds.items():
            if not isinstance(table[code], str):  # a defined code may carry no display string
                continue
            edges = [edge['value'] for edge in (lower, upper) if edge is not None]
            assert any(re.search(rf'(?<![\d.]){edge:g}(?![\d])', table[code]) for edge in edges), \
                f'{table_name}[{code}]: {table[code]!r} names none of {edges}'


def test_a_code_defined_without_a_name_carries_no_label():
    from azarashi.json.model import coded

    assert coded('x', 0, {0: ''}) == {'scheme': 'x', 'code': '0', 'recognized': True, 'labels': {}}


def test_an_unnamed_prefecture_bit_keeps_its_position(monkeypatch):
    from azarashi.json import model

    assert model.prefecture_bit(12)['labels'] == {'ja': '東京都', 'en': 'Tokyo'}
    # substitutes, because the decoder lists the prefectures in the real tables' own order
    monkeypatch.setattr(model, 'ex9_target_area_code_ja', {})
    monkeypatch.setattr(model, 'ex9_target_area_code_en', {})
    unnamed = model.prefecture_bit(12)
    assert unnamed == {'scheme': 'qzss.dcx.prefecture_bit', 'code': '12', 'recognized': False, 'labels': {}}
