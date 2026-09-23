"""Warning codes of the JMA-DC Report (Ash Fall), IS-QZSS-DCR-017 Table 4.1.2-36.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. The English for 7 is
azarashi's, in the dictionary's wording where it has one.
"""
from ...code_table import CodeTable

ash_fall_warning_code = CodeTable(
    {
        1: "少量の降灰",
        2: "やや多量の降灰",
        3: "多量の降灰",
        4: "小さな噴石の落下",
        7: "その他の防災気象情報要素2",
        # "N*": "防災気象情報要素2(コード番号：N)",
    },
    undefined="防災気象情報要素2(コード番号：%d)"
)


ash_fall_warning_code_en = CodeTable(
    {
        1: "Low ash fall",
        2: "Moderate ash fall",
        3: "Heavy ash fall",
        4: "Falling debris",
        7: "Other Ash Fall Warning",
    },
    undefined="Undefined Ash Fall Warning (Code: %d)"
)
