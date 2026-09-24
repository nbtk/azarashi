"""GPS time, which the L1S archive stamps each message with."""
from datetime import UTC, datetime

GPS_EPOCH = datetime(1980, 1, 6, tzinfo=UTC)
SECONDS_PER_WEEK = 7 * 24 * 3600

#: How far GPS time runs ahead of UTC, from the UTC instant each value holds. GPS time counts no
#: leap seconds. Leap seconds are to end by 2035 (CGPM, 2022); until then a new one is added here
#: when the IERS announces it. The table starts in 2017, before which no DCR or DCX was broadcast.
GPS_UTC_OFFSETS: tuple[tuple[datetime, int], ...] = (
    (datetime(2017, 1, 1, tzinfo=UTC), 18),
)
