from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_central_pressure = QzssDcrDefinition(
    {hpa: f"{hpa}hPa" for hpa in range(0, 1101)},
    undefined="中心気圧(コード番号：%d)"
)
