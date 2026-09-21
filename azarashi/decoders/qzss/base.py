from datetime import UTC, datetime
from typing import Any, ClassVar, Generic, TypeVar

from .context import Frame, Message

from ...reports import Report
from ...reports import base
from ...definitions.nmea import QZQSM_HEADER
from ...exceptions import AzarashiNotImplementedError


class Base:
    """Legacy schema-based entry for subclasses; built-in stages initialize typed inputs."""

    schema: ClassVar[type[base.Base]]  # checks the parameters and sets them as attributes
    message: bytes
    timestamp: datetime

    def __init__(self, sentence: str | bytes, **kwargs: Any) -> None:
        self.set_params(sentence=sentence, **kwargs)

    def decode(self) -> Report:
        raise AzarashiNotImplementedError('Decoder Not Implemented')

    def message_to_nmea(self) -> str:
        sat_id = getattr(self, 'satellite_id', None)
        if sat_id is None:
            sat_id = 55  # Set the satellite_id of PRN183 if it was default.

        nmea_partial = f'{QZQSM_HEADER},{sat_id},{self.message.hex()[:-1].upper()}'

        checksum = 0
        for c in nmea_partial[1:]:  # without the '$' at the beginning
            checksum ^= ord(c)

        return nmea_partial + '*%02X' % checksum

    def extract_field(self, slider: int, size: int) -> int:
        field = bytearray(self.message[slider >> 3:(slider + size >> 3) + 1])
        field[0] = field[0] & (2 ** (8 - (slider & 7)) - 1)
        return int.from_bytes(field, 'big') >> (8 - (slider + size & 7))

    def set_params(self, **kwargs: Any) -> None:
        self.__dict__.update(self.schema(**kwargs).get_params())

    def get_params(self) -> dict[str, Any]:
        return self.__dict__


class InputDecoder(Base):
    """Normalize reception time once, before parsing an input format."""

    def __init__(self, sentence: str | bytes, *, timestamp: datetime | None = None) -> None:
        self.sentence = sentence
        self.raw = b''
        self.timestamp = (datetime.now(UTC) if timestamp is None else timestamp).astimezone(UTC)


_Context = TypeVar('_Context', bound=Frame)


class ContextDecoder(Base, Generic[_Context]):
    """Read typed context without constructing or copying an intermediate report."""

    def __init__(self, context: _Context) -> None:
        self.context = context
        self.message = context.message
        self.timestamp = context.timestamp

    @property
    def sentence(self) -> str | bytes:
        return self.context.sentence

    @property
    def nmea(self) -> str:
        return self.context.nmea

    @property
    def message_header(self) -> str | bytes | None:
        return self.context.message_header

    @property
    def satellite_id(self) -> int | None:
        return self.context.satellite_id

    @property
    def satellite_prn(self) -> int | None:
        return self.context.satellite_prn

    @property
    def satellite_svid(self) -> int | None:
        return self.context.satellite_svid

    @property
    def raw(self) -> bytes:
        start = 3 if self.message[1] >> 2 == 44 else 1
        return self.message[start:27] + bytes((self.message[27] & 0xF0,))

    def get_params(self) -> dict[str, Any]:
        # The final public DCX constructor accepts sparse keyword fields. Keep this
        # compatibility adapter at the output boundary, never between decoders.
        return {'sentence': self.sentence, 'raw': self.raw, 'timestamp': self.timestamp,
                **self.context.params(),
                **{key: value for key, value in self.__dict__.items() if key != 'context'}}


class MessageDecoder(ContextDecoder[Message]):
    @property
    def preamble(self) -> str:
        return self.context.preamble

    @property
    def message_type(self) -> str:
        return self.context.message_type
