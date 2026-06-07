from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_weather_warning_state = QzssDcrDefinition(
    {
        1: "発表",
        2: "解除",
        # "N*": "発表状況(コード番号：N)",
    },
    undefined="発表状況(コード番号：%d)"
)
