from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_expected_ash_fall_time = QzssDcrDefinition(
    {hours: f"{hours}時間" for hours in range(1, 7)},
    undefined="基点時刻からの時間(コード番号：%d)"
)
