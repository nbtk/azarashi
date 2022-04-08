from ..exception import QzssDcrDecoderException


class QzssDcrDecoderBase:
    schema = None

    def __init__(self, sentence, **kwargs):
        self.set_params(sentence=sentence,
                        **kwargs)

    def decode(self):
        raise NotImplemented()

    def extract_field(self, slider, size):
        field = bytearray(self.message[slider >> 3:(slider + size >> 3) + 1])
        field[0] = field[0] & (2 ** (8 - (slider & 7)) - 1)
        return int.from_bytes(field, 'big') >> (8 - (slider + size & 7))

    def set_params(self, **kwargs):
        self.__dict__.update(self.schema(**kwargs).get_params())

    def get_params(self):
        return self.__dict__
