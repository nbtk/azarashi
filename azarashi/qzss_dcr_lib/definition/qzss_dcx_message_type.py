import enum
from .qzss_dcr_definition import QzssDcrDefinition


class DcxMessageType(enum.Enum):
    NULL_MSG = 0
    OUTSIDE_JAPAN = 1
    L_ALERT = 2
    J_ALERT = 3
    MT_INFO = 4
    UNKNOWN = 5


qzss_dcx_message_type = QzssDcrDefinition(
    {
        DcxMessageType.NULL_MSG: 'Null Message',
        DcxMessageType.OUTSIDE_JAPAN: 'Information from Organizations outside Japan',
        DcxMessageType.L_ALERT: 'L-Alert',
        DcxMessageType.J_ALERT: 'J-Alert',
        DcxMessageType.MT_INFO: 'Municipality-Transmitted Information',
        DcxMessageType.UNKNOWN: 'Unknown DCX Message Type',
    },
    undefined='Undefined Message Type (Code: %d)'
)