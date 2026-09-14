from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_hypocenter_magnitude = QzssDcrDefinition(
    {
        **{ma: f"{ma / 10}" for ma in range(1, 101)},  # 0.1 unit of the magnitude
        101: "10.0より大きい",
        126: "不明(8.0より大きい)",
        127: "不明",
    },
    undefined="マグニチュード(コード番号：%d)"
)
