from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_flood_warning_level = QzssDcrDefinition(
    {
        1: "警報解除",
        2: "氾濫警戒情報",
        3: "氾濫危険情報",
        4: "氾濫発生情報",
        15: "その他の警戒レベル",
        # "NN*": "警戒レベル(コード番号：NN)",
    },
    undefined="警戒レベル(コード番号：%d)"
)
