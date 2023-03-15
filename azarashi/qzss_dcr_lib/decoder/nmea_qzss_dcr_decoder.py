from ..exception import QzssDcrDecoderException
from ..decoder import QzssDcrDecoderBase
from ..decoder import QzssDcrDecoder
from ..report import QzssDcReportBase
from ..definition import nmea_qzss_dcr_message_header


class NmeaQzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportBase

    def decode(self):
        if not self.sentence:
            raise EOFError('Encountered EOF')

        self.sentence = self.sentence.split()[0]

        if len(self.sentence) < 76:
            raise QzssDcrDecoderException(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 76:
            raise QzssDcrDecoderException(
                'Too Long Sentence',
                self)

        # checks the checksum
        try:
            payload, csum = self.sentence.split('*')
        except ValueError:
            raise QzssDcrDecoderException(
                'Checksum Not Found',
                self)

        if len(csum) != 2:
            raise QzssDcrDecoderException(
                'Invalid Checksum Length',
                self)

        try:
            checksum = int(csum, 16)
        except ValueError:
            raise QzssDcrDecoderException(
                'Invalid Checksum',
                self)

        summed = 0
        for c in payload[1:]:  # without the '$' at the beginning
            summed ^= ord(c)

        if summed != checksum:
            raise QzssDcrDecoderException(
                'Checksum Mismatch',
                self)

        # extracts a message header, satellite id, and message
        try:
            self.message_header, sat_id, message_str = payload.split(',')
        except ValueError:
            raise QzssDcrDecoderException(
                'Invalid Sentence',
                self)

        # checks the message header
        if self.message_header != nmea_qzss_dcr_message_header:
            raise QzssDcrDecoderException(
                f'Unknown Message Header: {self.message_header}',
                self)

        # checks the satellite id
        if len(sat_id) != 2:
            raise QzssDcrDecoderException(
                f'Invalid Satellite ID: {sat_id}',
                self)
        self.satellite_id = int(sat_id)
        self.satellite_prn = self.satellite_id | 0x80

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(message_str + '0')  # padded with six 0s. the actual message size is 250 bits.
        except ValueError:
            raise QzssDcrDecoderException(
                'Invalid Message',
                self)

        # generates a nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
