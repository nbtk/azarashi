from ..definition import nmea_qzss_dcr_message_header


class QzssDcrDecoderBase:
    schema = None

    def __init__(self, sentence, **kwargs):
        self.set_params(sentence=sentence, **kwargs)

    def decode(self):
        raise NotImplemented()

    def message_to_nmea(self):
        sat_id = getattr(self, 'satellite_id', None)
        if sat_id is None:
            sat_id = 55  # Set the satellite_id of PRN183 if it was default.

        nmea_partial = '{header},{satellite_id},{message}'.format(header=nmea_qzss_dcr_message_header,
                                                                  satellite_id=sat_id,
                                                                  message=self.message.hex()[:-1].upper())

        checksum = 0
        for c in nmea_partial[1:]:  # without the '$' at the beginning
            checksum ^= ord(c)

        return (nmea_partial + '*%02X' % checksum)

    def extract_field(self, slider, size):
        field = bytearray(self.message[slider >> 3:(slider + size >> 3) + 1])
        field[0] = field[0] & (2 ** (8 - (slider & 7)) - 1)
        return int.from_bytes(field, 'big') >> (8 - (slider + size & 7))

    def set_params(self, **kwargs):
        self.__dict__.update(self.schema(**kwargs).get_params())

    def get_params(self):
        return self.__dict__
