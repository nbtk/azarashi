from ...code_table import CodeTable

depth_of_hypocenter = CodeTable(
    {
        **{km: f"{km}km" for km in range(0, 501)},
        501: "500kmより深い",
        511: "不明",
    },
    undefined="深さ(コード番号：%d)"
)
