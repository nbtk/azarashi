from ...code_table import CodeTable

typhoon_elapsed_time_from_reference_time = CodeTable(
    {hours: f"{hours}時間後" for hours in range(0, 128)},
    undefined="情報の基点時刻からの経過時間(コード番号：%d)"
)
