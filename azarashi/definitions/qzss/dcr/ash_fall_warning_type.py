"""Types of the JMA-DC Report (Ash Fall), IS-QZSS-DCR-017.

The English is what IS-QZSS-DCR-017 itself uses, in Volcanic Ash Fall Forecast (Preliminary) and
Volcanic Ash Fall Forecast (Detailed). A name with no source has no English here.
"""
from ...code_table import CodeTable

ash_fall_warning_type = CodeTable(
    {
        1: "速報",
        2: "詳細",
    },
    undefined="降灰予報(コード番号：%d)"
)


ash_fall_warning_type_en = CodeTable(
    {
        1: "Preliminary",
        2: "Detailed",
    },
    undefined="Undefined Ash Fall Forecast Type (Code: %d)"
)
