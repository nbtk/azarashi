from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from .qzss_dcr_decoder import QzssDcrDecoder
from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.report import QzssDcReportBase


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
        except:
            raise QzssDcrDecoderException(
                    'Invalid Message',
                    self.sentence)

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
