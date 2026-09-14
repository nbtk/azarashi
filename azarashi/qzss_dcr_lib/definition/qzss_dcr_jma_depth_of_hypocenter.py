from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_depth_of_hypocenter = QzssDcrDefinition(
    {
        **{km: f"{km}km" for km in range(0, 501)},
        501: "500kmより深い",
        511: "不明",
    },
    undefined="深さ(コード番号：%d)"
)
