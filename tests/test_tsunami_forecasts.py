"""Region-wise snapshots preserve transmitted codes and existing mutable report lists."""
import pytest

import azarashi
from qzqsm import with_fields
from test_dcr import TSUNAMI, _with_arrival_time


def test_forecasts_group_every_parallel_field_without_changing_output():
    report = azarashi.decode(TSUNAMI)
    before, text = report.get_params(), str(report)
    forecasts = report.forecasts
    assert len(forecasts) == len(report.tsunami_forecast_regions) > 1
    for i, forecast in enumerate(forecasts):
        assert forecast.region == report.tsunami_forecast_regions[i]
        assert forecast.region_code == report.tsunami_forecast_regions_raw[i]
        assert forecast.height == report.tsunami_heights[i]
        assert forecast.height_code == report.tsunami_heights_raw[i]
        assert forecast.arrival_time == report.expected_tsunami_arrival_times[i]
        assert forecast.arrival_time_raw == report.expected_tsunami_arrival_times_raw[i]
        assert forecast.arrival_time_type == report.expected_tsunami_arrival_time_types[i]
    assert report.get_params() == before and str(report) == text
    assert 'forecasts' not in report.get_params()


def test_forecasts_are_detached_and_reflect_changes_on_next_access():
    report = azarashi.decode(TSUNAMI)
    first = report.forecasts
    first[0].region = 'edited snapshot'
    first[0].arrival_time_raw['hour'] = 99
    assert report.tsunami_forecast_regions[0] != 'edited snapshot'
    assert report.expected_tsunami_arrival_times_raw[0]['hour'] != 99
    report.tsunami_heights[0] = 'edited source'
    assert first[0].height != 'edited source'
    assert report.forecasts[0].height == 'edited source'


@pytest.mark.parametrize('field', [
    'tsunami_forecast_regions', 'tsunami_forecast_regions_raw',
    'tsunami_heights', 'tsunami_heights_raw', 'expected_tsunami_arrival_times',
    'expected_tsunami_arrival_times_raw', 'expected_tsunami_arrival_time_types',
])
def test_forecasts_reject_misaligned_lists(field):
    report = azarashi.decode(TSUNAMI)
    getattr(report, field).pop()
    with pytest.raises(ValueError):
        _ = report.forecasts


@pytest.mark.parametrize('day,hour,minute', [(0, 31, 63), (0, 30, 62), (1, 29, 61), (0, 12, 30)])
@pytest.mark.parametrize('height', [13, 14, 15])
def test_forecasts_preserve_special_values(day, hour, minute, height):
    message = _with_arrival_time(TSUNAMI, 0, day, hour, minute)
    report = azarashi.decode(with_fields(message, [(96, 4, height)]))
    forecast = report.forecasts[0]
    assert forecast.arrival_time_raw == {'day': day, 'hour': hour, 'minute': minute}
    assert forecast.height_code == height
    assert forecast.height == report.tsunami_heights[0]
    assert forecast.arrival_time_type == report.expected_tsunami_arrival_time_types[0]
    assert forecast.arrival_time == report.expected_tsunami_arrival_times[0]
