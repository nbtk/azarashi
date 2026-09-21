from collections.abc import Callable
from typing import Any

from .state import ReaderStore
from .state import read_line
from ..definitions.nmea import QZQSM_HEADER

_pending_sentences: ReaderStore[list[str]] = ReaderStore(list)  # the sentences of a line not handed out yet


def nmea_qzss_dcr_message_extractor(reader: Callable[..., str | bytes],
                                    reader_args: tuple[Any, ...] | None = None) -> str:
    if reader_args is None:
        reader_args = ()
    header = QZQSM_HEADER
    pending = _pending_sentences.get(reader)
    while not pending:
        msg = read_line(reader, reader_args)
        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode(errors='replace')  # line noise must not stop the stream; the checksum rejects it
        start = msg.find(header)  # the sentence may follow noise on the same line
        if start >= 0:
            # a lost newline puts several sentences on one line: each is handed out, so a cut one loses no other
            pending.extend(header + part for part in msg[start + len(header):].split(header))
    return pending.pop(0)


def reset_pending_sentences(reader: Callable[..., Any]) -> None:
    _pending_sentences.discard(reader)
