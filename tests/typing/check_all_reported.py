"""Check that the type checker reported every line of the generated file with its expected error code.

A count of errors is not enough, since two errors on one line and none on another add up to the
same count. The error code matters as well: a call reported for a missing argument does not show
that the type of the argument is checked.

Reads mypy's text output or pyright's --outputjson output.

  python check_all_reported.py every_misuse.py mypy.txt
  python check_all_reported.py every_misuse.py pyright.json
"""
import json
import pathlib
import re
import sys

#: 二つの検査器は同じ誤りを違う名前で呼ぶ
PYRIGHT = {'reportArgumentType': 'arg-type',
           'reportCallIssue': 'arg-type',
           'reportAssignmentType': 'assignment',
           'reportAttributeAccessIssue': 'assignment'}

generated, report = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
text = report.read_text()

lines = generated.read_text().splitlines()
want = {n: m.group(1)
        for n, line in enumerate(lines, start=1)
        for m in [re.search(r'# want: ([a-z-]+)$', line)] if m}

got: dict[int, set[str]] = {}
if text.lstrip().startswith('{'):
    checker = 'pyright'
    for d in json.loads(text)['generalDiagnostics']:
        if d['severity'] != 'error':
            continue
        code = PYRIGHT.get(d.get('rule', ''))
        if code:
            got.setdefault(d['range']['start']['line'] + 1, set()).add(code)
else:
    checker = 'mypy'
    for n_, code in re.findall(r'^[^:]+:(\d+): error:.*\[([a-z-]+)\]$', text, re.M):
        got.setdefault(int(n_), set()).add(code)

missed = [(n, c) for n, c in want.items() if c not in got.get(n, set())]
print('checker           : %s' % checker)
print('wrong uses written: %d' % len(want))
print('reported as meant : %d' % (len(want) - len(missed)))
if missed:
    print('NOT REPORTED AS MEANT:')
    for n, c in missed:
        print('  %d: want %s, got %s | %s'
              % (n, c, sorted(got.get(n, ())) or 'nothing', lines[n - 1].strip()))
    sys.exit(1)
if not want:
    print('the generator produced nothing')
    sys.exit(1)
print('every wrong use was reported for the reason it was written')
