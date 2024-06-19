import enum
from .qzss_dcr_definition import QzssDcrDefinition


class DcxMessageType(enum.Enum):
    OUTSIDE_JAPAN = 0
    L_ALERT = 1
    J_ALERT = 2
    MT_INFO = 3
    UNKNOWN = 4


qzss_dcx_message_type = QzssDcrDefinition(
    {
        DcxMessageType.OUTSIDE_JAPAN: 'Information from Organizations outside Japan',
        DcxMessageType.L_ALERT: 'L-Alert',
        DcxMessageType.J_ALERT: 'J-Alert',
        DcxMessageType.MT_INFO: 'Municipality-Transmitted Information',
        DcxMessageType.UNKNOWN: 'Unknown DCX Message Type',
    },
    undefined='Undefined Message Type (Code: %d)'
)