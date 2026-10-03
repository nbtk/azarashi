from datetime import datetime

from ...reports import Report
from .base import ContextDecoder
from .context import Frame, Message
from . import dcr
from . import dcx
from ...definitions.qzss.l1s import message_types
from ...definitions.qzss.l1s import preambles
from ...definitions.nmea import QZQSM_HEADER
from ...exceptions import AzarashiInvalidMessageError


class Decoder(ContextDecoder[Frame]):
    def __init__(self, sentence: str | bytes, *, message: bytes,
                 timestamp: datetime, message_header: str | bytes | None = None,
                 satellite_id: int | None = None, satellite_prn: int | None = None,
                 satellite_svid: int | None = None) -> None:
        super().__init__(Frame(sentence=sentence, message=message, timestamp=timestamp,
                              message_header=message_header, satellite_id=satellite_id,
                              satellite_prn=satellite_prn, satellite_svid=satellite_svid))

    def decode(self) -> Report:
        # extracts the preamble
        self.preamble = preambles[self.extract_field(0, 8)]

        # checks the crc
        crc = 0
        crc_remaining_len = 226
        data = self.context.message[:28] + bytes((self.context.message[28] & 0xC0,))  # clears the last 6 bits
        for byte in data:
            crc ^= (byte << 16)
            for _ in range(8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= 0x1864cfb  # polynomial
                crc_remaining_len -= 1
                if crc_remaining_len == 0:
                    break
        crc &= 0xffffff
        transmitted = self.extract_field(226, 24)
        if crc != transmitted:
            raise AzarashiInvalidMessageError(
                f'CRC Mismatch: expected {crc:06X}, but got {transmitted:06X}',
                self)

        # checks the message type
        mt = self.extract_field(8, 6)  # 6 bits
        try:
            self.message_type = message_types[mt]
        except KeyError as err:
            raise AzarashiInvalidMessageError(
                f'Undefined Message Type: {mt}',
                self) from err

        next_decoder: type[ContextDecoder[Message]]
        if mt == 43:
            next_decoder = dcr.Decoder
        elif mt == 44:
            next_decoder = dcx.Decoder
        else:
            raise AzarashiInvalidMessageError(
                f'Unsupported Message Type: {mt}',
                self)

        # stacks the next decoder
        return next_decoder(Message(**self.context.params(), nmea=self._nmea(),
                                    preamble=self.preamble, message_type=self.message_type)).decode()

    def _nmea(self) -> str:
        sat_id = self.context.satellite_id
        if sat_id is None:
            sat_id = 55  # Set the satellite_id of PRN183 if it was default.

        nmea_partial = f'{QZQSM_HEADER},{sat_id},{self.context.message.hex()[:-1].upper()}'

        checksum = 0
        for c in nmea_partial[1:]:  # without the '$' at the beginning
            checksum ^= ord(c)

        return nmea_partial + '*%02X' % checksum
