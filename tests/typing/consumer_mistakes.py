"""Wrong uses of the installed package, one per line, which mypy --strict must all report.

CI checks the number of errors, so a type checker that no longer sees azarashi's types fails the job.
"""
import io

import azarashi
from azarashi.network.transmitter import Transmitter

report = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')

issued = report.report_time                                  # a DCX message has no report time
azarashi.decode(report.message, msg_type=0)                  # msg_type is a str
azarashi.decode_stream('$QZQSM,55,...')                      # a str is not a stream
seconds: int = report.timestamp                              # a datetime
azarashi.decode_stream(io.BytesIO(), msg_type='net')          # net is a datagram, not a stream
Transmitter().start(io.BytesIO(), msg_type='net')              # the transmitter reads a stream too
