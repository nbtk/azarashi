from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from .qzss_dcr_decoder_jma import QzssDcrDecoderJma
from .qzss_dcr_decoder_other_organization import QzssDcrDecoderOtherOrganization
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportMessagePartial
from ..definition import qzss_dcr_preamble
from ..definition import qzss_dcr_message_type
from ..definition import qzss_dcr_report_classification
from ..definition import qzss_dcr_report_classification_en


class QzssDcrDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportMessagePartial

    def decode(self):
        # checks the preamble
        pab = self.extract_field(0, 8)
        try:
            self.preamble = qzss_dcr_preamble[pab]
        except:
            raise QzssDcrDecoderException(
                    f'Invalid Preamble: {pab}',
                    self.sentence)

        # checks the crc
        crc = 0
        crc_remaining_len = 226
        data = self.message[:28] + bytes((self.message[28] & 0xC0,)) # clears the last 6 bits
        for byte in data:
            crc ^= (byte << 16)
            for _ in range(8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= 0x1864cfb # polynomial
                crc_remaining_len -= 1
                if crc_remaining_len == 0:
                    break
        crc &= 0xffffff
        if crc != self.extract_field(226, 24):
            raise QzssDcrDecoderException(
                    'CRC Mismatch',
                    self.sentence)

        # checks the message type
        mt = self.extract_field(8, 6) # 6 bits
        try:
            self.message_type = qzss_dcr_message_type[mt]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined Message Type: {mt}',
                    self.sentence)

        if mt == 43:
            next_decoder = QzssDcrDecoderJma
        elif mt == 44:
            next_decoder = QzssDcrDecoderOtherOrganization
        else:
            raise QzssDcrDecoderException(
                    f'Unsupported Message Type: {mt}',
                    self.sentence)

        rc = self.extract_field(14, 3)
        try:
            self.report_classification = qzss_dcr_report_classification[rc]
            self.report_classification_en = qzss_dcr_report_classification_en[rc]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined Report Classification: {rc}',
                    self.sentence)
        self.report_classification_no = rc

        # stacks the next decoder
        return next_decoder(**self.get_params()).decode()
