from ..reports import Report
from .qzss import l1s
from .qzss.base import InputDecoder
from ..exceptions import AzarashiInvalidMessageError

SENTENCE_LENGTH = 63  # the 250-bit message with 2 bits of padding, in hex digits


class Decoder(InputDecoder):
    sentence: str | bytes

    def decode(self) -> Report:
        if not self.sentence:
            raise AzarashiInvalidMessageError('Empty Message')

        sentence = self.sentence
        if isinstance(sentence, (bytes, bytearray)):  # a line read as bytes, as from pySerial
            sentence = sentence.decode(errors='replace')
        self.sentence = sentence.strip()

        if len(self.sentence) < SENTENCE_LENGTH:
            raise AzarashiInvalidMessageError(
                f'Too Short Sentence: expected {SENTENCE_LENGTH} characters, but got {len(self.sentence)}',
                self)
        if len(self.sentence) > SENTENCE_LENGTH:
            raise AzarashiInvalidMessageError(
                f'Too Long Sentence: expected {SENTENCE_LENGTH} characters, but got {len(self.sentence)}',
                self)

        # converts the message to bytes type
        try:
            self.message = bytes.fromhex(self.sentence + '0')
        except ValueError as err:
            raise AzarashiInvalidMessageError(
                'Invalid Message',
                self) from err
        if len(self.message) != 32:  # bytes.fromhex() skips whitespace between the bytes
            raise AzarashiInvalidMessageError(
                'Invalid Message',
                self)

        # stacks the next decoder
        return l1s.Decoder(
            sentence=self.sentence,
            message=self.message,
            timestamp=self.timestamp,
        ).decode()
