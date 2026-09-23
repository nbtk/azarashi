"""Elapsed times from the reference time of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m. Hours ahead is the dictionary's, from its Forecast for
X hours ahead.
"""
from ...code_table import CodeTable

typhoon_elapsed_time_from_reference_time = CodeTable(
    {hours: f"{hours}時間後" for hours in range(0, 128)},
    undefined="情報の基点時刻からの経過時間(コード番号：%d)"
)


typhoon_elapsed_time_from_reference_time_en = CodeTable(
    {hours: f"{hours} hour ahead" if hours == 1 else f"{hours} hours ahead" for hours in range(0, 128)},
    undefined="Undefined Elapsed Time (Code: %d)"
)
