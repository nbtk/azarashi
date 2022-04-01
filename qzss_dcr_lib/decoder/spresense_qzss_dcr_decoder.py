from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.decoder import QzssDcrDecoderBase
from qzss_dcr_lib.decoder import QzssDcrDecoder
from qzss_dcr_lib.report import QzssDcReportBase
from qzss_dcr_lib.definition import spresense_qzss_dcr_message_header


class SpresenseQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase

    def decode(self):
        if not self.sentence:
            raise EOFError('Encountered EOF')

        self.sentence = self.sentence.split()[0]

        if len(self.sentence) < 76:
            raise QzssDcrDecoderException(
                    'Too Short Sentence',
                    self.sentence)
        if len(self.sentence) > 76:
            raise QzssDcrDecoderException(
                    'Too Long Sentence',
                    self.sentence)

        # checks the checksum
        try:
            payload, csum = self.sentence.split('*')
        except:
            raise QzssDcrDecoderException(
                    'Checksum Not Found',
                    self.sentence)

        if len(csum) != 2:
            raise QzssDcrDecoderException(
                    'Invalid Checksum',
                    self.sentence)

        try:
            checksum = int(csum, 16)
        except:
            raise QzssDcrDecoderException(
                    'Invalid Checksum',
                    self.sentence)

        try:
            summed = 0
            for c in payload[1:]: # without the '$' at the beginning
                summed ^= ord(c)
        except:
            raise QzssDcrDecoderException(
                    'Invalid Sentence',
                    self.sentence)

        if summed != checksum:
            raise QzssDcrDecoderException(
                    'Checksum Mismatch',
                    self.sentence)

        # extracts a message header, satellite id, and message
        try:
            self.message_header, sat_id, message_str = payload.split(',')
        except:
            raise QzssDcrDecoderException(
                    'Invalid Sentence',
                    self.sentence)

        # checks the message headder
        if self.message_header != spresense_qzss_dcr_message_header:
            raise QzssDcrDecoderException(
                    f'Unknown Message Header: {self.message_header}',
                    self.sentence)

        # checks the satellite id
        if len(sat_id) != 2:
            raise QzssDcrDecoderException(
                    f'Invalid Satellite ID: {sat_id}',
                    self.sentence)
        self.satellite_id = int(sat_id, 16) + 100

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(message_str + '0') # padded with six 0s. the actual message size is 250 bits.
        except:
            raise QzssDcrDecoderException(
                    'Invalid Message',
                    self.sentence)

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
