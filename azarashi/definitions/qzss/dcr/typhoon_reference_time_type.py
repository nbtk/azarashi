"""Reference time types of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. Estimate and Forecast are the
English IS-QZSS-DCR-017 itself uses. A name with no source has no English here.
"""
from ...code_table import CodeTable

typhoon_reference_time_type = CodeTable(
    {
        1: "実況",
        2: "推定",
        3: "予報",
    },
    undefined="基点時刻分類(コード番号：%d)"
)


typhoon_reference_time_type_en = CodeTable(
    {
        1: "Analysis",
        2: "Estimate",
        3: "Forecast",
    },
    undefined="Undefined Reference Time Type (Code: %d)"
)
