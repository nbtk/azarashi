"""JSON v2 output, its machine-readable contract and the code tables its records name."""

import json
from importlib.resources import files

from .model import JsonValue as JsonValue
from .model import TYPE_NAMES, copy_json, dcr_model, dcx_model, is_test, message_id, report_name, series, texts
from .model import DCR_TYPES, utc_milliseconds
from .tables import code_tables as _code_tables
from ..reports import Report

SCHEMA = "schemas/report-v2.schema.json"


def to_json_dict(report: Report) -> dict[str, JsonValue]:
    """Return an independent JSON v2 record of the report."""
    name = report_name(report)
    data = dcr_model(name, report) if name in DCR_TYPES else dcx_model(name, report)
    record: dict[str, object] = {
        "schema_version": 2,
        "type": TYPE_NAMES[name],
        "is_test": is_test(name, report),
        "message_id": message_id(name, report),
    }
    if links := series(name, report):
        record["series"] = links
    record["reception"] = {
        "at": utc_milliseconds(report.timestamp),
        "satellite": None if report.satellite_prn is None else {"system": "qzss", "prn": report.satellite_prn},
        "nmea": report.nmea,
    }
    record["texts"] = texts(report)
    record["data"] = data
    result = copy_json(record)
    assert isinstance(result, dict)
    return result


def to_ndjson(report: Report) -> str:
    """Return one compact JSON record with a trailing newline."""
    return json.dumps(to_json_dict(report), ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"


def json_schema() -> dict[str, JsonValue]:
    """Return an independent copy of the bundled JSON v2 schema."""
    result = copy_json(json.loads(files("azarashi.json").joinpath(SCHEMA).read_text(encoding="utf-8")))
    assert isinstance(result, dict)
    return result


def code_tables() -> dict[str, JsonValue]:
    """Return the code tables that the JSON v2 records name, made anew from azarashi's own tables."""
    result = copy_json(_code_tables())
    assert isinstance(result, dict)
    return result
