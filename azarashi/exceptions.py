class AzarashiError(Exception):
    """The base of every exception azarashi defines."""

    def __init__(self, message: str, instance: object = None) -> None:
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self) -> str:
        sentence = getattr(self.instance, 'nmea', None) or getattr(self.instance, 'sentence', None)
        if not sentence:  # nothing to show: an empty one would leave a dangling arrow
            return self.message
        elif type(sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'


class AzarashiDecodeError(AzarashiError):
    """A message did not become a report. Catch this one to log it and keep reading the stream."""


class AzarashiInvalidMessageError(AzarashiDecodeError):
    """The message cannot be read: a length, a checksum or a CRC is wrong, or no decoder fits it.

    A code value the spec does not define is not one of these; it is kept and named in the report.
    """


class AzarashiNotImplementedError(AzarashiDecodeError, NotImplementedError):
    """azarashi has no decoder for the message, e.g. an experimental broadcast."""


class AzarashiTimeoutError(AzarashiError, EOFError):
    """A stream with a read timeout (e.g. pySerial) had no complete message before the timeout expired.

    Partially read data is kept, so calling decode_stream() again continues from it.
    It is an EOFError so that existing EOF handling keeps working; catch it first to keep reading.
    It stays outside AzarashiDecodeError because nothing failed to decode.
    """
