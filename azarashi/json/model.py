"""Report JSON conversion. Field selection is explicit; arbitrary instance attributes are not exported."""

import importlib
import math
import re
from itertools import pairwise
from datetime import UTC, datetime
from typing import Any, TypeAlias, cast
from .. import reports
from ..definitions.qzss.dcr.latitude_and_longitude import is_position
from ..reports.base import Coordinates
from ..exceptions import AzarashiArgumentTypeError
from ..definitions.camf import d_fields as B4_MODULE
from ..definitions.camf.a11_library import a11_library
from ..definitions.camf.a3_provider_identifier import a3_provider_identifier_map
from ..definitions.qzss.dcx.ex9_target_area_code import EX9_PREFECTURE_BITS
from ..definitions.qzss.dcx.ex9_target_area_code import ex9_target_area_code_ja, ex9_target_area_code_en
from ..definitions.qzss.dcx.ex1_target_area_code import ex1_target_area_code_ja, ex1_target_area_code_en

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Naive datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _coded(scheme: str, value: int, ja: Any = None, en: Any = None) -> dict[str, Any]:
    known = any(value in table for table in (ja, en) if table is not None)
    labels = {
        lang: table[value]
        for lang, table in [("ja", ja), ("en", en)]
        if table is not None and value in table and isinstance(table[value], str) and table[value]
    }
    return {"scheme": scheme, "code": str(value), "recognized": known, "labels": labels}


def _quantity(code: dict[str, Any], profile: str) -> dict[str, Any]:
    n = int(code["code"])
    if not code["recognized"]:
        return {"kind": "missing", "reason": "unrecognized_code", "code": code}
    scalar, bounds, missing, unit = PROFILES[profile] if profile in PROFILES else CAMF_PROFILES[profile]
    if n in scalar:
        return {"kind": "scalar", "value": scalar[n], "unit": unit, "code": code}
    if n in bounds:
        lower, upper = bounds[n]
        result = {"kind": "bounds", "lower": lower, "upper": upper, "unit": unit, "code": code}
        if profile == "hypocenter_magnitude" and n == 126:
            result["qualifier"] = "unknown_value"
        return result
    if n in missing:
        return {"kind": "missing", "reason": missing[n], "code": code}
    return {"kind": "category", "code": code}


def _bound(value: float, inclusive: bool) -> dict[str, Any]:
    return {"value": value, "inclusive": inclusive}


PROFILES: dict[str, Any] = {
    "depth_of_hypocenter": ({i: i for i in range(501)}, {501: (_bound(500, False), None)}, {511: "unknown"}, "km"),
    "eew_magnitude": ({i: i / 10 for i in range(1, 101)}, {101: (_bound(10, False), None)}, {127: "unknown"}, None),
    "hypocenter_magnitude": (
        {i: i / 10 for i in range(1, 101)},
        {101: (_bound(10, False), None), 126: (_bound(8, False), None)},
        {127: "unknown"},
        None,
    ),
    "tsunami_height": (
        {},
        {
            1: (None, _bound(0.2, False)),
            2: (_bound(0.2, True), _bound(1, True)),
            3: (_bound(1, False), _bound(3, True)),
            4: (_bound(3, False), _bound(5, True)),
            5: (_bound(5, False), _bound(10, True)),
            6: (_bound(10, False), None),
        },
        {13: "no_information", 14: "unknown"},
        "m",
    ),
    "northwest_pacific_tsunami_height": ({}, {508: (_bound(10, False), None)}, {511: "unknown"}, "m"),
    "typhoon_central_pressure": ({i: i for i in range(1101)}, {}, {}, "hPa"),
    "typhoon_maximum_wind_speed": ({i: i for i in range(15, 106)}, {}, {0: "unknown"}, "m/s"),
    "typhoon_maximum_gust_wind_speed": ({i: i for i in range(15, 106)}, {}, {0: "unknown"}, "m/s"),
    "expected_ash_fall_time": ({i: i for i in range(1, 7)}, {}, {}, "h"),
    "typhoon_elapsed_time_from_reference_time": ({i: i for i in range(128)}, {}, {}, "h"),
}


Range: TypeAlias = tuple[dict[str, Any] | None, dict[str, Any] | None]  # (lower, upper), None where it is open


def _up_to(*edges: float, floor: float | None = None) -> dict[int, Range]:
    """Contiguous ranges that leave out their lower edge and hold their upper one: (a, b].

    The first range reaches down without limit unless a floor is given, which it then leaves out;
    the last reaches up without limit.
    """
    rows: list[Range] = [(None if floor is None else _bound(floor, False), _bound(edges[0], True))]
    rows += [(_bound(a, False), _bound(b, True)) for a, b in pairwise(edges)]
    rows.append((_bound(edges[-1], False), None))
    return dict(enumerate(rows))


