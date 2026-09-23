"""Intensity categories of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017 Table 4.1.2-49.

Very Strong and Violent are JMA's, from Very Strong Typhoon (TY) and Violent Typhoon (TY) in its
multilingual dictionary of weather information terms (気象情報等に関する多言語辞書, updated 2026-03-26). The
dictionary gives no word for Strong alone, and the English for 0, 1 and 15 is azarashi's.
"""
from ...code_table import CodeTable

typhoon_intensity_category = CodeTable(
    {
        0: "なし",
        1: "強い",
        2: "非常に強い",
        3: "猛烈な",
        15: "その他の強さ階級分類",
        # "NN*": "強さ階級分類(コード番号：NN)",
    },
    undefined="強さ階級分類(コード番号：%d)"
)


typhoon_intensity_category_en = CodeTable(
    {
        0: "None",
        1: "Strong",
        2: "Very Strong",
        3: "Violent",
        15: "Other Intensity Category",
    },
    undefined="Undefined Typhoon Intensity (Code: %d)"
)
