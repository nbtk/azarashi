"""Lower limits of the seismic intensity of the EEW, IS-QZSS-DCR-017 Table 4.1.2-8.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. Unknown is the dictionary's
word for 不明 wherever it appears. The English for 1, 2, 3 and 14 is azarashi's, in the dictionary's
wording where it has one.
"""
from ...code_table import CodeTable

seismic_intensity_lower_limit = CodeTable(
    {
        1: "震度0",
        2: "震度1",
        3: "震度2",
        4: "震度3",
        5: "震度4",
        6: "震度5弱",
        7: "震度5強",
        8: "震度6弱",
        9: "震度6強",
        10: "震度7",
        14: "なし",
        15: "不明",
    },
    undefined="震度(下限)(コード番号：%d)"
)


seismic_intensity_lower_limit_en = CodeTable(
    {
        1: "Seismic intensity of 0",
        2: "Seismic intensity of 1",
        3: "Seismic intensity of 2",
        4: "Seismic intensity of 3",
        5: "Seismic intensity of 4",
        6: "Seismic intensity of 5-lower",
        7: "Seismic intensity of 5-upper",
        8: "Seismic intensity of 6-lower",
        9: "Seismic intensity of 6-upper",
        10: "Seismic intensity of 7",
        14: "None",
        15: "Unknown",
    },
    undefined="Undefined Seismic Intensity Lower Limit (Code: %d)"
)
