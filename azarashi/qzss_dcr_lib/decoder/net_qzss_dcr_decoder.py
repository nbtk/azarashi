from .qzss_dcr_decoder import QzssDcrDecoder
from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReport
from ..report import QzssDcReportBase


class NetQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase
    sentence: str | bytes

    def decode(self) -> QzssDcReport:
        if not self.sentence:
            raise EOFError('Encountered EOF')

        if not isinstance(self.sentence, (bytes, bytearray)):  # a datagram is bytes
            raise QzssDcrDecoderException(
                'Invalid Sentence',
                self)
        self.sentence = self.sentence.strip()

        if len(self.sentence) < 33:
            raise QzssDcrDecoderException(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 33:
            raise QzssDcrDecoderException(
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
