from ..reports import Report
from .qzss import l1s
from .qzss.base import InputDecoder
from ..exceptions import AzarashiInvalidMessageError

SENTENCE_LENGTH = 33  # the satellite id and 32 bytes of the message


class Decoder(InputDecoder):
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise AzarashiInvalidMessageError('Empty Message')

        if not isinstance(self.sentence, (bytes, bytearray)):  # a datagram is bytes
            raise AzarashiInvalidMessageError(
                'Invalid Sentence',
                self)
        self.sentence = self.sentence.strip()

        if len(self.sentence) < SENTENCE_LENGTH:
            raise AzarashiInvalidMessageError(
                f'Too Short Sentence: expected {SENTENCE_LENGTH} bytes, but got {len(self.sentence)}',
                self)
        if len(self.sentence) > SENTENCE_LENGTH:
            raise AzarashiInvalidMessageError(
                f'Too Long Sentence: expected {SENTENCE_LENGTH} bytes, but got {len(self.sentence)}',
                self)

        self.message = self.sentence[1:]

        # extracts a satellite id
        self.satellite_id = self.sentence[0]
        self.satellite_prn = self.satellite_id | 0x80

        # stacks the next decoder
        return l1s.Decoder(
            sentence=self.sentence,
            message=self.message,
            timestamp=self.timestamp,
            satellite_id=self.satellite_id,
            satellite_prn=self.satellite_prn,
        ).decode()
