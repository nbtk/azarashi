import argparse
import datetime
import sys
from pprint import pformat

from azarashi import QzssDcrDecoderException
from azarashi import QzssDcrDecoderNotImplementedError
from azarashi import decode_stream


def main():
    parser = argparse.ArgumentParser(description='azarashi CLI', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('type', help='message type', type=str, choices=['hex', 'nmea', 'ublox'])
    parser.add_argument('-f', '--input', help='input device', type=str, default='stdin')
    parser.add_argument('-s', '--source', help='output the source messages', action='store_true')
    parser.add_argument('-u', '--unique', help='supress duplicate messages', action='store_true')
    parser.add_argument('-v', '--verbose', help="verbose mode", action='store_true')
    args = parser.parse_args()
    if args.input == 'stdin':
        stream = sys.stdin
    else:
        stream = open(args.input, mode='r')

    while True:
        now = datetime.datetime.now().isoformat()
        try:
            report = decode_stream(stream, args.type, unique=args.unique)
            if args.verbose is True:
                print(f'{now} --------------------------------\n{pformat(report.get_params())}\n')
            else:
                print(f'{now} --------------------------------\n{report}\n')

            if args.source is True:
                if type(report.sentence) is bytes:
                    src = "b'" + ''.join(r'\x%02X' % c for c in report.sentence) + "'"
                else:
                    src = report.sentence
                print(f'# src: {src}\n# hex: {report.message.hex().upper()[:-1]}\n')

            sys.stdout.flush()
        except QzssDcrDecoderException as e:
            print(f'{now} --------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except QzssDcrDecoderNotImplementedError as e:
            print(f'{now} --------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except EOFError as e:
            print(f'{e}\n', file=sys.stderr)
            stream.close()
            return 0
        except Exception as e:
            print(f'{now} --------------------------------\n# [{type(e).__name__}] {e}\n', file=sys.stderr)
            stream.close()
            return 1


if __name__ == '__main__':
    exit(main())
