from ...code_table import CodeTable

weather_warning_state = CodeTable(
    {
        1: "発表",
        2: "解除",
        # "N*": "発表状況(コード番号：N)",
    },
    undefined="発表状況(コード番号：%d)"
)
