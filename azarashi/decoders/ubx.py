from ..reports import Report
from .qzss import l1s
from .qzss.base import InputDecoder
from ..definitions.ubx import RXM_SFRBX_HEADER
from ..definitions.qzss.ubx import svid_to_prn
from ..exceptions import AzarashiInvalidMessageError


class Decoder(InputDecoder):
    sentence: bytes

    def decode(self) -> Report:
        # extracts a message header, satellite id, and message
        self.message_header = self.sentence[:len(RXM_SFRBX_HEADER)]

        # checks the message header
        if self.message_header != RXM_SFRBX_HEADER:
            raise AzarashiInvalidMessageError(
                f'Unknown Message Header: {self.message_header!r}',
                self)

        if len(self.sentence) < len(RXM_SFRBX_HEADER) + 2 + 8 + 2:  # SFRBX + Length + fixed part + CHK
            raise AzarashiInvalidMessageError(
                'Too Short Sentence',
                self)

        # checks the fletcher's checksum
        sum_a = sum_b = 0
        for b in self.sentence[2: -2]:
            sum_a += b
            sum_b += sum_a
        sum_a &= 0xff
        sum_b &= 0xff
        if sum_a != self.sentence[-2] or sum_b != self.sentence[-1]:
            raise AzarashiInvalidMessageError(
                f'Checksum Mismatch: expected {sum_a:02X}{sum_b:02X}, but got {self.sentence[-2]:02X}{self.sentence[-1]:02X}',
                self)

        # checks the gnss id
        gnss_id = self.sentence[6]
        if gnss_id != 5:
            raise AzarashiInvalidMessageError(
                f'This Sentence is not from QZSS: {gnss_id}',
                self)

        # extracts the satellite id
        self.satellite_svid = self.sentence[7]
        self.satellite_prn = svid_to_prn.get(self.satellite_svid)  # None while it has no PRN number
        self.satellite_id = None if self.satellite_prn is None else self.satellite_prn & 0x3f  # the lower 6 bits

        # checks the signal id
        sig_id = self.sentence[8]
        if sig_id != 1:
            raise AzarashiInvalidMessageError(
                f'The Sentence is not an L1S Signal: {sig_id}',
                self)

        # checks the data size
        payload_length = len(self.sentence) - (len(RXM_SFRBX_HEADER) + 2 + 2)  # SFRBX + Length + CHK
        declared_length = int.from_bytes(self.sentence[4:6], 'little')
        if declared_length != payload_length:
            raise AzarashiInvalidMessageError(
                f'Payload Length Mismatch: declared {declared_length}, but got {payload_length}',
                self)
        num_data_word = self.sentence[10]
        if (num_data_word * 4 + 8 != payload_length
                or num_data_word < 8):  # the 250-bit message takes 8 data words
            raise AzarashiInvalidMessageError(
                f'Invalid Message Length: {num_data_word}',
                self)

        # extracts the dcr message
        data_offset = 14
        data = b''
        for i in range(num_data_word):
            data += bytes((self.sentence[data_offset + 3 + i * 4],
                           self.sentence[data_offset + 2 + i * 4],
                           self.sentence[data_offset + 1 + i * 4],
                           self.sentence[data_offset + 0 + i * 4]))
        self.message = data[:31] + bytes((data[31] & 0xC0,))

        # generates the nmea sentence
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return l1s.Decoder(
            sentence=self.sentence,
            message=self.message,
            nmea=self.nmea,
            timestamp=self.timestamp,
            message_header=self.message_header,
            satellite_id=self.satellite_id,
            satellite_prn=self.satellite_prn,
            satellite_svid=self.satellite_svid,
        ).decode()
