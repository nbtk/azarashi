from qzss_dcr_lib.definition import spresense_qzss_dcr_message_header


def spresense_qzss_dcr_message_extractor(reader, reader_args=(), reader_kwargs={}):
    while True:
        msg = reader(*reader_args, **reader_kwargs)
        if not msg:
            raise EOFError('Encountered EOF')
        elif type(msg) == bytes or type(msg) == bytearray:
            msg = msg.decode()
        if msg.startswith(spresense_qzss_dcr_message_header):
            return msg
