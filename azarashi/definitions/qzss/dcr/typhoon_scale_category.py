"""Scale categories of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017 Table 4.1.2-48.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. The English for 0 and 15 is
azarashi's, in the dictionary's wording where it has one.
"""
from ...code_table import CodeTable

typhoon_scale_category = CodeTable(
    {
        0: "なし",
        1: "大型",
        2: "超大型",
        15: "その他の大きさ階級分類",
        # "NN*": "大きさ階級分類(コード番号：NN)",
    },
    undefined="大きさ階級分類(コード番号：%d)"
)


typhoon_scale_category_en = CodeTable(
    {
        0: "None",
        1: "Large",
        2: "Very large",
        15: "Other Scale Category",
    },
    undefined="Undefined Typhoon Scale (Code: %d)"
)
