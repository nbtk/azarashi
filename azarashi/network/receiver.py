#!/usr/bin/env python3

import logging
import socket
import azarashi
from pprint import pformat


logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, bind_addr='::', bind_port=2112, bind_iface='any', address_family=socket.AF_UNSPEC):
        self.addr_info = socket.getaddrinfo(bind_addr, bind_port,
                                            address_family,
                                            socket.SOCK_DGRAM,
                                            socket.IPPROTO_UDP)[0]
        if bind_iface == 'any': 
            self.bind_iface = None
        else:
            self.bind_iface = (bind_iface + '\0').encode()

    @staticmethod
    def default_handler(report, *callback_args, **callback_kwargs):
        logger.info('- - - - - - - - - - - - - - - - - - - - - - - - - - - -\n' + pformat(report.get_params()) + '\n')

    def start(self, callback=default_handler, callback_args=(), callback_kwargs={}):
        callback = callback or self.handler
        with socket.socket(self.addr_info[0], self.addr_info[1]) as sock:
            if self.bind_iface is not None:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, 'wlan0'.encode())
            sock.bind(self.addr_info[-1])
            while True:
                data = sock.recvfrom(256)
                payload = data[0]
                callback(azarashi.decode(payload, 'net'),
                         *callback_args, **callback_kwargs)


def simple_handler(report):
        logger.info('\n' + str(report) + '\n')


def main():
    import argparse
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='azarashi network receiver', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-b', '--bind-addr', type=str, default='::', help="address to bind")
    parser.add_argument('-p', '--bind-port', type=int, default=2112, help='port to bind')
    parser.add_argument('-i', '--bind-iface', type=str, default='any', help="iface to bind")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose mode")
    args = parser.parse_args()
    recver = Receiver(args.bind_addr, args.bind_port)
    if args.verbose:
        recver.start()
    else:
        recver.start(callback=simple_handler)


if __name__ == '__main__':
    exit(main())

