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
