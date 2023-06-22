import datetime

from .hex_interface import hex_qzss_dcr_message_extractor
from .nmea_interface import nmea_qzss_dcr_message_extractor
from .ublox_interface import ublox_qzss_dcr_message_extractor
from ..decoder import HexQzssDcrDecoder
from ..decoder import NetQzssDcrDecoder
from ..decoder import NmeaQzssDcrDecoder
from ..decoder import UBloxQzssDcrDecoder
from ..exception import QzssDcrDecoderException

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


def decode_stream(stream, # do not decode one stream in parallel!
                  msg_type='nmea',
                  callback=None,
                  callback_args=(),
                  callback_kwargs={},
                  unique=False):
    for existing_stream in caches.keys():
        if existing_stream.closed:
            try:
                caches.pop(existing_stream) # discards the garbage to prevent memory leaks
            except KeyError: # might happen during race conditions
                pass

    if unique:
        cache = caches.get(stream)
        if cache is None:
            cache = []
    else:
        cache = None

    if msg_type == 'hex':
        if callable(getattr(stream, 'readline', None)):
            extractor = hex_qzss_dcr_message_extractor
            reader = stream.readline
            reader_kwargs = {}
        else:
            raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
    elif msg_type == 'nmea' or msg_type == 'spresense':
        if callable(getattr(stream, 'readline', None)):
            extractor = nmea_qzss_dcr_message_extractor
            reader = stream.readline
            reader_kwargs = {}
        else:
            raise QzssDcrDecoderException(f'readline() does not exist: {type(stream)}')
    elif msg_type == 'ublox':
        if callable(getattr(stream, 'read1', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = stream.read1
            reader_kwargs = {}
        elif hasattr(stream, 'buffer') and callable(getattr(stream.buffer, 'read1', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = stream.buffer.read1
            reader_kwargs = {}
        elif callable(getattr(stream, 'read', None)):
            extractor = ublox_qzss_dcr_message_extractor
            reader = stream.read
            reader_kwargs = {'size': 1}
        else:
            raise QzssDcrDecoderException(f'Neither read() nor read1() exists: {type(stream)}')
    else:
        raise QzssDcrDecoderException(f'Unknown Message Type: {msg_type}')

    while True:
        msg = extractor(reader, reader_kwargs=reader_kwargs)
        report = decode(msg, msg_type)

        if unique:
            if report in cache:
                freshness = (datetime.datetime.now() - report.timestamp).total_seconds()
                if freshness > cache_expiration:  # the cache is rotten
                    fire = True
                else:  # the cache is fresh
                    fire = False
                cache.remove(report)
            else:
                fire = True

            caches.update({stream: cache[-(cache_size - 1):] + [report]})

            if fire is False:
                continue

        if callback is None:
            return report
        callback(report, *callback_args, **callback_kwargs)
