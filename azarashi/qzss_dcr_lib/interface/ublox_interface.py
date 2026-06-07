import struct

from ..definition import qzss_dcr_message_type
from ..definition import ublox_qzss_dcr_message_header

buffers = {}


def __pop(size, reader, reader_args=None, reader_kwargs=None):
    buf = buffers.get(reader)
    if buf is None:
        buf = b''

    if reader_args is None:
        reader_args = ()

    if reader_kwargs is None:
        reader_kwargs = {}

    while size > len(buf):
        data = reader(*reader_args, **reader_kwargs)
        if not data:
            raise EOFError('Encountered EOF')
        buf += data

    ret = buf[:size]
    buffers.update({reader: buf[size:]})

    return ret


def ublox_qzss_dcr_message_extractor(reader, reader_args=None, reader_kwargs=None):

    if reader_args is None:
        reader_args = ()

    if reader_kwargs is None:
        reader_kwargs = {}

    match_count = 0
    while True:
        if ublox_qzss_dcr_message_header[match_count] == __pop(1,
                                                               reader,
                                                               reader_args,
                                                               reader_kwargs)[0]:
            match_count += 1
        else:
            match_count = 0

        if match_count == len(ublox_qzss_dcr_message_header): # SFRBX message
            match_count = 0
            message_length_bytes = __pop(2,
                                         reader,
                                         reader_args,
                                         reader_kwargs)
            message_length = struct.unpack('<H', message_length_bytes)[0]
            message = ublox_qzss_dcr_message_header + \
                      message_length_bytes + \
                      __pop(message_length + 2 , # payload + CK_A + CK_B
                            reader,
                            reader_args,
                            reader_kwargs)
            
            if message[6] != 5:  # not sent by QZSS
                continue

            if message[8] != 1:  # not a L1S signal
                continue

            if message[16] >> 2 not in qzss_dcr_message_type.keys():
                continue

            return message
