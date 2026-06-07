from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_seismic_intensity = QzssDcrDefinition(
    {
        1: "4未満",
        2: "4",
        3: "5弱",
        4: "5強",
        5: "6弱",
        6: "6強",
        7: "7",
    },
    undefined="震度(コード番号：%d)"
)
