"""docs/english-translation-policy.md lists azarashi's English; the lists must agree with the tables."""
import importlib
import pathlib
import re

import pytest

POLICY = pathlib.Path(__file__).resolve().parent.parent / 'docs/english-translation-policy.md'
NOTE = ' (Translated by azarashi)'


def _table(name, suffix=''):
    return getattr(importlib.import_module(f'azarashi.definitions.qzss.dcr.{name}'), name + suffix)


def _cells(line):
    return [cell.strip().replace('\\|', '|') for cell in re.split(r'(?<!\\)\|', line.strip())[1:-1]]


def _listed():
    """(table, code, Japanese, English) of every row under "azarashi's English", table by table."""
    text = POLICY.read_text(encoding='utf-8')
    section = text[text.index("## azarashi's English"):text.index('### Numbers')]
    rows = []
    for heading, body in re.findall(r'^### (\w+)\n(.*?)(?=^### |\Z)', section, re.M | re.S):
        for line in body.splitlines():
            cells = _cells(line) if line.startswith('| ') else []
            if cells and cells[0].isdigit():
                rows.append((heading, int(cells[0]), cells[1], cells[2]))
    return rows


LISTED = _listed()


def test_the_policy_lists_azarashis_english():
    assert len(LISTED) > 80
    assert {table for table, *_ in LISTED} >= {'notification_on_disaster_prevention', 'marine_warning_code',
                                               'flood_forecast_region', 'marine_forecast_region'}


@pytest.mark.parametrize('table, code, japanese, english', LISTED, ids=lambda value: str(value))
def test_a_listed_english_is_the_english_of_its_table(table, code, japanese, english):
    assert _table(table)[code] == japanese
    assert _table(table, '_en')[code] == english


def test_every_sentence_azarashi_translated_is_listed():
    notes = {code for code, text in _table('notification_on_disaster_prevention', '_en').items() if NOTE in text}
    listed = {code for table, code, *_ in LISTED if table == 'notification_on_disaster_prevention'}
    assert notes and notes <= listed


@pytest.mark.parametrize('table, prefix', [
    ('local_government', 'Other municipalities in '),
    ('flood_forecast_region', 'Other rivers in '),
])
def test_a_family_the_policy_counts_has_that_many_entries(table, prefix):
    counted = re.search(rf'`{table}`: (\d+) entries', POLICY.read_text(encoding='utf-8'))
    assert counted, table
    made = [text for text in _table(table, '_en').values() if text.startswith(prefix)]
    assert len(made) == int(counted.group(1))


def test_the_count_the_policy_gives_is_the_rows_it_lists():
    stated = re.search(r'^(\d+) entries are listed one by one below\.', POLICY.read_text(encoding='utf-8'), re.M)
    assert stated and int(stated.group(1)) == len(LISTED)