def _from(*edges: float, floor: float | None = None) -> dict[int, Range]:
    """Contiguous ranges that hold their lower edge and leave out their upper one: [a, b).

    A floor adds a first range above it, leaving both the floor and the first edge out; the last
    range reaches up without limit.
    """
    rows: list[Range] = [] if floor is None else [(_bound(floor, False), _bound(edges[0], False))]
    rows += [(_bound(a, True), _bound(b, False)) for a, b in pairwise(edges)]
    rows.append((_bound(edges[-1], True), None))
    return dict(enumerate(rows))


D26_FROM = (0, 10, 21, 51, 71, 101, 126, 151, 176, 201, 251, 301, 351, 401, 451, 501, 751)

#: CAMF Issue 1.2, 18.4.35: the B4 details that are numbers or numeric ranges. The edges are the
#: numbers the tables print. Where a table writes both sides of an edge with <, the edge goes with
#: the lower range, as the tables that do say where it goes mostly have it.
CAMF_PROFILES: dict[str, Any] = {
    "d1_magnitude_on_richter_scale": ({}, _from(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0), {}, None),
    "d3_azimuth_from_centre_of_main_ellipse_to_epicentre": ({i: i * 22.5 for i in range(16)}, {}, {}, "deg"),
    "d4_vector_length_between_centre_of_main_ellipse_and_epicentre": (
        dict(enumerate([0.25, 0.5, 0.75, 1, 2, 3, 5, 10, 20, 30, 40, 50, 70, 100, 150, 200])),
        {},
        {},
        "semi_major_axis",
    ),
    "d5_wave_height": ({}, _up_to(0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0), {}, "m"),
    "d6_temperature_range": ({}, _up_to(*range(-30, 36, 5), 45), {}, "degC"),
    "d8_wind_speed": ({}, _up_to(1, 6, 12, 20, 31, 40, 51, 62, 75, 89, 103, 118, floor=0), {}, "km/h"),
    "d9_rainfall_amounts": ({}, _up_to(2.5, 7.5, 10, 20, 30, 50, 80), {}, "mm/h"),
    "d13_visibility": ({}, _up_to(20, 200, 500, 1000, 2000, 4000, 10000, 20000, 50000), {}, "m"),
    "d14_snow_depth": ({}, _up_to(*range(20, 601, 20), floor=0), {}, "cm"),
    "d26_number_of_cases_per_100000_inhabitants": (
        {},
        {
            **{i: (_bound(a, True), _bound(b, False)) for i, (a, b) in enumerate(pairwise(D26_FROM))},
            16: (_bound(751, True), _bound(1000, True)),
            17: (_bound(1000, False), _bound(2000, True)),
            18: (_bound(2000, False), _bound(3000, True)),
            19: (_bound(3000, False), _bound(5000, True)),
            20: (_bound(5000, False), None),
        },
        {},
        None,
    ),
    "d27_noise_range": ({}, _up_to(45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, floor=40), {}, "dB"),
    "d29_outage_estimated_duration": (
        {},
        _from(30, 45, 60, 90, 120, 180, 240, 300, 600, 1440, 2880, 10080, floor=0),
        {},
        "min",
    ),
}


def _time_value(
    dt: datetime | None, raw: dict[str, int] | None = None, basis: str = "report_time", arrival: str | None = None
) -> dict[str, Any]:
    if dt is not None:
        return {"status": "time", "value": utc(dt), "basis": basis}
    status = "unrecognized_code"
    if arrival and raw is not None and (raw["hour"] == 31) and (raw["minute"] == 63):
        status = "arrived_or_unknown" if arrival == "northwest" else "arrival_estimated"
    elif arrival == "domestic" and raw == {"day": 0, "hour": 30, "minute": 62}:
        status = "no_information"
    elif raw and raw.get("minute_of_week") == 0:
        status = "not_used"
    result: dict[str, Any] = {"status": status, "value": None, "basis": None}
    if status == "unrecognized_code":
        result["source"] = raw
    return result


