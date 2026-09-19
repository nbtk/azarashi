from collections.abc import Callable
from typing import Any

from .state import read_line


def hex_qzss_dcr_message_extractor(reader: Callable[..., str | bytes],
                                   reader_args: tuple[Any, ...] | None = None,
                                   reader_kwargs: dict[str, Any] | None = None) -> str:
    if reader_args is None:
        reader_args = ()
    if reader_kwargs is None:
        reader_kwargs = {}
    msg = read_line(reader, reader_args, reader_kwargs)
    if isinstance(msg, (bytes, bytearray)):
        msg = msg.decode(errors='replace')  # line noise must not stop the stream; the decoder rejects it
    return msg
