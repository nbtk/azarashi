from ...code_table import CodeTable

tsunami_height = CodeTable(
    {
        1: "0.2m未満",
        2: "1m",
        3: "3m",
        4: "5m",
        5: "10m",
        6: "10m超",
        13: "該当情報なし",
        14: "不明",
        15: "その他の津波の高さ",
        # "NN*": "津波の高さ(コード番号：NN)",
    },
    undefined="津波の高さ(コード番号：%d)",
)
