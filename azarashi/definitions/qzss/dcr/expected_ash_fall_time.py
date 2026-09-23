"""Expected ash fall times of the JMA-DC Report (Ash Fall), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m.
"""
from ...code_table import CodeTable

expected_ash_fall_time = CodeTable(
    {hours: f"{hours}時間" for hours in range(1, 7)},
    undefined="基点時刻からの時間(コード番号：%d)"
)


expected_ash_fall_time_en = CodeTable(
    {hours: f"{hours} hour" if hours == 1 else f"{hours} hours" for hours in range(1, 7)},
    undefined="Undefined Expected Ash Fall Time (Code: %d)"
)
