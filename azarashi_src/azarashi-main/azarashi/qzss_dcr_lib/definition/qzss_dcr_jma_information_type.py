from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_information_type = QzssDcrDefinition(
    {
        0: '発表',
        1: '訂正',
        2: '取消',
    },
    undefined="情報形態(コード番号：%d)"
)

qzss_dcr_jma_information_type_en = QzssDcrDefinition(
    {
        0: 'Issue',
        1: 'Correction',
        2: 'Cancellation',
    },
    undefined="Undefined Information Type (Code: %d)"
)
