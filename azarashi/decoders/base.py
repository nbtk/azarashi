from datetime import datetime
from typing import Any, ClassVar

from ..reports import Report
from ..reports import base
from ..definitions import nmea_qzss_dcr_message_header
from ..exceptions import AzarashiNotImplementedError


class Base:
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

        nmea_partial = f'{nmea_qzss_dcr_message_header},{sat_id},{self.message.hex()[:-1].upper()}'

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
