from ..code_table import CodeTable

a1_message_type = CodeTable(
    {
        0: 'Test',
        1: 'Alert',
        2: 'Update',
        3: 'All Clear',
    },
    undefined='Undefined Message Type (Code: %d)'
)
