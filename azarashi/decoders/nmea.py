from ..reports import Report
from . import common
from .base import InputDecoder
from ..definitions import nmea_qzss_dcr_message_header
from ..exceptions import AzarashiInvalidMessageError


class Decoder(InputDecoder):
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise AzarashiInvalidMessageError('Empty Message')

        sentence = self.sentence
        if isinstance(sentence, (bytes, bytearray)):  # a line read as bytes, as from pySerial
            sentence = sentence.decode(errors='replace')
        words = sentence.split()
        self.sentence = words[0] if words else ''  # a blank line is too short

        if len(self.sentence) < 76:
            raise AzarashiInvalidMessageError(
                'Too Short Sentence',
                self)
        if len(self.sentence) > 76:
            raise AzarashiInvalidMessageError(
                'Too Long Sentence',
                self)

        # checks the checksum
        try:
            payload, csum = self.sentence.split('*')
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Checksum Not Found',
                self) from err

        if len(csum) != 2:
            raise AzarashiInvalidMessageError(
                'Invalid Checksum Length',
                self)

        try:
            checksum = int(csum, 16)
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Invalid Checksum',
                self) from err

        summed = 0
        for c in payload[1:]:  # without the '$' at the beginning
            summed ^= ord(c)

        if summed != checksum:
            raise AzarashiInvalidMessageError(
                'Checksum Mismatch, should be %02X' % summed,
                self)

        # extracts a message header, satellite id, and message
        try:
            self.message_header, sat_id, message_str = payload.split(',')
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Invalid Sentence',
                self) from err

        # checks the message header
        if self.message_header != nmea_qzss_dcr_message_header:
            raise AzarashiInvalidMessageError(
                f'Unknown Message Header: {self.message_header}',
                self)

        # checks the satellite id
        if len(sat_id) != 2 or not (sat_id.isascii() and sat_id.isdigit()):
            raise AzarashiInvalidMessageError(
                f'Invalid Satellite ID: {sat_id}',
                self)
        self.satellite_id = int(sat_id)
        self.satellite_prn = self.satellite_id | 0x80

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(message_str + '0')  # padded with six 0s. the actual message size is 250 bits.
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Invalid Message',
                self) from err

        # generates a nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return common.Decoder(
            sentence=self.sentence,
            message=self.message,
            nmea=self.nmea,
            timestamp=self.timestamp,
            message_header=self.message_header,
            satellite_id=self.satellite_id,
            satellite_prn=self.satellite_prn,
        ).decode()
