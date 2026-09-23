"""Seismic intensities of the JMA-DC Report (Seismic Intensity), IS-QZSS-DCR-017 Table 4.1.2-15.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. The English for 1, 2 and 7 is
azarashi's, in the dictionary's wording where it has one; Less than is how JMA's map of tsunami
information writes 未満.
"""
from ...code_table import CodeTable

seismic_intensity = CodeTable(
    {
        1: "4未満",
        2: "4",
        3: "5弱",
        4: "5強",
        5: "6弱",
        6: "6強",
        7: "7",
    },
    undefined="震度(コード番号：%d)"
)


seismic_intensity_en = CodeTable(
    {
        1: "Less than 4",
        2: "4",
        3: "5-lower",
        4: "5-upper",
        5: "6-lower",
        6: "6-upper",
        7: "7",
    },
    undefined="Undefined Seismic Intensity (Code: %d)"
)
