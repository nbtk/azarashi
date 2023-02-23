from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from .qzss_dcr_decoder import QzssDcrDecoder
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportBase


class HexQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase

    def decode(self):
        if not self.sentence:
            raise EOFError('Encountered EOF')

        self.sentence = self.sentence.split()[0]

        if len(self.sentence) < 63:
            raise QzssDcrDecoderException(
                    'Too Short Sentence',
                    self.sentence)
        if len(self.sentence) > 63:
            raise QzssDcrDecoderException(
                    'Too Long Sentence',
                    self.sentence)

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(self.sentence+'0')
        except ValueError:
            raise QzssDcrDecoderException(
                    'Invalid Message',
                    self.sentence)

        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
