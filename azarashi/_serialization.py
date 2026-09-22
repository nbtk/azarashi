"""Report JSON conversion. Field selection is explicit; arbitrary instance attributes are not exported."""

import importlib
import math
import re
from datetime import UTC, datetime
from typing import Any, TypeAlias, cast
from . import reports
from .definitions.camf import d_fields as B4_MODULE
from .definitions.qzss.dcx.a11_japanese_library import a11_japanese_library_ja, a11_japanese_library_en
from .definitions.camf.a11_international_library import a11_international_library, a11_international_library_code
from .definitions.qzss.dcx.a3_provider_identifier import a3_provider_identifier_map
from .definitions.qzss.dcx.ex9_target_area_code import EX9_PREFECTURE_BITS
from .definitions.qzss.dcx.ex9_target_area_code import ex9_target_area_code_ja, ex9_target_area_code_en
from .definitions.qzss.dcx.ex1_target_area_code import ex1_target_area_code_ja, ex1_target_area_code_en

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Naive datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def coded(scheme: str, value: int, ja: Any = None, en: Any = None) -> dict[str, Any]:
    known = any(value in table for table in (ja, en) if table is not None)
    labels = {
        lang: table[value]
        for lang, table in [("ja", ja), ("en", en)]
        if table is not None and value in table and isinstance(table[value], str) and table[value]
    }
    return {"scheme": scheme, "code": str(value), "recognized": known, "labels": labels}


def quantity(code: dict[str, Any], profile: str) -> dict[str, Any]:
    n = int(code["code"])
    if not code["recognized"]:
        return {"kind": "missing", "reason": "unrecognized_code", "code": code}
    scalar, bounds, missing, unit = PROFILES[profile]
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


def bound(value: float, inclusive: bool) -> dict[str, Any]:
    return {"value": value, "inclusive": inclusive}


PROFILES: dict[str, Any] = {
    "depth_of_hypocenter": ({i: i for i in range(501)}, {501: (bound(500, False), None)}, {511: "unknown"}, "km"),
    "eew_magnitude": ({i: i / 10 for i in range(1, 101)}, {101: (bound(10, False), None)}, {127: "unknown"}, None),
    "hypocenter_magnitude": (
        {i: i / 10 for i in range(1, 101)},
        {101: (bound(10, False), None), 126: (bound(8, False), None)},
        {127: "unknown"},
        None,
    ),
    "tsunami_height": (
        {},
        {
            1: (None, bound(0.2, False)),
            2: (bound(0.2, True), bound(1, True)),
            3: (bound(1, False), bound(3, True)),
            4: (bound(3, False), bound(5, True)),
            5: (bound(5, False), bound(10, True)),
            6: (bound(10, False), None),
        },
        {13: "no_information", 14: "unknown"},
        "m",
    ),
    "northwest_pacific_tsunami_height": ({}, {508: (bound(10, False), None)}, {511: "unknown"}, "m"),
    "typhoon_central_pressure": ({i: i for i in range(1101)}, {}, {}, "hPa"),
    "typhoon_maximum_wind_speed": ({i: i for i in range(15, 106)}, {}, {0: "unknown"}, "m/s"),
    "typhoon_maximum_gust_wind_speed": ({i: i for i in range(15, 106)}, {}, {0: "unknown"}, "m/s"),
    "expected_ash_fall_time": ({i: i for i in range(1, 7)}, {}, {}, "h"),
    "typhoon_elapsed_time_from_reference_time": ({i: i for i in range(128)}, {}, {}, "h"),
}


