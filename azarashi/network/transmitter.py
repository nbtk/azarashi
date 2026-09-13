#!/usr/bin/env python3

import argparse
import logging
import socket
import sys

import serial

from .log import configure_logging
from ..input_stream import RecordingStream
from ..input_stream import open_input
from ..qzss_dcr_lib.exception import QzssDcrDecoderException
from ..qzss_dcr_lib.exception import QzssDcrDecoderNotImplementedError
from ..qzss_dcr_lib.interface import decode_stream

logger = logging.getLogger(__name__)


class Transmitter:
    def __init__(self, dst_host='ff02::1', dst_port=2112, address_family=socket.AF_UNSPEC):
        self.addr_info = socket.getaddrinfo(dst_host, dst_port,
                                            address_family,
                                            socket.SOCK_DGRAM,
                                            socket.IPPROTO_UDP)[0]

    def handler(self, report):
        with socket.socket(self.addr_info[0], self.addr_info[1]) as sock:
            sat_id = (report.satellite_id or 55).to_bytes(1, 'big')  # PRN183, as in message_to_nmea()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            logger.info(report.nmea)
            sock.sendto(sat_id + report.message, self.addr_info[-1])

    def start(self, stream=sys.stdin, msg_type='ublox', unique=False):
        # relay every message; receivers choose what to use
        decode_stream(stream, msg_type=msg_type, callback=self.handler, unique=unique,
                      ignore_dcr=False, ignore_dcx=False)


def main():
    configure_logging()
    parser = argparse.ArgumentParser(description='azarashi network transmitter',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dst-host', help="destination host", type=str, default='ff02::1')
    parser.add_argument('-p', '--dst-port', help='destination port', type=int, default=2112)
    parser.add_argument('-t', '--msg-type', help="message type", type=str, choices=['hex', 'nmea', 'ublox'],
                        default='nmea')
    parser.add_argument('-f', '--input', help='input serial device or file', type=str, default='stdin')
    parser.add_argument('-b', '--baudrate', help='baud rate of the serial device', type=int, default=9600)
    parser.add_argument('--record', help='append the raw input to this file', type=str, default=None)
    parser.add_argument('-u', '--unique', help='supress duplicate messages', action='store_true')
    args = parser.parse_args()
    # read bytes so that line noise reaches the decoder instead of failing in a text decoder
    stream = open_input(args.input, args.baudrate)
    if args.record is not None:
        stream = RecordingStream(stream, open(args.record, mode='ab'))

    xmitter = Transmitter(dst_host=args.dst_host, dst_port=args.dst_port)
    while True:
        try:
            xmitter.start(stream=stream, msg_type=args.msg_type, unique=args.unique)
        except QzssDcrDecoderException as e:
            logger.warning(f'[{type(e).__name__}] {e}')
        except QzssDcrDecoderNotImplementedError as e:
            logger.warning(f'[{type(e).__name__}] {e}')
        except EOFError as e:
            logger.info(f'{e}')
            break
        except serial.SerialException as e:  # the serial device is gone (e.g. unplugged); retrying would spin
            logger.error(f'[{type(e).__name__}] {e}')
            stream.close()
            return 1
        except Exception as e:
            logger.warning(f'[{type(e).__name__}] {e}')

    stream.close()
    return 0


if __name__ == '__main__':
    exit(main())
