from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_ash_fall_warning_code = QzssDcrDefinition(
    {
        1: "少量の降灰",
        2: "やや多量の降灰",
        3: "多量の降灰",
        4: "小さな噴石の落下",
        7: "その他の防災気象情報要素2",
        # "N*": "防災気象情報要素2(コード番号：N)",
    },
    undefined="防災気象情報要素2(コード番号：%d)"
)