def _position(raw: Coordinates) -> dict[str, Any]:
    valid = is_position(raw)

    def degree(d: int, m: int, s: int, negative: int) -> float:
        return round((d + m / 60 + s / 3600) * (-1 if negative else 1), 9)

    return {
        "status": "valid" if valid else "unrecognized_code",
        "latitude_deg": degree(raw["lat_d"], raw["lat_m"], raw["lat_s"], raw["lat_ns"]) if valid else None,
        "longitude_deg": degree(raw["lon_d"], raw["lon_m"], raw["lon_s"], raw["lon_ew"]) if valid else None,
        "source": raw,
    }


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
            ("level", "flood_warning_levels_raw", "flood_warning_level"),
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


def _dcr_code(table: str, value: int) -> dict[str, Any]:
    tables = importlib.import_module(f"..definitions.qzss.dcr.{table}", __package__)
    ja = getattr(tables, table, None)
    en = getattr(tables, table + "_en", None)
    return _coded("qzss.dcr." + table, value, ja, en)


def _dcr_value(table: str, value: int) -> dict[str, Any]:
    c = _dcr_code(table, value)
    return _quantity(c, table) if table in PROFILES else c


def dcr_model(name: str, report: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "version": report.version,
        "report_time": _time_value(report.report_time, basis="received_at"),
    }
    for out, src, table in COMMON + SINGLES.get(name, []):
        data[out] = _dcr_value(table, getattr(report, src))
    if name in TIMES:
        out, src = TIMES[name]
        data[out] = _time_value(getattr(report, src), getattr(report, src + "_raw"))
    if name in ("EarthquakeEarlyWarning", "Hypocenter", "Tsunami"):
        data["notifications"] = [
            _dcr_value("notification_on_disaster_prevention", n) for n in report.notifications_on_disaster_prevention_raw
        ]
    if name in LISTS:
        out, columns = LISTS[name]
        arrival = name in ("Tsunami", "NorthwestPacificTsunami")
        rows = list(zip(*(getattr(report, src) for _, src, _ in columns), strict=True))
        data[out] = [
            {key: _dcr_value(table, v) for (key, _, table), v in zip(columns, row, strict=True)} for row in rows
        ]
        if arrival:
            for item, dt, raw in zip(
                data[out], report.expected_tsunami_arrival_times, report.expected_tsunami_arrival_times_raw, strict=True
            ):
                item["arrival"] = _time_value(dt, raw, arrival="domestic" if name == "Tsunami" else "northwest")
    for cls, source, table in [
        ("EarthquakeEarlyWarning", "eew_forecast_regions_raw", "eew_forecast_region"),
        ("Volcano", "local_governments_raw", "local_government"),
    ]:
        if name == cls:
            data["target_regions"] = [_dcr_value(table, n) for n in getattr(report, source)]
    if name in ("Hypocenter", "Typhoon"):
        data["position"] = _position(
            getattr(report, "coordinates_of_" + ("hypocenter" if name == "Hypocenter" else "typhoon") + "_raw")
        )
    if name == "EarthquakeEarlyWarning":
        data["assumptive"] = report.assumptive
    if name == "Volcano":
        data["activity_time_ambiguity"] = _dcr_code("ambiguity_of_activity_time", report.ambiguity_of_activity_time_no)
    if name == "NankaiTroughEarthquake":
        data["page"] = {
            "number": report.page_number,
            "total": report.total_page,
            "content_hex": report.text_information.hex(),
        }
    optional = []
    if name == "EarthquakeEarlyWarning":
        optional = ["long_period_ground_motion_lower", "long_period_ground_motion_upper"]
        for key in optional:
            if key in data and data[key]["code"] == "0":
                del data[key]
    return data


