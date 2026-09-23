"""Typhoon numbers of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m.
"""
from ...code_table import CodeTable

typhoon_number = CodeTable(
    {n: f"{n}号" for n in range(1, 100)},
    undefined="台風番号(コード番号：%d)"
)


typhoon_number_en = CodeTable(
    {n: f"No. {n}" for n in range(1, 100)},
    undefined="Undefined Typhoon Number (Code: %d)"
)
