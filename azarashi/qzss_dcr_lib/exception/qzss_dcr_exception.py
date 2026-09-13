class QzssDcrDecoderException(Exception):
    def __init__(self, message, instance=None):
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self):
        sentence = getattr(self.instance, 'nmea', None) or getattr(self.instance, 'sentence', None)
        if sentence is None:
            return f'{self.message}'
        elif type(sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'


class QzssDcrDecoderTimeoutError(EOFError):
    """A stream with a read timeout (e.g. pySerial) had no complete message before the timeout expired.

    Partially read data is kept, so calling decode_stream() again continues from it.
    It is an EOFError so that existing EOF handling keeps working; catch it first to keep reading.
    """


class QzssDcrDecoderNotImplementedError(NotImplementedError):
    def __init__(self, message, instance=None):
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self):
        sentence = getattr(self.instance, 'nmea', None) or getattr(self.instance, 'sentence', None)
        if sentence is None:
            return f'{self.message}'
        elif type(sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'
