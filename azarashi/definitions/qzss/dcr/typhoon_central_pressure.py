from ...code_table import CodeTable

typhoon_central_pressure = CodeTable(
    {hpa: f"{hpa}hPa" for hpa in range(0, 1101)},
    undefined="中心気圧(コード番号：%d)"
)
