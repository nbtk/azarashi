#!/usr/bin/env python3

import logging
import argparse
import socket
import sys
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
            sat_id = (report.satellite_id or 0x55).to_bytes(1, 'big')
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            logger.info(report.nmea)
            sock.sendto(sat_id + report.message, self.addr_info[-1])

    def start(self, stream=sys.stdin, msg_type='ublox', unique=False):
        decode_stream(stream, msg_type=msg_type, callback=self.handler, unique=unique)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='azarashi network transmitter', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dst-host', help="destination host", type=str, default='ff02::1')
    parser.add_argument('-p', '--dst-port', help='destination port', type=int, default=2112)
    parser.add_argument('-t', '--msg-type', help="message type", type=str, choices=['ublox', 'nmea', 'hex'], default='ublox')
    parser.add_argument('-f', '--input', help='input device', type=str, default='stdin')
    parser.add_argument('-u', '--unique', help='supress duplicate messages', action='store_true')
    args = parser.parse_args()
    if args.input == 'stdin': 
        stream = sys.stdin
    else:
        stream = open(args.input, mode='r')

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
        except Exception as e:
            logger.warning(f'[{type(e).__name__}] {e}')

    stream.close()
    return 0


if __name__ == '__main__':
    exit(main())

