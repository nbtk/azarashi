from ..reports import Report
from . import common
from .base import InputDecoder
from ..exceptions import AzarashiInvalidMessageError


class Decoder(InputDecoder):
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise AzarashiInvalidMessageError('Empty Message')

        sentence = self.sentence
        if isinstance(sentence, (bytes, bytearray)):  # a line read as bytes, as from pySerial
            sentence = sentence.decode(errors='replace')
        self.sentence = sentence.strip()

        if len(self.sentence) < 63:
            raise AzarashiInvalidMessageError(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 63:
            raise AzarashiInvalidMessageError(
                'Too Long Sentence',
                self)

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(self.sentence + '0')
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Invalid Message',
                self) from err
        if len(self.message) != 32:  # bytes.fromhex() skips whitespace between the bytes
            raise AzarashiInvalidMessageError(
                'Invalid Message',
                self)

        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return common.Decoder(
            sentence=self.sentence,
            message=self.message,
            nmea=self.nmea,
            timestamp=self.timestamp,
        ).decode()
