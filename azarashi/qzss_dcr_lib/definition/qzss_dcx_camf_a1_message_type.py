from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcx_camf_a1_message_type = QzssDcrDefinition(
    {
        1: 'Test',
        2: 'Alert',
        3: 'Update',
        4: 'All Clear',
    },
    undefined='Undefined Message Type (Code: %d)'
)