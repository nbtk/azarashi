from ...code_table import CodeTable

typhoon_scale_category = CodeTable(
    {
        0: "なし",
        1: "大型",
        2: "超大型",
        15: "その他の大きさ階級分類",
        # "NN*": "大きさ階級分類(コード番号：NN)",
    },
    undefined="大きさ階級分類(コード番号：%d)"
)
