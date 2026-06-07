from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcx_camf_a1_message_type = QzssDcrDefinition(
    {
        0: 'Test',
        1: 'Alert',
        2: 'Update',
        3: 'All Clear',
    },
    undefined='Undefined Message Type (Code: %d)'
)