def _ellipse(report: Any, prefix: str) -> dict[str, Any]:
    names = {
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
    keys = ("centre_latitude", "centre_longitude", "semi_major_axis", "semi_minor_axis", "azimuth")
    fields = names[prefix]
    lat, lon, major, minor, angle = [getattr(report, n) for n in fields]
    return {
        "centre": {"latitude_deg": lat, "longitude_deg": lon},
        "semi_major_axis_km": major,
        "semi_minor_axis_km": minor,
        "azimuth_deg": angle,
        # the transmitted codes, so that the conversions above never have to be inverted
        "source": {key: getattr(report.camf, field.split("_", 1)[0]) for key, field in zip(keys, fields, strict=True)},
    }


XCODES = [
    ("message_type", "a1", "a1_message_type"),
    ("country", "a2", "a2_country_region_name"),
    ("severity", "a5", "a5_severity"),
    ("duration", "a8", "a8_hazard_duration"),
]

B4_TABLES: dict[str, Any] = {k: v for k, v in vars(B4_MODULE).items() if re.match("d\\d+_", k)}


def _xcode(table: str, n: int) -> dict[str, Any]:
    """A table CAMF defines, under the camf. scheme of that table."""
    module = "a4_hazard_category_and_type" if table.startswith("a4_") else table
    definitions = importlib.import_module(f"..definitions.camf.{module}", __package__)
    return _coded("camf." + table, n, en=getattr(definitions, table))


def _region_code(n: int) -> dict[str, Any]:
    return _coded("qzss.dcx.area_code", n, ex1_target_area_code_ja, ex1_target_area_code_en)


def _prefecture_bit(bit: int) -> dict[str, Any]:
    """The prefecture EX9 sets at this bit, keyed by the bit position rather than the mask."""
    def named(table: Any) -> dict[int, Any]:
        mask = 1 << bit
        return {bit: table[mask]} if mask in table else {}  # an unnamed bit keeps its position only

    return _coded("qzss.dcx.prefecture_bit", bit, named(ex9_target_area_code_ja), named(ex9_target_area_code_en))


def _instruction_scheme(camf: Any) -> str:
    """The library A11 indexes: the international one for A9=0, the national one of A2 otherwise."""
    if camf.a9 == 0:  # the international library is the same table for every country
        return f"camf.instruction.library_{camf.a9}.version_{camf.a10}"
    return f"camf.instruction.country_{camf.a2}.library_{camf.a9}.version_{camf.a10}"


def dcx_model(name: str, report: Any) -> dict[str, Any]:
    if name == "NullMsg":
        return {}
    c = report.camf
    data = {"version": report.dcx_version, **{out: _xcode(table, getattr(c, field)) for out, field, table in XCODES}}
    provider_table: Any = a3_provider_identifier_map.get(c.a2)
    data["provider"] = _coded(f"camf.provider.country_{c.a2}", c.a3, en=provider_table)
    data["hazard"] = {part: _xcode("a4_hazard_" + part, c.a4) for part in ("type", "category", "definition")}
    data["onset"] = _time_value(
        report.a6a7_hazard_onset_datetime, {"week": c.a6, "minute_of_week": c.a7}, basis="received_at"
    )
    library = a11_library(c.a9, c.a2, c.a10)
    identifier = None if library.identifier is None else library.identifier.get(c.a11)
    data["instruction"] = {
        "library": _xcode("a9_type_of_library", c.a9),
        "version": _xcode("a10_library_version", c.a10),
        "content": _coded(_instruction_scheme(c), c.a11, library.ja, library.en),
        "identifier": identifier,
    }
    if not report.ignore_a12_to_a16:
        data["main_ellipse"] = _ellipse(report, "main")
    if not report.ignore_ex1:
        data["target_regions"] = [_region_code(c.ex1)]
    if not report.ignore_ex8_to_ex9:
        if c.ex8 == 0:
            data["target_regions"] = [_prefecture_bit(bit) for bit in range(EX9_PREFECTURE_BITS) if c.ex9 & 1 << bit + 17]
        else:
            data["target_regions"] = [_region_code(n) for shift in (48, 32, 16, 0) if (n := (c.ex9 >> shift & 65535))]
    if not report.ignore_ex2_to_ex7:
        data["evacuation"] = {"direction": "head_to" if c.ex2 else "leave", "ellipse": _ellipse(report, "additional")}
    if report.a17_type_of_specific_settings is not None:
        kind = ["refined_ellipse", "hazard_centre", "second_ellipse", "hazard_details"][int(c.a17)]
        if c.a17 == 0:
            value = _ellipse(report, "refined")
        elif c.a17 == 1:
            value = {
                "latitude_deg": report.c5_latitude_of_centre_of_hazard,
                "longitude_deg": report.c6_longitude_of_centre_of_hazard,
                "source": {"latitude": c.c5, "longitude": c.c6},  # offsets from the main ellipse centre
            }
        elif c.a17 == 2:
            value = {
                "scale_factor": report.c8_homothetic_factor_of_second_ellipse,
                "bearing_deg": report.c9_bearing_angle_of_second_ellipse,
                "instruction": _xcode("c10_instruction_library_for_second_ellipse", c.c10),
                "source": {"shift": c.c7, "scale_factor": c.c8, "bearing": c.c9},
            }
        else:
            value = {}
            for field, table in B4_TABLES.items():
                raw = getattr(c, field.split("_", 1)[0])
                if raw is None:
                    continue
                item = _coded("camf." + field, raw, en=table)
                value[field.split("_", 1)[1]] = _quantity(item, field) if field in CAMF_PROFILES else item
        data["specific_settings"] = {"kind": kind, kind: value}
    return data


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
