"""Which library A11 indexes. A9 chooses between CAMF's own and a country's, A10 its version.

The choice belongs here rather than in each caller: a decoder and the JSON conversion both need
it, and one rule in two places is a rule that can disagree with itself. The modules are imported
whole, so that the tables themselves are named in one place only.
"""
from typing import NamedTuple

from ..code_table import CodeTable
from . import a11_international_library as international
from . import a11_japanese_library as japanese


class A11Library(NamedTuple):
    """The tables A11 indexes. Every field is None for a library azarashi has not got."""

    name: str  # 'international', 'japanese', or '' when there is no library to read
    ja: CodeTable[int, str] | None
    en: CodeTable[int, str] | None
    identifier: CodeTable[int, str] | None  # the IC-A-nn names, which only CAMF's library gives


NO_LIBRARY = A11Library('', None, None, None)


def a11_library(a9: int, a2: int, a10: int) -> A11Library:
    """The library the guidance instruction comes from, empty when azarashi cannot read it."""
    if a10 != 0:  # only version #1 of any library is carried
        return NO_LIBRARY
    if a9 == 0:  # the international library is one table, shared by every country
        return A11Library('international', None,
                          international.a11_international_library,
                          international.a11_international_library_code)
    if a2 == 111:
        return A11Library('japanese',
                          japanese.a11_japanese_library_ja,
                          japanese.a11_japanese_library_en, None)
    return NO_LIBRARY
