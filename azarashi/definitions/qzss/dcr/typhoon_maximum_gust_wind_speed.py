"""Maximum wind gust speeds of the JMA-DC Report (Typhoon), IS-QZSS-DCR-017.

The English is azarashi's: the Japanese, with the unit spaced as JMA's multilingual dictionary of
weather information terms writes Over 10 m. Unknown is the dictionary's word for 不明.
"""
from ...code_table import CodeTable

typhoon_maximum_gust_wind_speed = CodeTable(
    {
        0: "不明",
        **{ms: f"{ms}m/s" for ms in range(15, 106)},
    },
    undefined="最大瞬間風速(コード番号：%d)"
)


typhoon_maximum_gust_wind_speed_en = CodeTable(
    {
        0: "Unknown",
        **{ms: f"{ms} m/s" for ms in range(15, 106)},
    },
    undefined="Undefined Maximum Wind Gust Speed (Code: %d)"
)
