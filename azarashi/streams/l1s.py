"""The QZSS L1S archive: a byte of PRN, then for each second four bytes of GPS time and the message.

The time is the GPS week in its upper 12 bits and the second of the week in its lower 20. The
message is the 250-bit L1S message in 32 bytes. Records whose message is not a DCR or DCX message,
such as the augmentation messages, are passed over here.
"""
from collections.abc import Callable
from typing import Any

from .state import ReaderStore
from .state import pop_bytes
from ..definitions.qzss.l1s import message_types

__all__ = ['l1s_qzss_dcr_message_extractor']

RECORD = 4 + 32  # GPS time + message
buffers: ReaderStore[bytearray] = ReaderStore(bytearray)  # unread bytes per reader; retention follows ReaderStore
prns: ReaderStore[bytearray] = ReaderStore(bytearray)  # the archive's PRN once it is read, empty before



def l1s_qzss_dcr_message_extractor(reader: Callable[..., bytes | None],
                                   reader_args: tuple[Any, ...] | None = None) -> bytes:
    """The next record that carries a DCR or DCX message, after the archive's PRN."""
    if reader_args is None:
        reader_args = ()

    buf = buffers.get(reader)
    prn = prns.get(reader)
    if not prn:
        prn += pop_bytes(1, buf, reader, reader_args, 'l1s')
    while True:
        record = pop_bytes(RECORD, buf, reader, reader_args, 'l1s')
        if record[5] >> 2 in message_types.keys():  # the message type, after the 8-bit preamble
            return bytes(prn) + record
