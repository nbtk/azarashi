from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_report_classification = QzssDcrDefinition(
    {
        1: "最優先",
        2: "優先",
        3: "通常",
        7: "訓練/試験",
    },
    undefined="通報区分(コード番号：%d)"
)

qzss_dcr_report_classification_en = QzssDcrDefinition(
    {
        1: "Maximum Priority",
        2: "Priority",
        3: "Regular",
        7: "Training/Test",
    },
    undefined="Report Classification (Code:%d)"
)
