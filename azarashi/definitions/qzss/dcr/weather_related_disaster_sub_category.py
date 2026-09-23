"""Disaster sub-categories of the JMA-DC Report (Weather), IS-QZSS-DCR-017 Table 4.1.2-40.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. Heavy Rain Emergency Warning
and Record-breaking heavy rain in a short time are the English IS-QZSS-DCR-017 itself uses. The
English for 7 and 31 is azarashi's, in the dictionary's wording where it has one.
"""
from ...code_table import CodeTable

weather_related_disaster_sub_category = CodeTable(
    {
        1: "暴風雪特別警報",
        2: "大雨特別警報",
        3: "暴風特別警報",
        4: "大雪特別警報",
        5: "波浪特別警報",
        6: "高潮特別警報",
        7: "全ての気象特別警報",
        21: "記録的短時間大雨情報",
        22: "竜巻注意情報",
        23: "土砂災害警戒情報",
        31: "その他の警報等情報要素",
        # "NN*": "警報等情報要素(コード番号：NN)",
    },
    undefined="警報等情報要素(コード番号：%d)"
)


weather_related_disaster_sub_category_en = CodeTable(
    {
        1: "Snowstorm Emergency Warning",
        2: "Heavy Rain Emergency Warning",
        3: "Storm Emergency Warning",
        4: "Heavy Snow Emergency Warning",
        5: "High Wave Emergency Warning",
        6: "Storm Surge Emergency Warning",
        7: "All Weather Emergency Warnings",
        21: "Record-breaking heavy rain in a short time",
        22: "Hazardous Wind Watch",
        23: "Landslide Alert Information",
        31: "Other Warning",
    },
    undefined="Undefined Disaster Sub-Category (Code: %d)"
)
