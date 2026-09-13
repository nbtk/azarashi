"""Mistakes the published package must catch, one per line.

Each line is expected to fail; the CI step asserts the count, so a checker
that has stopped seeing azarashi's types fails here rather than passing
silently.
"""
import azarashi

report = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')

issued = report.report_time                                  # a DCX message has no report time
azarashi.decode(report.message, msg_type=0)                  # msg_type is a str
azarashi.decode_stream('$QZQSM,55,...')                      # a str is not a stream
seconds: int = report.timestamp                              # a datetime
