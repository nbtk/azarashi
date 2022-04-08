from ..definition import ublox_qzss_dcr_message_header
from ..definition import qzss_dcr_message_type


buffers = {}


def __pop(size, reader, reader_args=(), reader_kwargs={}):
    buf = buffers.get(reader)
    if buf == None:
        buf = b''

    while size > len(buf):
        data = reader(*reader_args, **reader_kwargs)
        if not data:
            raise EOFError('Encountered EOF')
        buf += data

    ret = buf[:size]
    buffers.update({reader:buf[size:]})

    return ret


def ublox_qzss_dcr_message_extractor(reader, reader_args=(), reader_kwargs={}):
    match_count = 0
    while True:
        if ublox_qzss_dcr_message_header[match_count] == __pop(1,
                                                               reader,
                                                               reader_args,
                                                               reader_kwargs)[0]:
            match_count += 1
        else:
            match_count = 0

        if match_count == len(ublox_qzss_dcr_message_header):
            match_count = 0
            message = ublox_qzss_dcr_message_header + \
                      __pop(52-len(ublox_qzss_dcr_message_header),
                            reader,
                            reader_args,
                            reader_kwargs)
   
            if message[8] != 1: # not a L1S signal
                continue
    
            if message[16] >> 2 not in qzss_dcr_message_type.keys():
                continue

            return message
