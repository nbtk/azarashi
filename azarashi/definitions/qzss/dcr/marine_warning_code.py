"""Warning codes of the JMA-DC Report (Marine), IS-QZSS-DCR-017 Table 4.1.2-52.

No JMA source names these warnings in English. The English is azarashi's, made of the words of
JMA's multilingual dictionary of weather information terms (気象情報等に関する多言語辞書, updated 2026-03-26):
Marine as in its Volcanic Marine Warning, and Wind, Gale, Storm, Dense fog, Sea swell and Ice
accretion.
"""
from ...code_table import CodeTable

marine_warning_code = CodeTable(
    {
        0: "海上警報解除",
        10: "海上着氷警報",
        11: "海上濃霧警報",
        12: "海上うねり警報",
        20: "海上風警報",
        21: "海上強風警報",
        22: "海上暴風警報",
        23: "海上台風警報",
        31: "その他の警報等情報要素_海上警報",
        # 'NN*': "警報等情報要素_海上警報(コード番号：NN)",
    },
    undefined="警報等情報要素_海上警報(コード番号：%d)"
)


marine_warning_code_en = CodeTable(
    {
        0: "Marine Warning Lifted",
        10: "Marine Ice Accretion Warning",
        11: "Marine Dense Fog Warning",
        12: "Marine Swell Warning",
        20: "Marine Wind Warning",
        21: "Marine Gale Warning",
        22: "Marine Storm Warning",
        23: "Marine Typhoon Warning",
        31: "Other Marine Warning",
    },
    undefined="Undefined Marine Warning (Code: %d)"
)
