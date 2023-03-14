from ..exception import QzssDcrDecoderException
from ..decoder import QzssDcrDecoderBase
from ..decoder import QzssDcrDecoder
from ..report import QzssDcReportBase
from ..definition import ublox_qzss_dcr_message_header
from ..definition import qzss_dcr_satellite_prn


class UBloxQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase

    def decode(self):
        if len(self.sentence) < 52:
            raise QzssDcrDecoderException(
                    'Too Short Sentence',
                    self)
        if len(self.sentence) > 52:
            raise QzssDcrDecoderException(
                    'Too Long Sentence',
                    self)

        # extracts a message header, satellite id, and message
        self.message_header = self.sentence[:len(ublox_qzss_dcr_message_header)]

        # checks the message header
        if self.message_header != ublox_qzss_dcr_message_header:
            raise QzssDcrDecoderException(
                    f'Unknown Message Header: {self.message_header}',
                    self)

        # checks the gnss id
        gnss_id = self.sentence[6]
        if gnss_id != 5:
            raise QzssDcrDecoderException(
                    f'This Sentence is not from QZSS: {gnss_id}',
                    self)

        # extracts a satellite id
        self.satellite_id = self.sentence[7] + 51
        self.satellite_prn = self.satellite_id | 0x80

        # checks the signal id
        sig_id = self.sentence[8]
        if sig_id != 1:
            raise QzssDcrDecoderException(
                    f'The Sentence is not an L1S Signal: {sig_id}',
                    self)

        # checks the data size
        num_data_word = self.sentence[10]
        if num_data_word != 9:
            raise QzssDcrDecoderException(
                    f'Invalid Message Length: {num_data_word}',
                    self)

        # extracts a dcr message
        data_offset = 14
        data = b''
        for i in range(num_data_word):
            data += bytes((self.sentence[data_offset+3+i*4],
                           self.sentence[data_offset+2+i*4],
                           self.sentence[data_offset+1+i*4],
                           self.sentence[data_offset+0+i*4]))
        self.message = data[:31] + bytes((data[31] & 0xC0,))

        # generates a nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
