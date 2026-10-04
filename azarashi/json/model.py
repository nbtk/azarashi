"""Report JSON conversion. Field selection is explicit; arbitrary instance attributes are not exported.

Every field of data has one of a few outer shapes: a code, a quantity, a time, a position or a
group of values, each with a status that says whether the value can be used as it is.
"""

import math
from datetime import UTC, datetime
from itertools import pairwise
from collections.abc import Mapping
from typing import Any, Literal, TypeAlias, cast

from .. import reports
from ..definitions.camf.a11_library import a11_library
from ..definitions.camf.a7_hazard_onset_time_of_week import a7_hazard_onset_time_of_week_not_used_en
from ..definitions.camf.c7_shift_of_second_ellipse_centre import c7_shift_of_second_ellipse_centre_value
from ..definitions.camf.c8_homothetic_factor_of_second_ellipse import c8_homothetic_factor_of_second_ellipse_value
from ..definitions.camf.c9_bearing_angle_of_second_ellipse import c9_bearing_angle_of_second_ellipse_value
from ..definitions.camf.d_fields import d3_azimuth_from_centre_of_main_ellipse_to_epicentre_value
from ..definitions.camf.d_fields import d4_vector_length_between_centre_of_main_ellipse_and_epicentre_value
from ..definitions.qzss.dcr.day_hour_minute import expected_tsunami_arrival_time_kind
from ..definitions.qzss.dcr.latitude_and_longitude import is_position
from ..definitions.qzss.dcx.ex9_target_area_code import EX9_PREFECTURE_BITS
from ..exceptions import AzarashiArgumentTypeError
from ..reports.base import Coordinates, DayHourMinute
from .tables import B4_NAMES, TABLES, Table, instruction, prefecture_code, provider

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Naive datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def utc_milliseconds(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Naive datetime")
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


Range: TypeAlias = tuple[float | None, float | None]  # (lower, upper), None where it is open


def _up_to(*edges: float, floor: float | None = None) -> dict[int, Range]:
    """Contiguous ranges up to each edge: the first from the floor, or from nothing, the last without end."""
    rows: list[Range] = [(floor, edges[0]), *pairwise(edges), (edges[-1], None)]
    return dict(enumerate(rows))


def _from(*edges: float, floor: float | None = None) -> dict[int, Range]:
    """Contiguous ranges from each edge, the last without end; a floor adds a first range below them."""
    rows: list[Range] = [] if floor is None else [(floor, edges[0])]
    rows += pairwise(edges)
    rows.append((edges[-1], None))
    return dict(enumerate(rows))


#: a quantity table: the codes that are one number, those that are a range, and the UCUM unit
Profile: TypeAlias = tuple[Mapping[int, float], Mapping[int, Range], str]

PROFILES: dict[str, Profile] = {
    "qzss.dcr.depth_of_hypocenter": ({i: i for i in range(501)}, {501: (500, None)}, "km"),
    "qzss.dcr.eew_magnitude": ({i: i / 10 for i in range(1, 101)}, {101: (10, None)}, "1"),
    "qzss.dcr.hypocenter_magnitude": ({i: i / 10 for i in range(1, 101)}, {101: (10, None), 126: (8, None)}, "1"),
    "qzss.dcr.tsunami_height": (
        {},
        {1: (None, 0.2), 2: (0.2, 1), 3: (1, 3), 4: (3, 5), 5: (5, 10), 6: (10, None)},
        "m",
    ),
    "qzss.dcr.northwest_pacific_tsunami_height": (
        {},
        {1: (0.3, 1), 2: (1, 3), 3: (3, 5), 4: (5, 10), 508: (10, None)},
        "m",
    ),
    "qzss.dcr.typhoon_central_pressure": ({i: i for i in range(1101)}, {}, "hPa"),
    "qzss.dcr.typhoon_maximum_wind_speed": ({i: i for i in range(15, 106)}, {}, "m/s"),
    "qzss.dcr.typhoon_maximum_gust_wind_speed": ({i: i for i in range(15, 106)}, {}, "m/s"),
    "qzss.dcr.expected_ash_fall_time": ({i: i for i in range(1, 7)}, {}, "h"),
    "qzss.dcr.typhoon_elapsed_time_from_reference_time": ({i: i for i in range(128)}, {}, "h"),
    # CAMF Issue 1.2, 18.4.35: the B4 details that are numbers or numeric ranges, by the numbers the tables print
    "camf.d1_magnitude_on_richter_scale": ({}, _from(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0), "1"),
    "camf.d3_azimuth_from_centre_of_main_ellipse_to_epicentre": (
        d3_azimuth_from_centre_of_main_ellipse_to_epicentre_value,
        {},
        "deg",
    ),
    "camf.d4_vector_length_between_centre_of_main_ellipse_and_epicentre": (
        d4_vector_length_between_centre_of_main_ellipse_and_epicentre_value,
        {},
        "1",
    ),
    # CAMF Issue 1.2, 18.3: the second ellipse, made from the main one
    "camf.c7_shift_of_second_ellipse_centre": (c7_shift_of_second_ellipse_centre_value, {}, "1"),
    "camf.c8_homothetic_factor_of_second_ellipse": (c8_homothetic_factor_of_second_ellipse_value, {}, "1"),
    "camf.c9_bearing_angle_of_second_ellipse": (c9_bearing_angle_of_second_ellipse_value, {}, "deg"),
    "camf.d5_wave_height": ({}, _up_to(0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0), "m"),
    "camf.d6_temperature_range": ({}, _up_to(*range(-30, 36, 5), 45), "Cel"),
    "camf.d8_wind_speed": ({}, _up_to(1, 6, 12, 20, 31, 40, 51, 62, 75, 89, 103, 118, floor=0), "km/h"),
    "camf.d9_rainfall_amounts": ({}, _up_to(2.5, 7.5, 10, 20, 30, 50, 80), "mm/h"),
    "camf.d13_visibility": ({}, _up_to(20, 200, 500, 1000, 2000, 4000, 10000, 20000, 50000), "m"),
    "camf.d14_snow_depth": ({}, _up_to(*range(20, 601, 20), floor=0), "cm"),
    "camf.d26_number_of_cases_per_100000_inhabitants": (
        {},
        {
            **dict(enumerate(((0, 9), (10, 20), (21, 50), (51, 70), (71, 100), (101, 125), (126, 150),
                             (151, 175), (176, 200), (201, 250), (251, 300), (301, 350), (351, 400),
                             (401, 450), (451, 500), (501, 750)))),
            16: (751, 1000),
            17: (1000, None),
            18: (2000, None),
            19: (3000, None),
            20: (5000, None),
        },
        "1",
    ),
    "camf.d27_noise_range": ({}, _up_to(45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, floor=40), "dB"),
    "camf.d29_outage_estimated_duration": (
        {},
        _from(30, 45, 60, 90, 120, 180, 240, 300, 600, 1440, 2880, 10080, floor=0),
        "min",
    ),
}

#: a quantity measured in something the record gives elsewhere, rather than in a unit
RELATIVE_TO = {
    "camf.d4_vector_length_between_centre_of_main_ellipse_and_epicentre": "main_ellipse.semi_major_axis",
    "camf.c7_shift_of_second_ellipse_centre": "main_ellipse.semi_major_axis",
    "camf.c8_homothetic_factor_of_second_ellipse": "main_ellipse",  # both of its semi-axes
    "camf.c9_bearing_angle_of_second_ellipse": "main_ellipse.azimuth",  # turned from it
}


def quantity(table: Table, n: int, assumed: bool = False) -> dict[str, Any]:
    """A code that stands for a number or a range of numbers, in the unit of its table.

    A code that stands for no number has no value; one that says the number is unknown has a null one.
    """
    scalars, ranges, unit = PROFILES[table.name]
    status = table.status(n)
    result: dict[str, Any] = {"status": status}
    if status == "valid" and assumed:
        result["status"] = "assumed"
    if n in scalars:
        result.update({"value": scalars[n], "unit": unit})
    elif n in ranges:
        lower, upper = ranges[n]
        result.update({"range": {"lower": lower, "upper": upper}, "unit": unit})
    elif status != "valid":
        result["value"] = None
    if table.name in RELATIVE_TO and "unit" in result:
        result["relative_to"] = RELATIVE_TO[table.name]
    code_object = table.code(n)
    del code_object["status"]
    return {**result, **code_object}


def _time(dt: datetime | None, source: dict[str, int], precision: str = "minute") -> dict[str, Any]:
    """A time the message gives, and how precise it is.

    One whose fields are not a time is undefined.
    """
    if dt is None:
        return _no_time("undefined", source)
    return {"status": "valid", "value": utc(dt), "precision": precision, "source": source}


def _no_time(status: str, source: dict[str, int], labels: dict[str, str] | None = None) -> dict[str, Any]:
    """A time field that holds no time, with what the message gave in its place."""
    result: dict[str, Any] = {"status": status, "value": None}
    if labels:
        result["labels"] = labels
    result["source"] = source
    return result


def _day_hour_minute(raw: DayHourMinute) -> dict[str, int]:
    return {"day": raw["day"], "hour": raw["hour"], "minute": raw["minute"]}


def _arrival(report: Any, i: int, domestic: bool) -> dict[str, Any]:
    """An expected tsunami arrival: a time, or one of the words the tables give in place of one."""
    dt = report.expected_tsunami_arrival_times[i]
    raw = report.expected_tsunami_arrival_times_raw[i]
    source = _day_hour_minute(raw)
    arrived = (raw["hour"], raw["minute"]) == (31, 63)
    if dt is not None:
        return _time(dt, source)
    if domestic and (arrived or (raw["day"], raw["hour"], raw["minute"]) == (0, 30, 62)):
        ja, en = expected_tsunami_arrival_time_kind(raw, False)
        return _no_time("special", source, {"ja": ja, "en": en})
    if not domestic and arrived:  # arrived, or its time unknown
        return _no_time("special", source, {"en": report.expected_tsunami_arrival_time_types_en[i]})
    return _no_time("undefined", source)


POSITION_SOURCE = {
    "lat_ns": "latitude_hemisphere",
    "lat_d": "latitude_degrees",
    "lat_m": "latitude_minutes",
    "lat_s": "latitude_seconds",
    "lon_ew": "longitude_hemisphere",
    "lon_d": "longitude_degrees",
    "lon_m": "longitude_minutes",
    "lon_s": "longitude_seconds",
}


def _position(raw: Coordinates) -> dict[str, Any]:
    def degree(d: int, m: int, s: int, negative: int) -> float:
        return round((d + m / 60 + s / 3600) * (-1 if negative else 1), 9)

    source = {POSITION_SOURCE[key]: value for key, value in raw.items()}
    if not is_position(raw):
        return {"status": "undefined", "value": None, "source": source}
    latitude = degree(raw["lat_d"], raw["lat_m"], raw["lat_s"], raw["lat_ns"])
    longitude = degree(raw["lon_d"], raw["lon_m"], raw["lon_s"], raw["lon_ew"])
    return {"status": "valid", "value": {"latitude": latitude, "longitude": longitude}, "unit": "deg", "source": source}


def _version(value: int, valid: bool) -> dict[str, Any]:
    """The version the message says it is in: valid where it is one the specification gives."""
    return {"status": "valid" if valid else "undefined", "value": value}


def _dcr(table: str, n: int, assumed: bool = False) -> dict[str, Any]:
    t = TABLES["qzss.dcr." + table]
    return quantity(t, n, assumed) if t.name in PROFILES else t.code(n)


COMMON = [
    ("report_classification", "report_classification_no", "report_classification"),
    ("information_type", "information_type_no", "information_type"),
]
SINGLES = {
    "EarthquakeEarlyWarning": [
        ("depth", "depth_of_hypocenter_raw", "depth_of_hypocenter"),
        ("magnitude", "magnitude_raw", "eew_magnitude"),
        ("epicenter", "seismic_epicenter_raw", "epicenter_and_hypocenter"),
        ("intensity_lower", "seismic_intensity_lower_limit_raw", "seismic_intensity_lower_limit"),
        ("intensity_upper", "seismic_intensity_upper_limit_raw", "seismic_intensity_upper_limit"),
        (
            "long_period_ground_motion_lower",
            "long_period_ground_motion_lower_limit_raw",
            "long_period_ground_motion_lower_limit",
        ),
        (
            "long_period_ground_motion_upper",
            "long_period_ground_motion_upper_limit_raw",
            "long_period_ground_motion_upper_limit",
        ),
    ],
    "Hypocenter": [
        ("depth", "depth_of_hypocenter_raw", "depth_of_hypocenter"),
        ("magnitude", "magnitude_raw", "hypocenter_magnitude"),
        ("epicenter", "seismic_epicenter_raw", "epicenter_and_hypocenter"),
    ],
    "NankaiTroughEarthquake": [("information_serial", "information_serial_code_raw", "information_serial_code")],
    "Tsunami": [("warning", "tsunami_warning_code_raw", "tsunami_warning_code")],
    "NorthwestPacificTsunami": [("tsunamigenic_potential", "tsunamigenic_potential_raw", "tsunamigenic_potential")],
    "Volcano": [
        ("volcano", "volcano_name_raw", "volcano_name"),
        ("warning", "volcanic_warning_code_raw", "volcanic_warning_code"),
    ],
    "AshFall": [
        ("volcano", "volcano_name_raw", "volcano_name"),
        ("warning_type", "ash_fall_warning_type_raw", "ash_fall_warning_type"),
    ],
    "Weather": [("warning_state", "weather_warning_state_raw", "weather_warning_state")],
    "Typhoon": [
        (out, src + "_raw", table)
        for out, src, table in [
            ("number", "typhoon_number", "typhoon_number"),
            ("scale_category", "typhoon_scale_category", "typhoon_scale_category"),
            ("intensity_category", "typhoon_intensity_category", "typhoon_intensity_category"),
            ("central_pressure", "central_pressure", "typhoon_central_pressure"),
            ("maximum_wind_speed", "maximum_wind_speed", "typhoon_maximum_wind_speed"),
            ("maximum_gust_wind_speed", "maximum_gust_wind_speed", "typhoon_maximum_gust_wind_speed"),
            ("reference_time_type", "reference_time_type", "typhoon_reference_time_type"),
            ("elapsed_time", "elapsed_time_from_reference_time", "typhoon_elapsed_time_from_reference_time"),
        ]
    ],
}
LISTS = {
    "SeismicIntensity": (
        "observations",
        [("region", "prefectures_raw", "prefecture"), ("intensity", "seismic_intensities_raw", "seismic_intensity")],
    ),
    "Tsunami": (
        "forecasts",
        [
            ("region", "tsunami_forecast_regions_raw", "tsunami_forecast_region"),
            ("height", "tsunami_heights_raw", "tsunami_height"),
        ],
    ),
    "NorthwestPacificTsunami": (
        "forecasts",
        [
            ("region", "coastal_regions_raw", "coastal_region"),
            ("height", "tsunami_heights_raw", "northwest_pacific_tsunami_height"),
        ],
    ),
    "AshFall": (
        "forecasts",
        [
            ("region", "local_governments_raw", "local_government"),
            ("elapsed_time", "expected_ash_fall_times_raw", "expected_ash_fall_time"),
            ("warning", "ash_fall_warning_codes_raw", "ash_fall_warning_code"),
        ],
    ),
    "Weather": (
        "warnings",
        [
            ("region", "weather_forecast_regions_raw", "weather_forecast_region"),
            ("warning", "weather_related_disaster_sub_categories_raw", "weather_related_disaster_sub_category"),
        ],
    ),
    "Flood": (
        "warnings",
        [
            ("region", "flood_forecast_regions_raw", "flood_forecast_region"),
            ("warning", "flood_warning_levels_raw", "flood_warning_level"),
        ],
    ),
    "Marine": (
        "warnings",
        [
            ("region", "marine_forecast_regions_raw", "marine_forecast_region"),
            ("warning", "marine_warning_codes_raw", "marine_warning_code"),
        ],
    ),
}
TIMES = {  # the key in data, and the time the report holds
    "EarthquakeEarlyWarning": ("occurrence_time", "occurrence_time_of_earthquake"),
    "Hypocenter": ("occurrence_time", "occurrence_time_of_earthquake"),
    "SeismicIntensity": ("occurrence_time", "occurrence_time_of_earthquake"),
    "Volcano": ("activity_time", "activity_time"),
    "AshFall": ("activity_time", "activity_time"),
    "Typhoon": ("reference_time", "reference_time"),
}
DCR_TYPES = [
    "EarthquakeEarlyWarning",
    "Hypocenter",
    "SeismicIntensity",
    "NankaiTroughEarthquake",
    "Tsunami",
    "NorthwestPacificTsunami",
    "Volcano",
    "AshFall",
    "Weather",
    "Flood",
    "Typhoon",
    "Marine",
]
DCX_TYPES = ["NullMsg", "OutsideJapan", "LAlert", "JAlert", "MTInfo", "Unknown"]
TYPE_NAMES = dict(
    zip(
        DCR_TYPES + DCX_TYPES,
        [
            "qzss.dcr.earthquake_early_warning",
            "qzss.dcr.hypocenter",
            "qzss.dcr.seismic_intensity",
            "qzss.dcr.nankai_trough_earthquake",
            "qzss.dcr.tsunami",
            "qzss.dcr.northwest_pacific_tsunami",
            "qzss.dcr.volcano",
            "qzss.dcr.ash_fall",
            "qzss.dcr.weather",
            "qzss.dcr.flood",
            "qzss.dcr.typhoon",
            "qzss.dcr.marine",
            "qzss.dcx.null",
            "qzss.dcx.outside_japan",
            "qzss.dcx.l_alert",
            "qzss.dcx.j_alert",
            "qzss.dcx.mt_info",
            "qzss.dcx.unknown",
        ],
        strict=True,
    )
)

#: the precision of a volcano's activity time by its ambiguity Du; 6 and 7 leave no time
ACTIVITY_PRECISION = ["minute", "minute", "minute", "minute", "hour", "day"]


def dcr_model(name: str, report: Any) -> dict[str, Any]:
    at = report.report_time
    data: dict[str, Any] = {
        "version": _version(report.version, report.version == 1),
        "report_time": _time(at, {"month": at.month, "day": at.day, "hour": at.hour, "minute": at.minute}),
    }
    assumed = bool(getattr(report, "assumptive", False))
    for out, src, table in COMMON + SINGLES.get(name, []):
        data[out] = _dcr(table, getattr(report, src), assumed and out in ("depth", "magnitude"))
    if name in TIMES:
        out, src = TIMES[name]
        given = _day_hour_minute(getattr(report, src + "_raw"))
        du: int = report.ambiguity_of_activity_time_no if name == "Volcano" else 0
        if du < len(ACTIVITY_PRECISION):
            data[out] = _time(getattr(report, src), given, ACTIVITY_PRECISION[du])
        else:  # the message gives a time, and says its day, hour and minute are not valid
            data[out] = _no_time("special", given, TABLES["qzss.dcr.ambiguity_of_activity_time"].labels(du))
    if name in ("EarthquakeEarlyWarning", "Hypocenter", "Tsunami"):
        data["notifications"] = [
            _dcr("notification_on_disaster_prevention", n) for n in report.notifications_on_disaster_prevention_raw
        ]
    if name in LISTS:
        out, columns = LISTS[name]
        rows = list(zip(*(getattr(report, src) for _, src, _ in columns), strict=True))
        data[out] = [{key: _dcr(table, v) for (key, _, table), v in zip(columns, row, strict=True)} for row in rows]
        if name in ("Tsunami", "NorthwestPacificTsunami"):
            for i, item in enumerate(data[out]):
                item["arrival"] = _arrival(report, i, domestic=name == "Tsunami")
    for cls, source, table in [
        ("EarthquakeEarlyWarning", "eew_forecast_regions_raw", "eew_forecast_region"),
        ("Volcano", "local_governments_raw", "local_government"),
    ]:
        if name == cls:
            data["target_regions"] = [_dcr(table, n) for n in getattr(report, source)]
    if name in ("Hypocenter", "Typhoon"):
        data["position"] = _position(
            getattr(report, "coordinates_of_" + ("hypocenter" if name == "Hypocenter" else "typhoon") + "_raw")
        )
    if name == "Volcano":
        data["activity_time_ambiguity"] = _dcr("ambiguity_of_activity_time", report.ambiguity_of_activity_time_no)
    if name == "NankaiTroughEarthquake":
        data["page"] = {
            "number": report.page_number,
            "total": report.total_page,
            "content_hex": report.text_information.hex(),
        }
    return data


ELLIPSES = {
    "main": (
        "a12_ellipse_centre_latitude",
        "a13_ellipse_centre_longitude",
        "a14_ellipse_semi_major_axis",
        "a15_ellipse_semi_minor_axis",
        "a16_ellipse_azimuth",
    ),
    "refined": (
        "c1_refined_latitude_of_centre_of_main_ellipse",
        "c2_refined_longitude_of_centre_of_main_ellipse",
        "c3_refined_length_of_semi_major_axis",
        "c4_refined_length_of_semi_minor_axis",
        "a16_ellipse_azimuth",
    ),
    "additional": (
        "ex3_additional_ellipse_centre_latitude",
        "ex4_additional_ellipse_centre_longitude",
        "ex5_additional_ellipse_semi_major_axis",
        "ex6_additional_ellipse_semi_minor_axis",
        "ex7_additional_ellipse_azimuth",
    ),
}


def _ellipse(report: Any, which: str) -> dict[str, Any]:
    keys = ("centre_latitude", "centre_longitude", "semi_major_axis", "semi_minor_axis", "azimuth")
    fields = ELLIPSES[which]
    lat, lon, major, minor, angle = [getattr(report, n) for n in fields]
    return {
        "status": "valid",
        "value": {
            "centre": {"latitude_deg": lat, "longitude_deg": lon},
            "semi_major_axis_km": major,
            "semi_minor_axis_km": minor,
            "azimuth_deg": angle,
        },
        # the transmitted codes, so that the conversions above never have to be inverted
        "source": {key: getattr(report.camf, field.split("_", 1)[0]) for key, field in zip(keys, fields, strict=True)},
    }


XCODES = [
    ("message_type", "a1", "a1_message_type"),
    ("country", "a2", "a2_country_region_name"),
    ("severity", "a5", "a5_severity"),
    ("duration", "a8", "a8_hazard_duration"),
]

#: the version IS-QZSS-DCX-004 gives the messages of Japan; one from outside Japan is in its sender's
#: own versions, and one of a kind DCX does not define has none the specification gives
DCX_VERSION = {"LAlert": 1, "JAlert": 1, "MTInfo": 1}

SETTINGS = ["refined_ellipse", "hazard_centre", "second_ellipse", "hazard_details"]


def _camf(table: str, n: int) -> dict[str, Any]:
    t = TABLES["camf." + table]
    return quantity(t, n) if t.name in PROFILES else t.code(n)


def _target_regions(report: Any) -> list[dict[str, Any]] | None:
    c = report.camf
    area = TABLES["qzss.dcx.ex1_target_area_code"]
    regions = None
    if not report.ignore_ex1:
        regions = [] if c.ex1 == 0 else [area.code(c.ex1)]  # all 0: no target area
    if not report.ignore_ex8_to_ex9:
        if c.ex8 == 0:
            bits = TABLES["qzss.dcx.ex9_target_area_code_list"]
            regions = [bits.code(prefecture_code(bit)) for bit in range(EX9_PREFECTURE_BITS) if c.ex9 & 1 << bit + 17]
        else:
            regions = [area.code(n) for shift in (48, 32, 16, 0) if (n := (c.ex9 >> shift & 65535))]
    return regions


def _specific_settings(report: Any) -> dict[str, Any]:
    c = report.camf
    kind = SETTINGS[int(c.a17)]
    settings: dict[str, Any] = {"type": _camf("a17_type_of_specific_settings", c.a17)}
    if c.a17 == 0:
        settings[kind] = _ellipse(report, "refined")
    elif c.a17 == 1:
        settings[kind] = {
            "status": "valid",
            "value": {
                "latitude_deg": report.c5_latitude_of_centre_of_hazard,
                "longitude_deg": report.c6_longitude_of_centre_of_hazard,
            },
            "source": {"latitude": c.c5, "longitude": c.c6},  # offsets from the main ellipse centre
        }
    elif c.a17 == 2:
        settings[kind] = {
            "shift": _camf("c7_shift_of_second_ellipse_centre", c.c7),
            "scale_factor": _camf("c8_homothetic_factor_of_second_ellipse", c.c8),
            "bearing": _camf("c9_bearing_angle_of_second_ellipse", c.c9),
            "instruction": _camf("c10_instruction_library_for_second_ellipse", c.c10),
        }
    else:
        details: dict[str, Any] = {}
        for name in B4_NAMES:
            raw = getattr(c, name.split("_", 1)[0])
            if raw is not None:
                details[name.split("_", 1)[1]] = _camf(name, raw)
        settings[kind] = details
    return settings


def dcx_model(name: str, report: Any) -> dict[str, Any]:
    if name == "NullMsg":
        return {}
    c = report.camf
    data: dict[str, Any] = {
        "version": _version(
            report.dcx_version,
            name == "OutsideJapan" or report.dcx_version == DCX_VERSION.get(name),
        ),
        **{out: _camf(table, getattr(c, field)) for out, field, table in XCODES},
        "provider": provider(c.a2).code(c.a3),
        "hazard": {part: _camf("a4_hazard_" + part, c.a4) for part in ("type", "category", "definition")},
    }
    source = {"week": c.a6, "minute_of_week": c.a7}
    if c.a7 == 0:  # not used
        data["onset"] = _no_time("special", source, {"en": a7_hazard_onset_time_of_week_not_used_en})
    else:
        data["onset"] = _time(report.a6a7_hazard_onset_datetime, source)
    guidance: dict[str, Any] = {
        "library": _camf("a9_type_of_library", c.a9),
        "library_version": _camf("a10_library_version", c.a10),
    }
    if c.a9 == 0:
        library = a11_library(c.a9, c.a2, c.a10)
        guidance["content"] = {}
        parts: tuple[Literal["list_a", "list_b"], ...] = ("list_a", "list_b")
        for part in parts:
            raw = c.a11 >> 5 if part == "list_a" else c.a11 & 0x1f
            names = library.identifier if part == "list_a" else library.identifier_b
            guidance["content"][part] = {
                **instruction(c.a9, c.a2, c.a10, part=part).code(raw),
                "identifier": None if names is None else names.get(raw),
            }
        guidance["source"] = {"a11": c.a11}
    else:
        guidance["content"] = instruction(c.a9, c.a2, c.a10).code(c.a11)
    data["instruction"] = guidance
    if not report.ignore_a12_to_a16:
        data["main_ellipse"] = _ellipse(report, "main")
    regions = _target_regions(report)
    if regions is not None:
        data["target_regions"] = regions
    if not report.ignore_ex2_to_ex7:
        data["evacuation"] = {
            "direction": TABLES["qzss.dcx.ex2_evacuate_direction_type"].code(c.ex2),
            "ellipse": _ellipse(report, "additional"),
        }
    if report.a17_type_of_specific_settings is not None:
        data["specific_settings"] = _specific_settings(report)
    return data


LIFECYCLE_DCR = ["issue", "correction", "cancellation"]  # information type It
LIFECYCLE_DCX = [None, "issue", "update", "all_clear"]  # message type A1; 0 is a test


def series(name: str, report: Any) -> dict[str, Any]:
    """How the message stands among the others: what it does to its series, and what names the series."""
    result: dict[str, Any] = {}
    if name in DCR_TYPES:
        it = report.information_type_no
        result["lifecycle"] = LIFECYCLE_DCR[it] if it < len(LIFECYCLE_DCR) else None
        if name == "NankaiTroughEarthquake":
            result["key"] = ".".join(
                [
                    f"{report.report_time:%Y-%m-%dT%H:%MZ}",
                    str(report.report_classification_no),
                    str(it),
                    str(report.information_serial_code_raw),
                    str(report.total_page),
                ]
            )
        return result
    if name == "NullMsg":
        return result
    c = report.camf
    if c.a1 != 0:
        result["lifecycle"] = LIFECYCLE_DCX[c.a1]
    if name in ("LAlert", "MTInfo"):  # IS-QZSS-DCX-004 4.2.3.1
        result["key"] = f"{c.a2}.{c.a3}.{c.a4}.{c.ex1}"
    elif name == "JAlert":
        result["key"] = f"{c.a2}.{c.a3}.{c.a4}"
    return result


def message_id(name: str, report: Any) -> str:
    """The same for every copy of one message: its system and format, and the content no satellite changes."""
    raw: bytes = report.raw
    return ".".join(TYPE_NAMES[name].split(".")[:2]) + ":" + raw.hex()


def texts(report: Any) -> dict[str, str]:
    result: dict[str, str] = report.get_texts()
    return result


def copy_json(value: Any) -> JsonValue:
    """Detach mutable report values and reject values JSON cannot represent."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, list):
        items = cast(list[object], value)
        return [copy_json(v) for v in items]
    if isinstance(value, dict):
        result: dict[str, JsonValue] = {}
        mapping = cast(dict[object, object], value)
        for key, v in mapping.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be strings")
            result[key] = copy_json(v)
        return result
    raise TypeError(f"Cannot serialize {type(value).__name__} as JSON")


def is_test(name: str, report: Any) -> bool:
    """Whether the report is a training or test message: DCR report classification 7, CAMF A1 0."""
    if name in DCR_TYPES:
        return bool(report.report_classification_no == 7)
    if name == "NullMsg":  # no alert, and so no A1
        return False
    return bool(report.camf.a1 == 0)


def report_name(report: reports.Report) -> str:
    supported = {getattr(reports.dcr, n): n for n in DCR_TYPES}
    supported.update({getattr(reports.dcx, n): n for n in DCX_TYPES})
    for cls in type(report).__mro__:
        if cls in supported:
            return supported[cls]
    raise AzarashiArgumentTypeError(f"Unsupported report type: {type(report).__name__}")
