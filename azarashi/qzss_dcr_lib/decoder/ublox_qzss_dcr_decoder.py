from ..decoder import QzssDcrDecoder
from ..decoder import QzssDcrDecoderBase
from ..definition import ublox_qzss_dcr_message_header
from ..definition import ublox_qzss_svn_prn_map
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportBase


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

        # checks the fletcher's checksum
        sum_a = sum_b = 0
        for b in self.sentence[2: -2]:
            sum_a += b
            sum_b += sum_a
        sum_a &= 0xff
        sum_b &= 0xff
        if sum_a != self.sentence[-2] or sum_b != self.sentence[-1]:
            raise QzssDcrDecoderException(
                'Checksum Mismatch',
                self)

        # checks the gnss id
        gnss_id = self.sentence[6]
        if gnss_id != 5:
            raise QzssDcrDecoderException(
                f'This Sentence is not from QZSS: {gnss_id}',
                self)

        # extracts a satellite id
        self.satellite_prn = ublox_qzss_svn_prn_map.get(self.sentence[7])
        if self.satellite_prn is None:
            self.satellite_id = None
        else:
            # 2. PRNの下位6ビットからSatellite IDを計算
            # 0x3F は二進数で 00111111 となり、これとのAND演算で下位6ビットのみが残る
            self.satellite_id = self.satellite_prn & 0x3F

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
            data += bytes((self.sentence[data_offset + 3 + i * 4],
                           self.sentence[data_offset + 2 + i * 4],
                           self.sentence[data_offset + 1 + i * 4],
                           self.sentence[data_offset + 0 + i * 4]))
        self.message = data[:31] + bytes((data[31] & 0xC0,))

        # generates a nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return QzssDcrDecoder(**self.get_params()).decode()
