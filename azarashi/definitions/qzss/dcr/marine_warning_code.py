"""Warning codes of the JMA-DC Report (Marine), IS-QZSS-DCR-017 Table 4.1.2-52.

The English for 11 and 21 to 23 is JMA's, as its explanation of the Asia-Pacific surface analysis
chart (https://www.jma.go.jp/jma/kishou/know/kurashi/ASAS_kaisetu.html, retrieved 2026-09-24) names
the marine warnings: FOG WARNING, GALE WARNING, STORM WARNING and TYPHOON WARNING. JMA writes them
in capitals; here each word begins with a capital, as in the other tables. Only the case is
changed.

The same chart calls 海上風警報, 20, just WARNING, which tells what it is only beside the others on the
chart. Alone it would drop the 風 the Japanese says, so the English here is Wind Warning, with the
dictionary's Wind.

The English for 0, 10, 12, 20 and 31 is azarashi's, made the way JMA names the others, of the words
of JMA's multilingual dictionary of weather information terms (気象情報等に関する多言語辞書, updated 2026-03-26):
Wind, Ice accretion and Sea swell, and Marine as in its Volcanic Marine Warning, which sets 0 and
31 apart from the other warnings.
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
        10: "Ice Accretion Warning",
        11: "Fog Warning",
        12: "Swell Warning",
        20: "Wind Warning",
        21: "Gale Warning",
        22: "Storm Warning",
        23: "Typhoon Warning",
        31: "Other Marine Warning",
    },
    undefined="Undefined Marine Warning (Code: %d)"
)
