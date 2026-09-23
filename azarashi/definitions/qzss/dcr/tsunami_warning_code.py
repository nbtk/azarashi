"""Warning codes of the JMA-DC Report (Tsunami), IS-QZSS-DCR-017 Table 4.1.2-22.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. The English for 1, 2, 5 and
15 is azarashi's, in the dictionary's wording where it has one.
"""
from ...code_table import CodeTable

tsunami_warning_code = CodeTable(
    {
        1: "津波なし",
        2: "警報解除",
        3: "津波警報",
        4: "大津波警報",
        5: "大津波警報：発表",
        15: "その他の警報",
        # "NN*": "警報(コード番号：NN)",
    },
    undefined="警報(コード番号：%d)"
)


tsunami_warning_code_en = CodeTable(
    {
        1: "No Tsunami",
        2: "Warning Lifted",
        3: "Tsunami Warning",
        4: "Major Tsunami Warning",
        5: "Major Tsunami Warning: Issued",
        15: "Other Warning",
    },
    undefined="Undefined Tsunami Warning (Code: %d)"
)
