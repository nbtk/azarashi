from ...code_table import CodeTable

long_period_ground_motion_lower_limit = CodeTable(
    {
        0: None,
        1: "長周期地震動階級1未満",
        2: "長周期地震動階級1",
        3: "長周期地震動階級2",
        4: "長周期地震動階級3",
        5: "長周期地震動階級4",
        7: "不明",
    },
    undefined="長周期地震動階級(下限)(コード番号：%d)"
)