def time_value(
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


def position(raw: dict[str, int]) -> dict[str, Any]:
    valid = (
        raw["lat_ns"] in (0, 1)
        and raw["lon_ew"] in (0, 1)
        and (0 <= raw["lat_d"] < 90)
        and (0 <= raw["lon_d"] < 180)
        and all(0 <= raw[k] < 60 for k in ["lat_m", "lat_s", "lon_m", "lon_s"])
    )

    def degree(p: str) -> float:
        return round(
            (raw[p + "_d"] + raw[p + "_m"] / 60 + raw[p + "_s"] / 3600)
            * (-1 if raw[p + ("_ns" if p == "lat" else "_ew")] else 1),
            9,
        )

    return {
        "status": "valid" if valid else "unrecognized_code",
        "latitude_deg": degree("lat") if valid else None,
        "longitude_deg": degree("lon") if valid else None,
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
        ("long_period_lower", "long_period_ground_motion_lower_limit_raw", "long_period_ground_motion_lower_limit"),
        ("long_period_upper", "long_period_ground_motion_upper_limit_raw", "long_period_ground_motion_upper_limit"),
    ],
    "Hypocenter": [
        ("depth", "depth_of_hypocenter_raw", "depth_of_hypocenter"),
        ("magnitude", "magnitude_raw", "hypocenter_magnitude"),
        ("epicenter", "seismic_epicenter_raw", "epicenter_and_hypocenter"),
    ],
    "NankaiTroughEarthquake": [("information_serial", "information_serial_code_raw", "information_serial_code")],
    "Tsunami": [("warning", "tsunami_warning_code_raw", "tsunami_warning_code")],
    "NorthwestPacificTsunami": [("potential", "tsunamigenic_potential_raw", "tsunamigenic_potential")],
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
            ("scale", "typhoon_scale_category", "typhoon_scale_category"),
            ("intensity", "typhoon_intensity_category", "typhoon_intensity_category"),
            ("pressure", "central_pressure", "typhoon_central_pressure"),
            ("wind_speed", "maximum_wind_speed", "typhoon_maximum_wind_speed"),
            ("gust_speed", "maximum_gust_wind_speed", "typhoon_maximum_gust_wind_speed"),
            ("reference_type", "reference_time_type", "typhoon_reference_time_type"),
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
TIMES = {
    "EarthquakeEarlyWarning": "occurrence_time_of_earthquake",
    "Hypocenter": "occurrence_time_of_earthquake",
    "SeismicIntensity": "occurrence_time_of_earthquake",
    "Volcano": "activity_time",
    "AshFall": "activity_time",
    "Typhoon": "reference_time",
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


def dcr_code(table: str, value: int) -> dict[str, Any]:
    tables = importlib.import_module(f".definitions.qzss.dcr.{table}", __package__)
    ja = getattr(tables, table, None)
    en = getattr(tables, table + "_en", None)
    return coded("qzss.dcr." + table, value, ja, en)


def dcr_value(table: str, value: int) -> dict[str, Any]:
    c = dcr_code(table, value)
    return quantity(c, table) if table in PROFILES else c


def dcr_model(name: str, report: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "version": report.version,
        "report_time": time_value(report.report_time, basis="received_at"),
    }
    for out, src, table in COMMON + SINGLES.get(name, []):
        data[out] = dcr_value(table, getattr(report, src))
    if name in TIMES:
        src = TIMES[name]
        data[src] = time_value(getattr(report, src), getattr(report, src + "_raw"))
    if name in ("EarthquakeEarlyWarning", "Hypocenter", "Tsunami"):
        data["notifications"] = [
            dcr_value("notification_on_disaster_prevention", n) for n in report.notifications_on_disaster_prevention_raw
        ]
    if name in LISTS:
        out, columns = LISTS[name]
        arrival = name in ("Tsunami", "NorthwestPacificTsunami")
        rows = list(zip(*(getattr(report, src) for _, src, _ in columns), strict=True))
        data[out] = [
            {key: dcr_value(table, v) for (key, _, table), v in zip(columns, row, strict=True)} for row in rows
        ]
        if arrival:
            for item, dt, raw in zip(
                data[out], report.expected_tsunami_arrival_times, report.expected_tsunami_arrival_times_raw, strict=True
            ):
                item["arrival"] = time_value(dt, raw, arrival="domestic" if name == "Tsunami" else "northwest")
    for cls, source, table in [
        ("EarthquakeEarlyWarning", "eew_forecast_regions_raw", "eew_forecast_region"),
        ("Volcano", "local_governments_raw", "local_government"),
    ]:
        if name == cls:
            data["regions"] = [dcr_value(table, n) for n in getattr(report, source)]
    if name in ("Hypocenter", "Typhoon"):
        data["position"] = position(
            getattr(report, "coordinates_of_" + ("hypocenter" if name == "Hypocenter" else "typhoon") + "_raw")
        )
    if name == "EarthquakeEarlyWarning":
        data["assumptive"] = report.assumptive
    if name == "Volcano":
        data["activity_time_ambiguity_code"] = report.ambiguity_of_activity_time_no
    if name == "NankaiTroughEarthquake":
        data["page"] = {
            "number": report.page_number,
            "total": report.total_page,
            "content_hex": report.text_information.hex(),
        }
    optional = []
    if name == "EarthquakeEarlyWarning":
        optional = ["long_period_lower", "long_period_upper"]
        for key in optional:
            if key in data and data[key]["code"] == "0":
                del data[key]
    return data


def ellipse(report: Any, prefix: str) -> dict[str, Any]:
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


def xcode(table: str, n: int) -> dict[str, Any]:
    """A table CAMF defines, under the scheme of the service that carried the message."""
    module = "a4_hazard_category_and_type" if table == "a4_hazard_type" else table
    definitions = importlib.import_module(f".definitions.camf.{module}", __package__)
    return coded("camf." + table, n, en=getattr(definitions, table))


def region_code(n: int) -> dict[str, Any]:
    return coded("qzss.dcx.area_code", n, ex1_target_area_code_ja, ex1_target_area_code_en)


def prefecture_bit(bit: int) -> dict[str, Any]:
    """The prefecture EX9 sets at this bit, keyed by the bit position rather than the mask."""
    def named(table: Any) -> dict[int, Any]:
        mask = 1 << bit
        return {bit: table[mask]} if mask in table else {}  # an unnamed bit keeps its position only

    return coded("qzss.dcx.prefecture_bit", bit, named(ex9_target_area_code_ja), named(ex9_target_area_code_en))


def instruction_scheme(camf: Any) -> str:
    """The library A11 indexes: CAMF's own for A9=0, and a country's own otherwise."""
    if camf.a9 == 0:  # the international library is the same table for every country
        return f"camf.instruction.library_{camf.a9}.version_{camf.a10}"
    return f"qzss.dcx.instruction.country_{camf.a2}.library_{camf.a9}.version_{camf.a10}"


def dcx_model(name: str, report: Any) -> dict[str, Any]:
    if name == "NullMsg":
        return {}
    c = report.camf
    data = {"version": report.dcx_version, **{out: xcode(table, getattr(c, field)) for out, field, table in XCODES}}
    provider_table: Any = a3_provider_identifier_map.get(c.a2)
    data["provider"] = coded(f"qzss.dcx.provider.country_{c.a2}", c.a3, en=provider_table)
    data["hazard"] = {
        "code": xcode("a4_hazard_type", c.a4),
        "category": report.a4_hazard_category,
        "definition": report.a4_hazard_definition,
    }
    data["onset"] = time_value(
        report.a6a7_hazard_onset_datetime, {"week": c.a6, "minute_of_week": c.a7}, basis="received_at"
    )
    ja, en, identifier = (None, None, None)
    if c.a10 == 0:
        if c.a9 == 0:
            en = a11_international_library
            identifier = a11_international_library_code.get(c.a11)
        elif c.a2 == 111:
            ja, en = (a11_japanese_library_ja, a11_japanese_library_en)
    data["instruction"] = {
        "country_code": str(c.a2),
        "library": xcode("a9_type_of_library", c.a9),
        "version": xcode("a10_library_version", c.a10),
        "content": coded(instruction_scheme(c), c.a11, ja, en),
        "identifier": identifier,
    }
    if not report.ignore_a12_to_a16:
        data["main_ellipse"] = ellipse(report, "main")
    if not report.ignore_ex1:
        data["target_regions"] = [region_code(c.ex1)]
    if not report.ignore_ex8_to_ex9:
        if c.ex8 == 0:
            data["target_regions"] = [prefecture_bit(bit) for bit in range(EX9_PREFECTURE_BITS) if c.ex9 & 1 << bit + 17]
        else:
            data["target_regions"] = [region_code(n) for shift in (48, 32, 16, 0) if (n := (c.ex9 >> shift & 65535))]
    if not report.ignore_ex2_to_ex7:
        data["evacuation"] = {"direction": "head_to" if c.ex2 else "leave", "ellipse": ellipse(report, "additional")}
    if report.a17_type_of_specific_settings is not None:
        kind = ["refined_ellipse", "hazard_centre", "second_ellipse", "hazard_details"][int(c.a17)]
        if c.a17 == 0:
            value = ellipse(report, "refined")
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
                "instruction": xcode("c10_instruction_library_for_second_ellipse", c.c10),
                "source": {"shift": c.c7, "scale_factor": c.c8, "bearing": c.c9},
            }
        else:
            value = {}
            for field, table in B4_TABLES.items():
                raw = getattr(c, field.split("_", 1)[0])
                if raw is None:
                    continue
                item = coded("camf." + field, raw, en=table)
                if field.startswith(("d3_", "d4_")):
                    item = {
                        "code": item,
                        "value": getattr(report, field),
                        "unit": "deg" if field.startswith("d3_") else "semi_major_axis",
                    }
                value[field.split("_", 1)[1]] = item
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


def report_name(report: reports.Report) -> str:
    supported = {getattr(reports.dcr, n): n for n in DCR_TYPES}
    supported.update({getattr(reports.dcx, n): n for n in DCX_TYPES})
    for cls in type(report).__mro__:
        if cls in supported:
            return supported[cls]
    raise TypeError(f"Unsupported report type: {type(report).__name__}")
