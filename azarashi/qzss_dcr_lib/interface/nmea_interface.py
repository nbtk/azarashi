from collections.abc import Callable
from typing import Any

from .stream_state import read_line
from ..definition import nmea_qzss_dcr_message_header


def nmea_qzss_dcr_message_extractor(reader: Callable[..., str | bytes],
                                    reader_args: tuple[Any, ...] | None = None,
                                    reader_kwargs: dict[str, Any] | None = None) -> str:
    if reader_args is None:
        reader_args = ()
    if reader_kwargs is None:
        reader_kwargs = {}
    while True:
        msg = read_line(reader, reader_args, reader_kwargs)
        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode(errors='replace')  # line noise must not stop the stream; the checksum rejects it
        start = msg.find(nmea_qzss_dcr_message_header)  # the sentence may follow noise on the same line
        if start >= 0:
            return msg[start:]
