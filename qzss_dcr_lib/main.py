from .exception import QzssDcrDecoderException
from .interface import decode
from .interface import decode_stream
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', help='Set a message type: "spresense", "ublox" or "hex"', type=str)
    args = parser.parse_args()
    if args.type not in ('hex', 'spresense', 'ublox'):
        raise NotImplementedError('The message type must be specified as "spresense", "ublox" or "hex"')

    while True:
        try:
            report = decode_stream(sys.stdin, args.type)
            print(f'--------------------------------\n{report}\n')
        except QzssDcrDecoderException as e:
            print(f'--------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except NotImplementedError as e:
            print(f'--------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except Exception as e:
            print(f'--------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
            return 1


if __name__ == '__main__':
    exit(main())
