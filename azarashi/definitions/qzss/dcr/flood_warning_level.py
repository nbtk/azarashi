"""Warning levels of the JMA-DC Report (Flood), IS-QZSS-DCR-017 Table 4.1.2-44.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. The English for 1 and 15 is
azarashi's, in the dictionary's wording where it has one.
"""
from ...code_table import CodeTable

flood_warning_level = CodeTable(
    {
        1: "警報解除",
        2: "氾濫警戒情報",
        3: "氾濫危険情報",
        4: "氾濫発生情報",
        15: "その他の警戒レベル",
        # "NN*": "警戒レベル(コード番号：NN)",
    },
    undefined="警戒レベル(コード番号：%d)"
)


flood_warning_level_en = CodeTable(
    {
        1: "Warning Lifted",
        2: "Information to provide a warning on flooding",
        3: "Information on potential flood hazards",
        4: "Information on flooding",
        15: "Other Warning Level",
    },
    undefined="Undefined Warning Level (Code: %d)"
)
