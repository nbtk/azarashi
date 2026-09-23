"""Upper limits of the long-period ground motion class of the EEW, IS-QZSS-DCR-017.

Unknown is the dictionary's word for 不明 wherever it appears. The English for 1, 2, 3, 4, 5 and 6 is
azarashi's, in the dictionary's wording where it has one; Less than is how JMA's map of tsunami
information writes 未満.
"""
from ...code_table import CodeTable

long_period_ground_motion_upper_limit = CodeTable(
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


long_period_ground_motion_upper_limit_en = CodeTable(
    {
        1: "Less than Long-Period Ground Motion class of 1",
        2: "Long-Period Ground Motion class of 1",
        3: "Long-Period Ground Motion class of 2",
        4: "Long-Period Ground Motion class of 3",
        5: "Long-Period Ground Motion class of 4",
        6: "or greater",
        7: "Unknown",
    },
    undefined="Undefined Long-Period Ground Motion Upper Limit (Code: %d)"
)
