from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_long_period_ground_motion_upper_limit = QzssDcrDefinition(
    {
        0: None,
        1: "長周期地震動階級1未満",
        2: "長周期地震動階級1",
        3: "長周期地震動階級2",
        4: "長周期地震動階級3",
        5: "長周期地震動階級4",
        6: "〜程度以上",
        7: "不明",
    },
    undefined="長周期地震動階級(上限)(コード番号：%d)"
)
