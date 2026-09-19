"""Every message in the sample logs, rendered and listed field by field, compared with tests/golden.

After an intended change of the output, regenerate the files and review the difference:
    python tests/test_golden.py
"""
import datetime
import os
import sys
from pprint import pformat

import pytest

import azarashi
from azarashi.decoders import NmeaQzssDcrDecoder
from azarashi.reports import QzssDcReportJmaNankaiTroughEarthquake as Nankai

_CONTROLS = {c: f'\\x{c:02x}' for c in [*range(0x00, 0x09), *range(0x0b, 0x20), *range(0x7f, 0xa0)]}  # readable diffs
TESTS = os.path.dirname(os.path.realpath(__file__))
LOGS = {  # log -> the time the messages are taken as received at
    'qzqsm_220307.log': datetime.datetime(2022, 3, 7, 6, 0, tzinfo=datetime.UTC),
    'qzqsm_dcx_240604.log': datetime.datetime(2024, 6, 4, 3, 0, tzinfo=datetime.UTC),
}


def render(log):
    Nankai.reports, Nankai.completed, Nankai.announcement = {}, False, None  # pages are assembled across the log
    blocks = []
    with open(os.path.join(TESTS, log), encoding='utf-8') as f:
        for line in f:
            if not line.startswith('$QZQSM'):
                continue
            sentence = line.strip()
            try:
                report = NmeaQzssDcrDecoder(sentence, timestamp=LOGS[log]).decode()
            except azarashi.AzarashiInvalidMessageError as e:
                blocks.append(f'>>> {sentence}\n# [{type(e).__name__}] {e}\n')
                continue
            params = report.get_params()
            if 'camf' in params:
                params['camf'] = vars(params['camf'])
            blocks.append(f'>>> {sentence}\n{type(report).__name__}\n{report}\n{pformat(params, width=120)}\n')
    return '\n'.join(blocks).translate(_CONTROLS)


def _golden(log):
    return os.path.join(TESTS, 'golden', log.replace('.log', '.txt'))


@pytest.fixture(autouse=True)
def fresh_nankai_assembly(monkeypatch):
    monkeypatch.setattr(Nankai, 'reports', {})
    monkeypatch.setattr(Nankai, 'completed', False)
    monkeypatch.setattr(Nankai, 'announcement', None)


@pytest.mark.parametrize('log', sorted(LOGS))
def test_log_matches_golden(log):
    with open(_golden(log), encoding='utf-8') as f:
        expected = f.read()
    assert render(log) == expected


if __name__ == '__main__':
    os.makedirs(os.path.join(TESTS, 'golden'), exist_ok=True)
    for name in sorted(LOGS):
        with open(_golden(name), 'w', encoding='utf-8') as out:
            out.write(render(name))
        print(f'wrote {_golden(name)}', file=sys.stderr)
