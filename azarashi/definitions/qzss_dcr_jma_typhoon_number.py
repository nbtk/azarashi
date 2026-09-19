from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_number = QzssDcrDefinition(
    {n: f"{n}号" for n in range(1, 100)},
    undefined="台風番号(コード番号：%d)"
)
