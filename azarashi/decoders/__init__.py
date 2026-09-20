"""The decoders that turn what a stream delivers into the reports of azarashi.reports.

Each module decodes one thing and calls the next, and Decoder is the way into each: the four
input formats hand over a message, common reads what every message carries and passes it to the
message type, and dcr and dcx read the rest. dcr holds one class per disaster category, because
the message differs by category, and each makes the report class of the same name in reports.dcr.
"""
from . import base
from . import common
from . import dcr
from . import dcx
from . import hex
from . import net
from . import nmea
from . import ublox

__all__ = ['base', 'common', 'dcr', 'dcx', 'hex', 'net', 'nmea', 'ublox']
