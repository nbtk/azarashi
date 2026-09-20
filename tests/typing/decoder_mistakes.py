"""Static checks of the internal frame boundary; do not execute this file."""
from datetime import UTC, datetime

from azarashi.decoders.common import Decoder

stamp = datetime.now(UTC)
Decoder('', nmea='', timestamp=stamp)  # want: call-arg
Decoder('', message='invalid', nmea='', timestamp=stamp)  # want: arg-type
Decoder('', message=b'', nmea='', timestamp=stamp, satelite_id=55)  # want: call-arg
