import struct
from collections.abc import Callable
from typing import Any

from .state import ReaderStore
from .state import empty_read_error
from .state import read_stream
from ..exceptions import AzarashiReopenStream
from ..exceptions import AzarashiStopReading
from ..exceptions import AzarashiTimeoutError
from ..definitions import qzss_dcr_message_type
from ..definitions import ublox_qzss_dcr_message_header

buffers: ReaderStore[bytearray] = ReaderStore(bytearray)  # unread bytes per reader; retention follows ReaderStore
#: a read that did not deliver: what was read is kept, so a later call resumes from it. A stream
#: that failed is not here, because the bytes it gave are half of a frame that can never arrive.
INCOMPLETE = (AzarashiTimeoutError, AzarashiStopReading)


def __pop(size: int,
          buf: bytearray,
          reader: Callable[..., bytes | None],
          reader_args: tuple[Any, ...]) -> bytes:
    while size > len(buf):
        try:
            data = read_stream(reader, reader_args)
        except AzarashiReopenStream:
            buf.clear()  # the rest of the frame can never arrive, and the bytes read are half of one
            raise
        if not data:
            raise empty_read_error(reader)
        buf += data

    ret = bytes(buf[:size])
    del buf[:size]

    return ret


def _is_sfrbx_payload_length(length: int) -> bool:
    return 8 <= length <= 8 + 4 * 255 and length % 4 == 0  # fixed part + numWords (U1) data words


def _is_checksum_valid(message: bytes) -> bool:
    ck_a = ck_b = 0
    for b in message[2:-2]:
        ck_a = (ck_a + b) & 0xff
        ck_b = (ck_b + ck_a) & 0xff
    return ck_a == message[-2] and ck_b == message[-1]


def ublox_qzss_dcr_message_extractor(reader: Callable[..., bytes | None],
                                     reader_args: tuple[Any, ...] | None = None) -> bytes:
    if reader_args is None:
        reader_args = ()

    header = ublox_qzss_dcr_message_header
    buf = buffers.get(reader)
    match_count = 0
    while True:
        try:
            byte = __pop(1, buf, reader, reader_args)[0]
        except INCOMPLETE:
            buf[:0] = header[:match_count]  # a later call resumes from the partial header
            raise
        if header[match_count] == byte:
            match_count += 1
        elif header[0] == byte:  # the mismatched byte may start a new header
            match_count = 1
        else:
            match_count = 0

        if match_count == len(header): # SFRBX message
            match_count = 0
            try:
                message_length_bytes = __pop(2, buf, reader, reader_args)
            except INCOMPLETE:
                buf[:0] = header
                raise
            message_length = struct.unpack('<H', message_length_bytes)[0]
            if not _is_sfrbx_payload_length(message_length):  # a false header: rescan the bytes after it
                buf[:0] = message_length_bytes
                continue

            try:
                payload = __pop(message_length + 2,  # payload + CK_A + CK_B
                                buf, reader, reader_args)
            except INCOMPLETE:
                if header in message_length_bytes + buf:  # another header follows: this one was a false header
                    buf[:0] = message_length_bytes
                    continue
                buf[:0] = header + message_length_bytes  # a later call resumes this message
                raise
            message = header + message_length_bytes + payload

            if not _is_checksum_valid(message):
                # the length itself may be corrupted: rescan these bytes rather than dropping what follows.
                # a message that still looks like a DCR message is returned so that the decoder reports it.
                buf[:0] = message[len(header):]

            if message_length < 12:  # no data word
                continue

            if message[6] != 5:  # not sent by QZSS
                continue

            if message[8] != 1:  # not a L1S signal
                continue

            if message[16] >> 2 not in qzss_dcr_message_type.keys():
                continue

            return message
