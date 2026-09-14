from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_maximum_wind_speed = QzssDcrDefinition(
    {
        0: "不明",
        **{ms: f"{ms}m/s" for ms in range(15, 106)},
    },
    undefined="最大風速(コード番号：%d)"
)
