from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_ash_fall_warning_type = QzssDcrDefinition(
    {
        1: "速報",  # Ash Fall Forecast (Preliminary)
        2: "詳細",  # Ash Fall Forecast (Detailed)
    },
    undefined="降灰予報(コード番号：%d)"
)
