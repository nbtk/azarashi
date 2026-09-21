from ...code_table import CodeTable
import enum


class MessageType(enum.Enum):
    NULL_MSG = 0
    OUTSIDE_JAPAN = 1
    L_ALERT = 2
    J_ALERT = 3
    LOCAL_GOV = 4
    UNKNOWN = 5


message_type = CodeTable(
    {
        MessageType.NULL_MSG: 'Null Message',
        MessageType.OUTSIDE_JAPAN: 'Information from Organizations outside Japan',
        MessageType.L_ALERT: 'L-Alert',
        MessageType.J_ALERT: 'J-Alert',
        MessageType.LOCAL_GOV: 'Information from Local Government',
        MessageType.UNKNOWN: 'Unknown DCX Message Type',
    },
    undefined='Undefined Message Type (Code: %d)'
)
