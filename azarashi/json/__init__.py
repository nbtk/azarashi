"""JSON v1 output and its machine-readable contract."""

import json
from importlib.resources import files

from ._serialization import JsonValue as JsonValue
from ._serialization import TYPE_NAMES, copy_json, dcr_model, dcx_model, report_name, DCR_TYPES, utc
from .reports import Report


def to_json_dict(report: Report) -> dict[str, JsonValue]:
    """Return an independent JSON v1 record, including NMEA and the current str(report)."""
    name = report_name(report)
    data = dcr_model(name, report) if name in DCR_TYPES else dcx_model(name, report)
    record = copy_json(
        {
            "schema_version": 1,
            "type": TYPE_NAMES[name],
            "received_at": utc(report.timestamp),
            "satellite": None if report.satellite_prn is None else {"system": "qzss", "prn": report.satellite_prn},
            "nmea": report.nmea,
            "text": str(report),
            "data": data,
        }
    )
    assert isinstance(record, dict)
    return record


def to_ndjson(report: Report) -> str:
    """Return one compact JSON record with a trailing newline."""
    return json.dumps(to_json_dict(report), ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"


def json_schema() -> dict[str, JsonValue]:
    """Return an independent copy of the bundled JSON v1 schema."""
    resource = files("azarashi").joinpath("schemas/report-v1.schema.json")
    result = copy_json(json.loads(resource.read_text(encoding="utf-8")))
    assert isinstance(result, dict)
    return result
