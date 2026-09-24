from datetime import datetime, timedelta

from ..reports import Report
from .qzss import l1s
from .qzss.base import InputDecoder
from ..definitions.gps import GPS_EPOCH
from ..definitions.gps import GPS_UTC_OFFSETS
from ..definitions.gps import SECONDS_PER_WEEK
from ..exceptions import AzarashiInvalidMessageError


def _gps_to_utc(week: int, seconds: int) -> datetime | None:
    """The UTC instant of a GPS week and second, or None before GPS_UTC_OFFSETS begins."""
    gps = GPS_EPOCH + timedelta(weeks=week, seconds=seconds)
    for since, offset in reversed(GPS_UTC_OFFSETS):
        utc = gps - timedelta(seconds=offset)
        if utc >= since:
            return utc
    return None


class Decoder(InputDecoder):
    """A record of the L1S archive, after the archive's PRN: the time it gives replaces the timestamp."""

    sentence: bytes

    def decode(self) -> Report:
        if len(self.sentence) != 1 + 4 + 32:  # PRN + GPS time + message
            raise AzarashiInvalidMessageError(
                f'Invalid Record Length: {len(self.sentence)}',
                self)

        self.satellite_prn = self.sentence[0]
        self.satellite_id = self.satellite_prn & 0x3f  # the lower 6 bits, as in the QZQSM sentence

        time = int.from_bytes(self.sentence[1:5], 'big')
        week, seconds = time >> 20, time & 0xFFFFF
        if seconds >= SECONDS_PER_WEEK:
            raise AzarashiInvalidMessageError(
                f'Invalid Second of the Week: {seconds}',
                self)
        utc = _gps_to_utc(week, seconds)
        if utc is None:
            raise AzarashiInvalidMessageError(
                f'Time Before the GPS-UTC Offsets Known: week {week}, second {seconds}',
                self)
        self.timestamp = utc

        self.message = self.sentence[5:36] + bytes((self.sentence[36] & 0xC0,))  # 250 bits
        self.nmea = self.message_to_nmea()

        # stacks the next decoder
        return l1s.Decoder(
            sentence=self.sentence,
            message=self.message,
            nmea=self.nmea,
            timestamp=self.timestamp,
            satellite_id=self.satellite_id,
            satellite_prn=self.satellite_prn,
        ).decode()
