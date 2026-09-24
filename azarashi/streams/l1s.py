"""The QZSS L1S archive: a byte of PRN, then for each second four bytes of GPS time and the message.

The time is the GPS week in its upper 12 bits and the second of the week in its lower 20. The
message is the 250-bit L1S message in 32 bytes. Records whose message is not a DCR or DCX message,
such as the augmentation messages, are passed over here.

A record is in step when its time follows the time of the record before it. The preamble is not
used for this, as a later edition may add patterns. When a byte is lost or added, the records
after it are out of step: one error is raised, and the archive is read on from the next record
that is in step again.
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .state import ReaderStore
from .state import pop_bytes
from ..definitions.gps import SECONDS_PER_WEEK
from ..definitions.qzss.l1s import message_types
from ..exceptions import AzarashiInvalidMessageError

__all__ = ['l1s_qzss_dcr_message_extractor']

RECORD = 4 + 32  # GPS time + message
STEP = 24 * 3600  # the longest step from a record to the next: an archive holds a day


@dataclass
class _Archive:
    prn: int | None = None  # read from the head of the archive
    time: int | None = None  # the GPS time, in seconds, of the last record in step
    in_step: bool = True


buffers: ReaderStore[bytearray] = ReaderStore(bytearray)  # unread bytes per reader; retention follows ReaderStore
archives: ReaderStore[_Archive] = ReaderStore(_Archive)  # what is read of the archive so far



def l1s_qzss_dcr_message_extractor(reader: Callable[..., bytes | None],
                                   reader_args: tuple[Any, ...] | None = None) -> bytes:
    """The next record that carries a DCR or DCX message, after the archive's PRN."""
    if reader_args is None:
        reader_args = ()

    buf = buffers.get(reader)
    archive = archives.get(reader)
    if archive.prn is None:
        archive.prn = pop_bytes(1, buf, reader, reader_args, 'l1s')[0]
    while True:
        record = pop_bytes(RECORD, buf, reader, reader_args, 'l1s')
        time = int.from_bytes(record[:4], 'big')
        week, second = time >> 20, time & 0xFFFFF
        if archive.time is not None:
            if not (second < SECONDS_PER_WEEK and 0 < week * SECONDS_PER_WEEK + second - archive.time <= STEP):
                buf[:0] = record[1:]  # look for a record in step from the next byte
                if archive.in_step:
                    archive.in_step = False
                    last_week, last_second = divmod(archive.time, SECONDS_PER_WEEK)
                    raise AzarashiInvalidMessageError(
                        f'Record Out of Step After GPS Week {last_week} Second {last_second}')
                continue
            archive.in_step = True
        if second < SECONDS_PER_WEEK:  # the decoder reports a second past the week
            archive.time = week * SECONDS_PER_WEEK + second
        if record[5] >> 2 in message_types.keys():  # the message type, after the 8-bit preamble
            return bytes((archive.prn,)) + record
