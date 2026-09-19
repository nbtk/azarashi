from .dcr import QzssDcrDecoder
from .base import QzssDcrDecoderBase
from ..exceptions import AzarashiInvalidMessageError
from ..reports import QzssDcReport
from ..reports import QzssDcReportBase


class HexQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase
    sentence: str | bytes

    def decode(self) -> QzssDcReport:
        if not self.sentence:
            raise EOFError('Encountered EOF')

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
        return QzssDcrDecoder(**self.get_params()).decode()
