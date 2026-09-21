from ...code_table import CodeTable

expected_ash_fall_time = CodeTable(
    {hours: f"{hours}時間" for hours in range(1, 7)},
    undefined="基点時刻からの時間(コード番号：%d)"
)
