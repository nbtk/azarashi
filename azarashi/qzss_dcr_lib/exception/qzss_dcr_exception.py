class QzssDcrDecoderException(Exception):
    def __init__(self, message, instance=None):
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self):
        sentence = getattr(self.instance, 'nmea') or getattr(self.instance, 'sentence')
        if sentence is None:
            return f'{self.message}'
        elif type(sentence) is bytes:
                sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'


class QzssDcrDecoderNotImplementedError(NotImplementedError):
    def __init__(self, message, instance=None):
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self):
        sentence = getattr(self.instance, 'nmea') or getattr(self.instance, 'sentence')
        if sentence is None:
            return f'{self.message}'
        elif type(sentence) is bytes:
                sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'

