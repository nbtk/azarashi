from ...code_table import CodeTable

tsunami_warning_code = CodeTable(
    {
        1: "津波なし",
        2: "警報解除",
        3: "津波警報",
        4: "大津波警報",
        5: "大津波警報：発表",
        15: "その他の警報",
        # "NN*": "警報(コード番号：NN)",
    },
    undefined="警報(コード番号：%d)"
)
