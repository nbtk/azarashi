"""Warning codes of the JMA-DC Report (Volcano), IS-QZSS-DCR-017 Table 4.1.2-31.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. 24 is taken from the
dictionary's Volcanic Warning: extreme caution advised at the foot of mountains concerned. The
English for 127 is azarashi's.
"""
from ...code_table import CodeTable

volcanic_warning_code = CodeTable(
    {
        11: "レベル1(活火山であることに留意)",
        12: "レベル2(火口周辺規制)",
        13: "レベル3(入山規制)",
        14: "レベル4(高齢者等避難)",
        15: "レベル5(避難)",
        21: "活火山であることに留意",
        22: "火口周辺危険",
        23: "入山危険",
        24: "山麓厳重警戒",
        25: "居住地域厳重警戒",
        35: "活火山であることに留意(海底火山)",
        36: "周辺海域警戒",
        52: "噴火",
        62: "噴火したもよう",
        127: "その他の防災気象情報要素",
        # "NNN*": "防災気象情報要素(コード番号：NNN)",
    },
    undefined="防災気象情報要素(コード番号：%d)"
)


volcanic_warning_code_en = CodeTable(
    {
        11: "Level 1 (Potential for increased activity)",
        12: "Level 2 (Restriction on proximity to the crater)",
        13: "Level 3 (Restriction on proximity to the volcano)",
        14: "Level 4 (Evacuation of the elderly, etc.)",
        15: "Level 5 (Evacuation)",
        21: "Potential for increased activity",
        22: "Caution advised around the crater",
        23: "Caution in non-residential areas near the crater",
        24: "Extreme caution advised at the foot of mountains concerned",
        25: "Extreme caution advised in residential areas and non-residential areas nearer the crater",
        35: "Potential for increased activity (Submarine volcano)",
        36: "Caution advised for the sea area in the vicinity of the volcano",
        52: "Volcanic eruptions",
        62: "Possible eruption",
        127: "Other Volcanic Warning",
    },
    undefined="Undefined Volcanic Warning (Code: %d)"
)
