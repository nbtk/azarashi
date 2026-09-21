from ...code_table import CodeTable

ash_fall_warning_type = CodeTable(
    {
        1: "速報",  # Ash Fall Forecast (Preliminary)
        2: "詳細",  # Ash Fall Forecast (Detailed)
    },
    undefined="降灰予報(コード番号：%d)"
)
