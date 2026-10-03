from ..reports import Report
from .qzss import l1s
from .qzss.base import InputDecoder
from ..definitions.ubx import RXM_SFRBX_HEADER
from ..definitions.qzss.ubx import GNSS_ID
from ..definitions.qzss.ubx import L1S_SIGNAL_ID
from ..definitions.qzss.ubx import svid_to_prn
from ..exceptions import AzarashiInvalidMessageError

SHORTEST_SENTENCE = len(RXM_SFRBX_HEADER) + 2 + 8 + 2  # SFRBX + Length + fixed part + CHK
MESSAGE_WORDS = 8  # the 250-bit message takes 8 data words


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

        if len(self.sentence) < SHORTEST_SENTENCE:
            raise AzarashiInvalidMessageError(
                f'Too Short Sentence: expected at least {SHORTEST_SENTENCE} bytes, but got {len(self.sentence)}',
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
        if gnss_id != GNSS_ID:
            raise AzarashiInvalidMessageError(
                f'This Sentence is not from QZSS: expected GNSS ID {GNSS_ID}, but got {gnss_id}',
                self)

        # extracts the satellite id
        self.satellite_svid = self.sentence[7]
        self.satellite_prn = svid_to_prn.get(self.satellite_svid)  # None while it has no PRN number
        self.satellite_id = None if self.satellite_prn is None else self.satellite_prn & 0x3f  # the lower 6 bits

        # checks the signal id
        sig_id = self.sentence[8]
        if sig_id != L1S_SIGNAL_ID:
            raise AzarashiInvalidMessageError(
                f'The Sentence is not an L1S Signal: expected Signal ID {L1S_SIGNAL_ID}, but got {sig_id}',
                self)

        # checks the data size
        payload_length = len(self.sentence) - (len(RXM_SFRBX_HEADER) + 2 + 2)  # SFRBX + Length + CHK
        declared_length = int.from_bytes(self.sentence[4:6], 'little')
        if declared_length != payload_length:
            raise AzarashiInvalidMessageError(
                f'Payload Length Mismatch: declared {declared_length} bytes, but got {payload_length}',
                self)
        num_data_word = self.sentence[10]
        expected_length = 8 + num_data_word * 4  # fixed part + data words
        if expected_length != payload_length:
            raise AzarashiInvalidMessageError(
                f'Invalid Message Length: expected {expected_length} bytes for {num_data_word} data words, '
                f'but got {payload_length}',
                self)
        if num_data_word < MESSAGE_WORDS:
            raise AzarashiInvalidMessageError(
                f'Invalid Message Length: expected at least {MESSAGE_WORDS} data words, but got {num_data_word}',
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

        # stacks the next decoder
        return l1s.Decoder(
            sentence=self.sentence,
            message=self.message,
            timestamp=self.timestamp,
            message_header=self.message_header,
            satellite_id=self.satellite_id,
            satellite_prn=self.satellite_prn,
            satellite_svid=self.satellite_svid,
        ).decode()
