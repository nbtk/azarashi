"""Regenerate the schema, the code tables and deterministic examples: PYTHONPATH=.:tests python -m examples.generate."""
from azarashi import decode
import json
from pathlib import Path
from azarashi import json_schema, to_json_dict
from azarashi.json.model import TYPE_NAMES
from test_declared_types import REPORTS, RECEIVED
from test_dcx_fields import dcx, JAPAN
from test_jma_reports import HYPOCENTER, TSUNAMI
from qzqsm import jma


def fixtures():
    selected = [next(r for r in REPORTS if type(r).__name__ == name) for name in TYPE_NAMES]
    # Additional settings and B4 hazards, not hundreds of nearly identical log messages.
    seen = set()
    for report in REPORTS:
        if not hasattr(report, 'camf') or not hasattr(report, 'a17_type_of_specific_settings'):
            continue
        key = report.camf.a17, report.camf.a4 if report.camf.a17 == 3 else None
        if key not in seen:
            seen.add(key)
            selected.append(report)
    sentences = [jma(2, HYPOCENTER + [(96, 9, n)]) for n in (10, 501, 511, 502)]
    sentences += [jma(5, TSUNAMI + [(84, 1, 0), (85, 5, hour), (90, 6, minute)])
                  for hour, minute in [(31, 63), (30, 62), (25, 0)]]
    sentences.append(dcx(**JAPAN, a3=1, a14=1))  # an L-Alert with an ellipse, as the README shows
    sentences += [dcx(**JAPAN, a3=2, ex8=0, ex9=((1 << 12) | (1 << 13)) << 17),
                  dcx(**JAPAN, a3=2, ex8=1, ex9=(1100 << 48) | (1101 << 32)),
                  dcx(**JAPAN, a3=2, ex8=1, ex9=65535 << 48)]
    selected += [decode(s, 'nmea', timestamp=RECEIVED) for s in sentences]
    selected.append(decode(selected[0].message.hex()[:-1], 'hex', timestamp=RECEIVED))
    return selected


def code_tables_text(tables):
    """The code tables as docs/json gives them: one code to a line, so that a change shows as the lines it changes."""
    def line(value):
        return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(', ', ': '))

    out = ['{', f'  "schema_version": {line(tables["schema_version"])},', '  "tables": {']
    names = list(tables['tables'])
    for i, name in enumerate(names):
        table = tables['tables'][name]
        out += [f'    {line(name)}: {{', f'      "source": {line(table["source"])},', '      "codes": {']
        codes = list(table['codes'].items())
        out += [f'        {line(code)}: {line(entry)}' + (',' if j < len(codes) - 1 else '')
                for j, (code, entry) in enumerate(codes)]
        out += ['      }', '    }' + (',' if i < len(names) - 1 else '')]
    return '\n'.join(out + ['  }', '}']) + '\n'


if __name__ == '__main__':
    from jsonschema import Draft202012Validator, FormatChecker
    from strict_schema import strict
    from azarashi import code_tables
    from examples.schema import schema_text
    root = Path(__file__).resolve().parents[2]
    (root / 'azarashi/json/schemas/report-v2.schema.json').write_text(schema_text(), encoding='utf-8')
    (root / 'docs/json/code-tables-v2.json').write_text(code_tables_text(code_tables()), encoding='utf-8')
    validator = Draft202012Validator(strict(json_schema()), format_checker=FormatChecker())
    chosen = fixtures()
    for r in chosen:
        validator.validate(to_json_dict(r))
    folder = root / 'docs/json'
    records = [to_json_dict(r) for r in chosen]
    (folder / 'report-v2.examples.ndjson').write_text(''.join(
        json.dumps(r, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n'
        for r in records), encoding='utf-8')
    (folder / 'report-v2.examples.pretty.json').write_text(
        json.dumps(records, ensure_ascii=False, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote the schema, the code tables, {len(TYPE_NAMES)} report variants and {len(chosen)} complete examples.')
