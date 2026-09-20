from ..reports import Report
from ..reports import base
from . import common
from .base import Base
from ..exceptions import AzarashiInvalidMessageError


class Decoder(Base):
    schema = base.Base
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise AzarashiInvalidMessageError('Empty Message')

        if not isinstance(self.sentence, (bytes, bytearray)):  # a datagram is bytes
            raise AzarashiInvalidMessageError(
                'Invalid Sentence',
                self)
        self.sentence = self.sentence.strip()

        if len(self.sentence) < 33:
            raise AzarashiInvalidMessageError(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 33:
            raise AzarashiInvalidMessageError(
                'Too Long Sentence',
                self)

        self.message = self.sentence[1:]

        # extracts a satellite id
        self.satellite_id = self.sentence[0]
        self.satellite_prn = self.satellite_id | 0x80

        # generates a nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return common.Decoder(**self.get_params()).decode()
