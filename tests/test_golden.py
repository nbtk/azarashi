"""Every message in the sample logs, rendered and listed field by field, compared with tests/golden.

After an intended change of the output, regenerate the files and review the difference:
    python tests/test_golden.py
"""
import datetime
import gzip
import os
import sys
from pprint import pformat

import pytest

import azarashi
from azarashi.decoders import nmea
from azarashi.reports.dcr import NankaiTroughEarthquake as Nankai

_CONTROLS = {c: f'\\x{c:02x}' for c in [*range(0x00, 0x09), *range(0x0b, 0x20), *range(0x7f, 0xa0)]}  # readable diffs
TESTS = os.path.dirname(os.path.realpath(__file__))
LOGS = {  # log -> the time the messages are taken as received at
    'qzqsm_260821.log': datetime.datetime(2026, 8, 21, 15, 0, tzinfo=datetime.UTC),
    'qzqsm_dcx_260917.log': datetime.datetime(2026, 9, 17, 3, 0, tzinfo=datetime.UTC),
    'qzqsm_260924.log': datetime.datetime(2026, 9, 24, 5, 0, tzinfo=datetime.UTC),
}
JSON_LOGS = sorted(LOGS)  # the logs whose reports are compared as JSON as well
#: the QZSS L1S frames of a u-blox receiver on 2026-09-24, 10:00-12:00 JST, with nothing else it sent:
#: the messages of qzqsm_260924.log as a u-blox stream gives them, in the order they arrived
RECORDING = 'ublox_260924.ubx.gz'
RECORDING_REPORTS = 7039


def render(log):
    Nankai.reports, Nankai.completed, Nankai.announcement = {}, False, None  # pages are assembled across the log
    blocks = []
    with open(os.path.join(TESTS, log), encoding='utf-8') as f:
        for line in f:
            if not line.startswith('$QZQSM'):
                continue
            sentence = line.strip()
            try:
                report = nmea.Decoder(sentence, timestamp=LOGS[log]).decode()
            except azarashi.AzarashiInvalidMessageError as e:
                blocks.append(f'>>> {sentence}\n# [{type(e).__name__}] {e}\n')
                continue
            params = report.get_params()
            if 'camf' in params:
                params['camf'] = vars(params['camf'])
            blocks.append(f'>>> {sentence}\n{type(report).__name__}\n{report}\n{pformat(params, width=120)}\n')
    return '\n'.join(blocks).translate(_CONTROLS)


def render_json(log):
    Nankai.reports, Nankai.completed, Nankai.announcement = {}, False, None
    records = []
    with open(os.path.join(TESTS, log), encoding='utf-8') as f:
        for line in f:
            if line.startswith('$QZQSM'):
                records.append(azarashi.to_ndjson(nmea.Decoder(line.strip(), timestamp=LOGS[log]).decode()))
    return ''.join(records)


def _golden(log, suffix='.txt'):
    return os.path.join(TESTS, 'golden', log.replace('.log', suffix))


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


@pytest.mark.parametrize('log', JSON_LOGS)
def test_log_matches_json_golden(log):
    with open(_golden(log, '.ndjson'), encoding='utf-8') as f:
        expected = f.read()
    assert render_json(log) == expected


def _message(report):
    return type(report), report.raw


def test_the_recording_gives_the_messages_of_its_log():
    log = 'qzqsm_260924.log'
    with open(os.path.join(TESTS, log), encoding='utf-8') as f:
        logged = {_message(azarashi.decode(line.strip())) for line in f if line.startswith('$QZQSM')}
    reports = []
    with gzip.open(os.path.join(TESTS, RECORDING)) as f, pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(f, 'ublox', callback=reports.append, ignore_dcx=False, timestamp=LOGS[log])
    assert len(reports) == RECORDING_REPORTS
    assert {_message(report) for report in reports} <= logged


if __name__ == '__main__':
    os.makedirs(os.path.join(TESTS, 'golden'), exist_ok=True)
    for name in sorted(LOGS):
        with open(_golden(name), 'w', encoding='utf-8') as out:
            out.write(render(name))
        print(f'wrote {_golden(name)}', file=sys.stderr)
    for name in JSON_LOGS:
        with open(_golden(name, '.ndjson'), 'w', encoding='utf-8') as out:
            out.write(render_json(name))
        print(f'wrote {_golden(name, ".ndjson")}', file=sys.stderr)
