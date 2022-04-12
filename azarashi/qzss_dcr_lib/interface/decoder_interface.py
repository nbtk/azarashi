from .hex_interface import hex_qzss_dcr_message_extractor
from .spresense_interface import spresense_qzss_dcr_message_extractor
from .ublox_interface import ublox_qzss_dcr_message_extractor
from ..exception import QzssDcrDecoderException
from ..decoder import HexQzssDcrDecoder
from ..decoder import SpresenseQzssDcrDecoder
from ..decoder import UBloxQzssDcrDecoder


caches = {}
cache_size = 20


def decode(msg, msg_type='hex'):
    if not msg:
        raise EOFError('Encountered EOF')

    if msg_type == 'hex':
        return HexQzssDcrDecoder(msg).decode()
    elif msg_type == 'spresense':
        return SpresenseQzssDcrDecoder(msg).decode()
    elif msg_type == 'ublox':
        return UBloxQzssDcrDecoder(msg).decode()
    else:
        raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')


def decode_stream(stream,
                  msg_type='hex',
                  callback=None,
                  callback_args=(),
                  callback_kwargs={},
                  unique=False):
    cache = caches.get(stream)
    if cache is None:
        cache = []

    while True:
        if msg_type == 'hex':
            msg = hex_qzss_dcr_message_extractor(stream.readline)
        elif msg_type == 'spresense':
            msg = spresense_qzss_dcr_message_extractor(stream.readline)
        elif msg_type == 'ublox':
            if 'buffer' in dir(stream) and 'read1' in dir(stream.buffer):
                msg = ublox_qzss_dcr_message_extractor(stream.buffer.read1)
            else:
                msg = ublox_qzss_dcr_message_extractor(stream.read1)
        else:
            raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')
    
        report = decode(msg, msg_type)
        if report in cache:
            kick = False
            cache.remove(report)
        else:
            kick = True

        if unique:
            cache = cache[-(cache_size-1):] + [report]
        else:
            cache = []

        caches.update({stream: cache})

        if kick == True:
            if callback == None:
                return report
            callback(report, *callback_args, **callback_kwargs)
