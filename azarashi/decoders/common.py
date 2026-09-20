from datetime import datetime

from ..reports import Report
from ..reports import base
from .base import Base
from . import dcr
from . import dcx
from ..definitions import qzss_dcr_message_type
from ..definitions import qzss_dcr_preamble
from ..exceptions import AzarashiInvalidMessageError


class Decoder(Base):
    schema = base.MessagePartial

    def __init__(self, sentence: str | bytes, *, message: bytes, nmea: str,
                 timestamp: datetime, message_header: str | bytes | None = None,
                 satellite_id: int | None = None, satellite_prn: int | None = None,
                 satellite_svid: int | None = None) -> None:
        super().__init__(sentence, message=message, nmea=nmea, timestamp=timestamp,
                         message_header=message_header, satellite_id=satellite_id,
                         satellite_prn=satellite_prn, satellite_svid=satellite_svid)

    def decode(self) -> Report:
        # extracts the preamble
        self.preamble = qzss_dcr_preamble[self.extract_field(0, 8)]

        # checks the crc
        crc = 0
        crc_remaining_len = 226
        data = self.message[:28] + bytes((self.message[28] & 0xC0,))  # clears the last 6 bits
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
        if crc != self.extract_field(226, 24):
            raise AzarashiInvalidMessageError(
                'CRC Mismatch',
                self)

        # checks the message type
        mt = self.extract_field(8, 6)  # 6 bits
        try:
            self.message_type = qzss_dcr_message_type[mt]
        except KeyError as err:
            raise AzarashiInvalidMessageError(
                f'Undefined Message Type: {mt}',
                self) from err

        next_decoder: type[Base]
        if mt == 43:
            next_decoder = dcr.Decoder
        elif mt == 44:
            next_decoder = dcx.Decoder
        else:
            raise AzarashiInvalidMessageError(
                f'Unsupported Message Type: {mt}',
                self)

        # stacks the next decoder
        return next_decoder(**self.get_params()).decode()
