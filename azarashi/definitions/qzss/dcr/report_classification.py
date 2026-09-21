from ...code_table import CodeTable

report_classification = CodeTable(
    {
        1: "最優先",
        2: "優先",
        3: "通常",
        7: "訓練/試験",
    },
    undefined="通報区分(コード番号：%d)"
)

report_classification_en = CodeTable(
    {
        1: "Maximum Priority",
        2: "Priority",
        3: "Regular",
        7: "Training/Test",
    },
    undefined="Undefined Report Classification (Code: %d)"
)
