import datetime
from .hex_interface import hex_qzss_dcr_message_extractor
from .nmea_interface import nmea_qzss_dcr_message_extractor
from .ublox_interface import ublox_qzss_dcr_message_extractor
from ..exception import QzssDcrDecoderException
from ..decoder import HexQzssDcrDecoder
from ..decoder import NetQzssDcrDecoder
from ..decoder import NmeaQzssDcrDecoder
from ..decoder import UBloxQzssDcrDecoder

caches = {}
cache_size = 256
cache_expiration = 3600 * 24


def decode(msg, msg_type='nmea'):
    if not msg:
        raise EOFError('Encountered EOF')

    if msg_type == 'hex':
        return HexQzssDcrDecoder(msg).decode()
    elif msg_type == 'net':
        return NetQzssDcrDecoder(msg).decode()
    elif msg_type == 'nmea' or msg_type == 'spresense':
        return NmeaQzssDcrDecoder(msg).decode()
    elif msg_type == 'ublox':
        return UBloxQzssDcrDecoder(msg).decode()
    else:
        raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')


def decode_stream(stream,
                  msg_type='nmea',
                  callback=None,
                  callback_args=(),
                  callback_kwargs={},
                  unique=False):
    cache = caches.get(stream)
    if cache is None:
        cache = []

    while True:
        if msg_type == 'hex':
            if callable(getattr(stream, 'readline', None)):
                msg = hex_qzss_dcr_message_extractor(stream.readline)
            else:
                raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
        elif msg_type == 'nmea' or msg_type == 'spresense':
            if callable(getattr(stream, 'readline', None)):
                msg = nmea_qzss_dcr_message_extractor(stream.readline)
            else:
                raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
        elif msg_type == 'ublox':
            if callable(getattr(stream, 'read1', None)):
                msg = ublox_qzss_dcr_message_extractor(stream.read1)
            elif hasattr(stream, 'buffer') and callable(getattr(stream.buffer, 'read1', None)):
                msg = ublox_qzss_dcr_message_extractor(stream.buffer.read1)
            elif callable(getattr(stream, 'read', None)):
                msg = ublox_qzss_dcr_message_extractor(stream.read, reader_kwargs={'size': 1})
            else:
                raise QzssDcrDecoderException(f'read() nor read1() do not exist: {type(stream)}')
        else:
            raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')

        report = decode(msg, msg_type)
        if report in cache:
            freshness = (datetime.datetime.now()-report.timestamp).total_seconds()
            if freshness > cache_expiration: # the cache is rotten
                kick = True
            else: # the cache is fresh
                kick = False
            cache.remove(report)
        else:
            kick = True

        if unique:
            cache = cache[-(cache_size - 1):] + [report]
        else:
            cache = []

        caches.update({stream: cache})

        if kick is True:
            if callback is None:
                return report
            callback(report, *callback_args, **callback_kwargs)
