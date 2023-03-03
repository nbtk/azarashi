class QzssDcrDecoderException(Exception):
    def __init__(self, message, sentence=None):
        self.message = message
        self.sentence = sentence
        super().__init__(self.message)

    def __str__(self):
        if type(self.sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in self.sentence) + "'"
        else:
            sentence = self.sentence

        if sentence is not None:
            return f'{self.message} -> {sentence}'
        return f'{self.message}'


class QzssDcrDecoderNotImplementedError(NotImplementedError):
    def __init__(self, message, sentence=None):
        self.message = message
        self.sentence = sentence
        super().__init__(self.message)

    def __str__(self):
        if type(self.sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in self.sentence) + "'"
        else:
            sentence = self.sentence

        if sentence is not None:
            return f'{self.message} -> {sentence}'
        return f'{self.message}'
