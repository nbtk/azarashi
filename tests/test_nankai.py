"""Page assembly of Nankai Trough earthquake information."""
import os

import pytest

import azarashi
from azarashi.qzss_dcr_lib.report.qzss_dc_report import QzssDcReportJmaNankaiTroughEarthquake as Nankai
from qzqsm import with_fields

LOG = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'qzqsm_220307.log')
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
    """page number -> sentence of the 27-page announcement in the log (issued at 04:35 UTC)"""
    pages = {}
    with open(LOG, encoding='utf-8') as f:
        for line in f:
            if line.startswith('$QZQSM') and _field(line, 17, 4) == 4:  # disaster category: Nankai Trough
                pages.setdefault(_field(line, *PAGE_NUMBER), line.strip())
    assert sorted(pages) == list(range(1, 28))
    return pages


def _announcement_b():
    """A later announcement (04:40 UTC) with the same layout and a text of 'B's."""
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
    with open(LOG, encoding='utf-8') as f:
        reports = [azarashi.decode(line.strip()) for line in f if line.startswith('$QZQSM')]
    nankai = [r for r in reports if isinstance(r, Nankai)]
    assert len(nankai) == 81 and nankai[-1].completed is True
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
