from ...code_table import CodeTable

typhoon_maximum_gust_wind_speed = CodeTable(
    {
        0: "不明",
        **{ms: f"{ms}m/s" for ms in range(15, 106)},
    },
    undefined="最大瞬間風速(コード番号：%d)"
)
