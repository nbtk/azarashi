"""Information serial codes of the JMA-DC Report (Nankai Trough Earthquake), IS-QZSS-DCR-017.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. A name with no source has no
English here.
"""
from ...code_table import CodeTable

information_serial_code = CodeTable(
    {
        1: "調査中A（監視領域内でマグニチュード6.8以上の地震が発生したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）",
        2: "調査中B（1カ所以上のひずみ計での有意な変化と共に、他の複数の観測点でもそれに関係すると思われる変化が観測され、想定震源域内のプレート境界で通常と異なるゆっくりすべりが発生している可能性がある場合など、ひずみ計で南海トラフ地震との関連性の検討が必要と認められる変化を観測したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）",
        3: "調査中C（その他、想定震源域内のプレート境界の固着状態の変化を示す可能性のある現象が観測される等、南海トラフ地震との関連性の検討が必要と認められる現象を観測したことにより、臨時に「南海トラフ沿いの地震に関する評価検討会」を開催）",
        4: "巨大地震警戒",
        5: "巨大地震注意",
        6: "調査終了",
        15: "その他の情報",
    },
    undefined="地震関連情報(コード番号：%d)"
)


information_serial_code_en = CodeTable(
    {
        4: "Megathrust Earthquake Alert",
        5: "Megathrust Earthquake Attention",
        6: "Analysis Complete",
    },
    undefined="Undefined Information Serial Code (Code: %d)"
)
