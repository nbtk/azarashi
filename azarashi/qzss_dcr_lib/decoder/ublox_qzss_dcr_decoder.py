from ..exception import QzssDcrDecoderException
from ..decoder import QzssDcrDecoderBase
from ..decoder import QzssDcrDecoder
from ..report import QzssDcReportBase
from ..definition import ublox_qzss_dcr_message_header


class UBloxQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase

    def decode(self):
        if len(self.sentence) < 52:
            raise QzssDcrDecoderException(
                    'Too Short Sentence',
                    self.sentence)
        if len(self.sentence) > 52:
            raise QzssDcrDecoderException(
                    'Too Long Sentence',
                    self.sentence)

        #TODO Check csum!

        # extracts a message header, satellite id, and message
        self.message_header = self.sentence[:len(ublox_qzss_dcr_message_header)]

        # checks the message headder
        if self.message_header != ublox_qzss_dcr_message_header:
            raise QzssDcrDecoderException(
                    f'Unknown Message Header: {self.message_header}',
                    self.sentence)

        # checks the gnss id
        gnss_id = self.sentence[6]
        if gnss_id != 5:
            raise QzssDcrDecoderException(
                    f'This Sentence is not from QZSS: {gnss_id}',
                    self.sentence)

        # extracts a satellite id
        self.satellite_id = self.sentence[7] + 182

        # checks the signal id
        sig_id = self.sentence[8]
        if sig_id != 1:
            raise QzssDcrDecoderException(
                    f'The Sentence is not an L1S Signal: {sig_id}',
                    self.sentence)

        # checks the data size
        num_data_word = self.sentence[10]
        if num_data_word != 9:
            raise QzssDcrDecoderException(
                    f'Invalid Message Length: {num_data_word}',
                    self.sentence)

        # extracts a dcr message
        data_offset = 14
        data = bytearray()
        for i in range(num_data_word):
            data += bytearray([self.sentence[data_offset+3+i*4],
                               self.sentence[data_offset+2+i*4],
                               self.sentence[data_offset+1+i*4],
                               self.sentence[data_offset+0+i*4]])
        data = data[:32]
        data[31] &= 0xC0
        self.message = bytes(data)

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
