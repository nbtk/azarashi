"""Magnitudes of the JMA-DC Report (Hypocenter), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m. Unknown is the dictionary's word for 不明.
"""
from ...code_table import CodeTable

hypocenter_magnitude = CodeTable(
    {
        **{ma: f"{ma / 10}" for ma in range(1, 101)},  # the code is the magnitude in steps of 0.1
        101: "10.0より大きい",
        126: "不明(8.0より大きい)",
        127: "不明",
    },
    undefined="マグニチュード(コード番号：%d)"
)


hypocenter_magnitude_en = CodeTable(
    {
        **{ma: f"{ma / 10}" for ma in range(1, 101)},
        101: "Over 10.0",
        126: "Unknown (Over 8.0)",
        127: "Unknown",
    },
    undefined="Undefined Magnitude (Code: %d)"
)
