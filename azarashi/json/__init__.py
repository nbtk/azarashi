"""JSON v2 output, its machine-readable contract and the code tables its records name."""

import json
from importlib.resources import files

from .model import JsonValue as JsonValue
from .model import TYPE_NAMES, copy_json, dcr_model, dcx_model, is_test, message_id, report_name, series, texts
from .model import DCR_TYPES, utc_milliseconds
from .tables import code_tables as _code_tables
from ..reports import Report

SCHEMA = "schemas/report-v2.schema.json"


def record(report: Report) -> dict[str, JsonValue]:
    """The JSON v2 record of the report, a new dict at each call: what report.to_json_dict() returns."""
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


def ndjson(report: Report) -> str:
    """The JSON v2 record as one compact line with a trailing newline: what report.to_ndjson() returns."""
    return json.dumps(record(report), ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"


def json_schema() -> dict[str, JsonValue]:
    """Return the bundled JSON v2 schema, a new dict at each call."""
    result = copy_json(json.loads(files("azarashi.json").joinpath(SCHEMA).read_text(encoding="utf-8")))
    assert isinstance(result, dict)
    return result


def code_tables() -> dict[str, JsonValue]:
    """Return the code tables that the JSON v2 records name, a new dict at each call."""
    result = copy_json(_code_tables())
    assert isinstance(result, dict)
    return result
