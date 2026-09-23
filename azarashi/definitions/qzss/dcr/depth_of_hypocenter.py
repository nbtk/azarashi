"""Depths of the hypocenter, IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m. Unknown is the dictionary's word for 不明.
"""
from ...code_table import CodeTable

depth_of_hypocenter = CodeTable(
    {
        **{km: f"{km}km" for km in range(0, 501)},
        501: "500kmより深い",
        511: "不明",
    },
    undefined="深さ(コード番号：%d)"
)


depth_of_hypocenter_en = CodeTable(
    {
        **{km: f"{km} km" for km in range(0, 501)},
        501: "Deeper than 500 km",
        511: "Unknown",
    },
    undefined="Undefined Depth (Code: %d)"
)
