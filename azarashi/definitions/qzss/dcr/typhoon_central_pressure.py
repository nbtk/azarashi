"""Central pressures of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m.
"""
from ...code_table import CodeTable

typhoon_central_pressure = CodeTable(
    {hpa: f"{hpa}hPa" for hpa in range(0, 1101)},
    undefined="中心気圧(コード番号：%d)"
)


typhoon_central_pressure_en = CodeTable(
    {hpa: f"{hpa} hPa" for hpa in range(0, 1101)},
    undefined="Undefined Central Pressure (Code: %d)"
)
