"""Warning states of the JMA-DC Report (Weather), IS-QZSS-DCR-017 Table 4.1.2-39.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. A name with no source has no
English here.
"""
from ...code_table import CodeTable

weather_warning_state = CodeTable(
    {
        1: "発表",
        2: "解除",
        # "N*": "発表状況(コード番号：N)",
    },
    undefined="発表状況(コード番号：%d)"
)


weather_warning_state_en = CodeTable(
    {
        1: "Announcement",
        2: "Cancel",
    },
    undefined="Undefined Warning State (Code: %d)"
)
