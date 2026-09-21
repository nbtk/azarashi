from ...code_table import CodeTable

typhoon_number = CodeTable(
    {n: f"{n}号" for n in range(1, 100)},
    undefined="台風番号(コード番号：%d)"
)
