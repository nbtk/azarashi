import argparse
import datetime
import sys
from pprint import pformat

from azarashi import QzssDcrDecoderException
from azarashi import QzssDcrDecoderNotImplementedError
from azarashi import decode_stream
from azarashi.input_stream import RecordingStream
from azarashi.input_stream import open_input


def _utc(time: datetime.datetime) -> str:
    return time.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')


def main() -> int:
    parser = argparse.ArgumentParser(description='azarashi CLI', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('type', help='message type', type=str, choices=['hex', 'nmea', 'ublox'])
    parser.add_argument('-f', '--input', help='input serial device or file', type=str, default='stdin')
    parser.add_argument('-b', '--baudrate', help='baud rate of the serial device', type=int, default=9600)
    parser.add_argument('--record', help='append the raw input to this file', type=str, default=None)
    parser.add_argument('--time', help='time the input was received, e.g. 2026-09-01T12:00:00Z',
                        type=datetime.datetime.fromisoformat, default=None)
    parser.add_argument('-s', '--source', help='output the source messages', action='store_true')
    parser.add_argument('-u', '--unique', help='supress duplicate messages', action='store_true')
    parser.add_argument('-r', '--ignore-dcr', help='ignore dcr messages', action='store_true')
    parser.add_argument('-x', '--ignore-dcx', help='ignore dcx messages', action='store_true')
    parser.add_argument('-v', '--verbose', help="verbose mode", action='store_true')
    args = parser.parse_args()
    # read bytes so that line noise reaches the decoder instead of failing in a text decoder
    source = open_input(args.input, args.baudrate)
    stream = source if args.record is None else RecordingStream(source, open(args.record, mode='ab'))

    def now() -> str:
        return _utc(args.time or datetime.datetime.now(datetime.UTC))

    while True:
        try:
            report = decode_stream(stream, args.type,
                                   unique=args.unique,
                                   ignore_dcr=args.ignore_dcr,
                                   ignore_dcx=args.ignore_dcx,
                                   timestamp=args.time)
            received = _utc(report.timestamp)  # decode_stream() waits for a message: this is when it arrived
            if args.verbose is True:
                print(f'{received} --------------------------------\n{pformat(report.get_params())}\n')
            else:
                print(f'{received} --------------------------------\n{report}\n')

            if args.source is True:
                sentence = report.sentence
                if isinstance(sentence, bytes):
                    src = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
                else:
                    src = sentence
                print(f'# src: {src}\n# hex: {report.message.hex().upper()[:-1]}\n')

            sys.stdout.flush()
        except QzssDcrDecoderException as e:
            print(f'{now()} --------------------------------\n'
                  f'# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except QzssDcrDecoderNotImplementedError as e:
            print(f'{now()} --------------------------------\n'
                  f'# [{type(e).__name__}] {e}\n', file=sys.stderr)
        except EOFError as e:
            print(f'{e}\n', file=sys.stderr)
            stream.close()
            return 0
        except Exception as e:
            print(f'{now()} --------------------------------\n'
                  f'# [{type(e).__name__}] {e}\n', file=sys.stderr)
            stream.close()
            return 1


if __name__ == '__main__':
    exit(main())
