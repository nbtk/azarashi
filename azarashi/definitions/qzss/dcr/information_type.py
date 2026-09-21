from ...code_table import CodeTable

information_type = CodeTable(
    {
        0: '発表',
        1: '訂正',
        2: '取消',
    },
    undefined="情報形態(コード番号：%d)"
)

information_type_en = CodeTable(
    {
        0: 'Issue',
        1: 'Correction',
        2: 'Cancellation',
    },
    undefined="Undefined Information Type (Code: %d)"
)
