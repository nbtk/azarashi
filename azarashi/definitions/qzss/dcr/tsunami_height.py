"""Tsunami heights of the JMA-DC Report (Tsunami), IS-QZSS-DCR-017 Table 4.1.2-23.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. Unknown is the dictionary's
word for 不明 wherever it appears. Less than 0.2 m, for 1, is JMA's, as its map of tsunami
information (https://www.jma.go.jp/bosai/map.html, retrieved 2026-09-24) writes it. 1 m, 3 m, 5 m
and 10 m, for 2 to 5, are JMA's, as its English guide to tsunami warnings
(https://www.data.jma.go.jp/eqev/data/en/guide/tsunamiinfo.html, retrieved 2026-09-24) writes the
estimated heights. The English for 13 and 15 is azarashi's, in the dictionary's wording where it
has one.
"""
from ...code_table import CodeTable

tsunami_height = CodeTable(
    {
        1: "0.2m未満",
        2: "1m",
        3: "3m",
        4: "5m",
        5: "10m",
        6: "10m超",
        13: "該当情報なし",
        14: "不明",
        15: "その他の津波の高さ",
        # "NN*": "津波の高さ(コード番号：NN)",
    },
    undefined="津波の高さ(コード番号：%d)",
)


tsunami_height_en = CodeTable(
    {
        1: "Less than 0.2 m",
        2: "1 m",
        3: "3 m",
        4: "5 m",
        5: "10 m",
        6: "Over 10 m",
        13: "No information",
        14: "Unknown",
        15: "Other Tsunami Height",
    },
    undefined="Undefined Tsunami Height (Code: %d)"
)
