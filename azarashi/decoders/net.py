from ..reports import Report
from ..reports import base
from .common import QzssDcrDecoder
from .base import QzssDcrDecoderBase
from ..exceptions import AzarashiInvalidMessageError


class NetQzssDcrDecoder(QzssDcrDecoderBase):
    schema = base.Base
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise EOFError('Encountered EOF')

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
        return QzssDcrDecoder(**self.get_params()).decode()
