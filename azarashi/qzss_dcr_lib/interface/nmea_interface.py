from ..definition import nmea_qzss_dcr_message_header


def nmea_qzss_dcr_message_extractor(reader, reader_args=(), reader_kwargs={}):
    while True:
        msg = reader(*reader_args, **reader_kwargs)
        if not msg:
            raise EOFError('Encountered EOF')
        elif type(msg) == bytes or type(msg) == bytearray:
            msg = msg.decode()
        if msg.startswith(nmea_qzss_dcr_message_header):
            return msg
