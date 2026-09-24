"""Page assembly of Nankai Trough earthquake information."""
import gzip
import os

import pytest

import azarashi
from azarashi.reports import dcr
from azarashi.reports.dcr import NankaiTroughEarthquake as Nankai
from qzqsm import with_fields

TESTS = os.path.dirname(os.path.realpath(__file__))
LOG = os.path.join(TESTS, 'qzqsm_260924.log')
RECORDING = os.path.join(TESTS, 'ublox_260924.ubx.gz')  # the same announcement from two satellites
REPORT_MINUTE = (35, 6)
PAGE_NUMBER = (201, 6)
TOTAL_PAGE = (207, 6)
TEXT_BYTES = [(57 + i * 8, 8) for i in range(18)]


@pytest.fixture(autouse=True)
def fresh_assembly(monkeypatch):
    monkeypatch.setattr(Nankai, 'reports', {})
    monkeypatch.setattr(Nankai, 'completed', False)
    monkeypatch.setattr(Nankai, 'announcement', None)


def _field(sentence, pos, size):
    bits = int(sentence.split(',')[2].split('*')[0], 16) >> 2  # 250-bit message
    return bits >> (250 - pos - size) & ((1 << size) - 1)


def _announcement_a():
    """page number -> sentence of the 27-page announcement in the log (issued at 01:35 UTC)"""
    pages = {}
    with open(LOG, encoding='utf-8') as f:
        for line in f:
            if line.startswith('$QZQSM') and _field(line, 17, 4) == 4:  # disaster category: Nankai Trough
                pages.setdefault(_field(line, *PAGE_NUMBER), line.strip())
    assert sorted(pages) == list(range(1, 28))
    return pages


def _announcement_b():
    """A later announcement (01:40 UTC) with the same layout and a text of 'B's."""
    pages = {}
    for page, sentence in _announcement_a().items():
        text = [(pos, size, ord('B')) for pos, size in TEXT_BYTES]
        pages[page] = with_fields(sentence, [(*REPORT_MINUTE, 40), *text])
    return pages


def test_pages_are_assembled():
    report = None
    for page, sentence in _announcement_a().items():
        report = azarashi.decode(sentence)
        assert report.completed is (page == 27)
    text = report.extract_text_information()
    assert text.startswith('南海トラフ沿いのプレート境界で')
    assert text.endswith('防災対応をとってください。')  # without the 0s after the last character


def test_duplicate_pages_from_several_satellites():
    reports = []
    with gzip.open(RECORDING) as f, pytest.raises(azarashi.AzarashiNoMoreData):
        azarashi.decode_stream(f, 'ublox', callback=reports.append)
    nankai = [r for r in reports if isinstance(r, Nankai)]
    assert len(nankai) == 386 and {r.satellite_prn for r in nankai} == {185, 189}
    assert nankai[-1].completed is True
    assert nankai[-1].extract_text_information().startswith('南海トラフ沿いのプレート境界で')


def test_pages_of_different_announcements_are_not_mixed():
    a, b = _announcement_a(), _announcement_b()
    for page in range(1, 11):  # announcement A: pages 1-10
        azarashi.decode(a[page])
    for page in range(11, 28):  # announcement B: pages 1-10 were missed
        report = azarashi.decode(b[page])
    assert report.completed is False
    assert report.extract_text_information() == '受信中 (27) [17/27]'


def test_newer_announcement_replaces_a_partial_one():
    a, b = _announcement_a(), _announcement_b()
    for page in range(1, 11):
        azarashi.decode(a[page])
    for page in range(1, 28):
        report = azarashi.decode(b[page])
    assert report.completed is True
    assert report.extract_text_information() == 'B' * 18 * 27


def test_late_page_of_an_older_announcement_is_ignored():
    a, b = _announcement_a(), _announcement_b()
    for page in range(1, 27):
        azarashi.decode(b[page])
    late = azarashi.decode(a[5])
    assert late.extract_text_information() == '受信中 (5) [-/27]'
    report = azarashi.decode(b[27])
    assert report.completed is True
    assert report.extract_text_information() == 'B' * 18 * 27


def test_page_that_differs_from_the_one_received_restarts_the_assembly():
    a = _announcement_a()
    azarashi.decode(a[1])
    azarashi.decode(a[2])
    changed = with_fields(a[1], [(*TEXT_BYTES[0], ord('C'))])  # the same page of the same announcement, other text
    report = azarashi.decode(changed)
    assert report.extract_text_information() == '受信中 (1) [1/27]'
    assert Nankai.reports == {1: report}


def _with_page(sentence, page, total):
    return with_fields(sentence, [(*PAGE_NUMBER, page), (*TOTAL_PAGE, total)])


@pytest.mark.parametrize('page, total, code', [  # the code is the page number and the total page (12 bits)
    (0, 1, 1),
    (1, 0, 64),
    (0, 0, 0),
    (5, 3, 323),  # beyond the total page
])
def test_page_that_cannot_be_placed_is_a_code(page, total, code):
    report = azarashi.decode(_with_page(_announcement_a()[1], page, total))
    assert (report.page_number, report.total_page) == (page, total)
    assert report.extract_text_information() == f'ページ番号・総ページ数(コード番号：{code})'
    assert str(report).endswith(f'\nページ番号・総ページ数(コード番号：{code})')
    assert (Nankai.reports, Nankai.completed, Nankai.announcement) == ({}, False, None)


@pytest.mark.parametrize('page, total', [(0, 27), (1, 0), (28, 27)])
def test_page_that_cannot_be_placed_does_not_break_the_assembly(page, total):
    a = _announcement_a()
    for number in range(1, 27):
        azarashi.decode(a[number])
    azarashi.decode(_with_page(a[1], page, total))  # the same announcement time
    report = azarashi.decode(a[27])
    assert report.completed is True
    assert report.extract_text_information().startswith('南海トラフ沿いのプレート境界で')


class _WatchingTheLock(dict):
    """Records whether the assembly lock was held each time the pages were touched."""

    def __init__(self, *args):
        super().__init__(*args)
        self.held = []

    def _note(self):
        self.held.append(dcr._assembly_lock.locked())

    def __getitem__(self, key):
        self._note()
        return super().__getitem__(key)

    def update(self, *args, **kwargs):
        self._note()
        return super().update(*args, **kwargs)


def test_the_pages_are_read_under_the_lock(monkeypatch):
    # another thread starting a newer announcement empties the pages, and a report renders its text
    # from a callback, which decode_stream runs outside its own lock
    a = _announcement_a()
    for number in sorted(a):
        report = azarashi.decode(a[number])
    watched = _WatchingTheLock(Nankai.reports)
    monkeypatch.setattr(Nankai, 'reports', watched)
    assert report.extract_text_information().startswith('南海トラフ沿いのプレート境界で')
    assert watched.held == [True] * 27


def test_a_page_is_placed_under_the_lock(monkeypatch):
    watched = _WatchingTheLock()
    monkeypatch.setattr(Nankai, 'reports', watched)
    azarashi.decode(_announcement_a()[1])
    assert watched.held == [True]
