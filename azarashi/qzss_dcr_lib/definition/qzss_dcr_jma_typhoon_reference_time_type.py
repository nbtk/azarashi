from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_reference_time_type = QzssDcrDefinition(
    {
        1: "実況",  # Analysis
        2: "推定",  # Estimation
        3: "予報",  # Forecast
    },
    undefined="基点時刻分類(コード番号：%d)"
)
