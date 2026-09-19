#!/usr/bin/env python3

import argparse
import logging
import socket
import sys
from collections.abc import Callable
from pprint import pformat
from typing import Any

from .log import configure_logging
from ..exceptions import AzarashiDecodeError
from ..exceptions import AzarashiInvalidMessageError
from ..api import decode
from ..reports import QzssDcReport

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, bind_addr: str = '::', bind_port: int = 2112, bind_iface: str = 'any',
                 address_family: int = socket.AF_UNSPEC) -> None:
        self.addr_info = socket.getaddrinfo(bind_addr, bind_port,
                                            address_family,
                                            socket.SOCK_DGRAM,
                                            socket.IPPROTO_UDP)[0]
        self.bind_iface: bytes | None
        if bind_iface == 'any':
            self.bind_iface = None
        else:
            self.bind_iface = (bind_iface + '\0').encode()

    @staticmethod
    def default_handler(report: QzssDcReport) -> None:
        logger.info('- - - - - - - - - - - - - - - - - - - - - - - - - - - -\n' + pformat(report.get_params()) + '\n')

    def start(self,
              callback: Callable[..., object] | None = None,
              callback_args: tuple[Any, ...] = (),
              callback_kwargs: dict[str, Any] | None = None,
              ignore_dcr: bool = False,
              ignore_dcx: bool = True) -> None:
        if callback_kwargs is None:
            callback_kwargs = {}
        callback = callback or self.default_handler
        with socket.socket(self.addr_info[0], self.addr_info[1]) as sock:
            if self.bind_iface is not None:
                if sys.platform != 'linux':
                    raise OSError('Binding to an interface needs SO_BINDTODEVICE, which only Linux has')
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.bind_iface)
            sock.bind(self.addr_info[-1])
            while True:
                data = sock.recvfrom(256)
                payload = data[0]
                try:
                    if not payload:  # a datagram never ends a stream, so an empty one is only too short
                        raise AzarashiInvalidMessageError('Too Short Sentence')
                    report = decode(payload, 'net')
                except AzarashiDecodeError as e:
                    # a datagram that is not a message, e.g. from other software: leaving would drop what is queued
                    logger.warning(f'[{type(e).__name__}] {e}')
                    continue
                if report.message_type == 'DCR' and ignore_dcr is True:
                    continue
                if report.message_type == 'DCX' and ignore_dcx is True:
                    continue
                callback(report, *callback_args, **callback_kwargs)


def simple_handler(report: QzssDcReport) -> None:
    logger.info('\n' + str(report) + '\n')


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description='azarashi network receiver',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-b', '--bind-addr', help="address to bind", type=str, default='::')
    parser.add_argument('-p', '--bind-port', help='port to bind', type=int, default=2112)
    parser.add_argument('-i', '--bind-iface', help="iface to bind", type=str, default='any')
    parser.add_argument('-r', '--ignore-dcr', help='ignore dcr messages', action='store_true')
    parser.add_argument('-x', '--ignore-dcx', help='ignore dcx messages', action='store_true')
    parser.add_argument('-v', '--verbose', help="verbose mode", action='store_true')
    args = parser.parse_args()
    recver = Receiver(args.bind_addr, args.bind_port, args.bind_iface)
    if args.verbose:
        recver.start(ignore_dcr=args.ignore_dcr, ignore_dcx=args.ignore_dcx)
    else:
        recver.start(callback=simple_handler, ignore_dcr=args.ignore_dcr, ignore_dcx=args.ignore_dcx)
    return 0


if __name__ == '__main__':
    exit(main())
