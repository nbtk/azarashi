from .qzss_dcr_decoder import QzssDcrDecoder
from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReport
from ..report import QzssDcReportBase


class HexQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase
    sentence: str

    def decode(self) -> QzssDcReport:
        if not self.sentence:
            raise EOFError('Encountered EOF')

        self.sentence = self.sentence.strip()

        if len(self.sentence) < 63:
            raise QzssDcrDecoderException(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 63:
            raise QzssDcrDecoderException(
                'Too Long Sentence',
                self)

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(self.sentence + '0')
        except ValueError as err:
            raise QzssDcrDecoderException(
                'Invalid Message',
                self) from err
        if len(self.message) != 32:  # bytes.fromhex() skips whitespace between the bytes
            raise QzssDcrDecoderException(
                'Invalid Message',
                self)

        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
