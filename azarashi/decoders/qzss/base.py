from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from .context import Frame, Message
from ...reports import Report
from ...exceptions import AzarashiNotImplementedError


class InputDecoder:
    """Mutable input parsing state with one normalized reception timestamp."""

    message: bytes

    def __init__(self, sentence: str | bytes, *, timestamp: datetime | None = None) -> None:
        self.sentence = sentence
        self.raw = b''
        self.timestamp = (datetime.now(UTC) if timestamp is None else timestamp).astimezone(UTC)


_Context = TypeVar('_Context', bound=Frame)


class ContextDecoder(Generic[_Context]):
    """Decode a typed context; expose the source sentence for exception diagnostics."""

    def __init__(self, context: _Context) -> None:
        self.context = context

    def decode(self) -> Report:
        raise AzarashiNotImplementedError('Decoder Not Implemented')

    @property
    def sentence(self) -> str | bytes:
        return self.context.sentence

    @property
    def nmea(self) -> str:
        return self.context.nmea if isinstance(self.context, Message) else ''  # a DCR or DCX message only

    def extract_field(self, slider: int, size: int) -> int:
        field = bytearray(self.context.message[slider >> 3:(slider + size >> 3) + 1])
        field[0] = field[0] & (2 ** (8 - (slider & 7)) - 1)
        return int.from_bytes(field, 'big') >> (8 - (slider + size & 7))

    @property
    def raw(self) -> bytes:
        start = 3 if self.context.message[1] >> 2 == 44 else 1
        return self.context.message[start:27] + bytes((self.context.message[27] & 0xF0,))

    def get_params(self) -> dict[str, Any]:
        # Sparse keyword fields preserve the public DCX constructor's optional attributes.
        return {**self.context.params(),
                **{key: value for key, value in self.__dict__.items() if key != 'context'}}
