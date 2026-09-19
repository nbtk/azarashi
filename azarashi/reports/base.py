"""What every report carries, whatever the message said."""
from copy import deepcopy
from datetime import datetime, UTC
from typing import Any, TypedDict


class Coordinates(TypedDict):
    """Latitude and longitude as transmitted: 0 is north or east, 1 south or west."""
    lat_ns: int
    lat_d: int
    lat_m: int
    lat_s: int
    lon_ew: int
    lon_d: int
    lon_m: int
    lon_s: int


class DayHourMinute(TypedDict):
    """A time as transmitted, before it is checked and completed to a datetime."""
    day: int
    hour: int
    minute: int



class QzssDcReportBase:
    def __init__(self,
                 sentence: str | bytes,
                 raw: bytes | None = None,
                 timestamp: datetime | None = None,
                 **kwargs: Any) -> None:
        self.sentence = sentence
        if raw is None:
            raw = b''
        self.raw = raw
        if timestamp is None:
            timestamp = datetime.now(UTC)
        self.timestamp = timestamp.astimezone(UTC)  # a naive timestamp is taken as local time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QzssDcReportBase) or type(self) is not type(other):
            return False
        return self.raw == other.raw

    def __hash__(self) -> int:
        return hash(self.raw)

    def __str__(self) -> str:
        return str(self.__dict__)

    def get_params(self) -> dict[str, Any]:
        return deepcopy(self.__dict__)


class QzssDcReportMessagePartial(QzssDcReportBase):
    def __init__(self,
                 message: bytes,
                 nmea: str,
                 message_header: str | bytes | None = None,
                 satellite_id: int | None = None,
                 satellite_prn: int | None = None,
                 satellite_svid: int | None = None,
                 sentence: str | bytes | None = None,
                 **kwargs: Any) -> None:
        if sentence is None:
            sentence = message
        super().__init__(sentence, **kwargs)
        self.message = message
        self.nmea = nmea
        self.message_header = message_header
        self.satellite_id = satellite_id
        self.satellite_prn = satellite_prn
        self.satellite_svid = satellite_svid  # the number a u-blox receiver gives the satellite
        if self.message[1] >> 2 == 44: # DCX
            # starts from camf, discards pab, mt and sd fields.
            self.raw = self.message[3:27] + bytes((self.message[27] & 0xF0,))
        else:
            self.raw = self.message[1:27] + bytes((self.message[27] & 0xF0,))

class QzssDcReportMessageBase(QzssDcReportMessagePartial):
    def __init__(self,
                 preamble: str,
                 message_type: str,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.preamble = preamble
        self.message_type = message_type
