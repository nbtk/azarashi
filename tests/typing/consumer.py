"""What a caller must be able to type-check against the published package.

Built and installed the way a user would get it, then checked with --strict:
the annotations have to be visible (py.typed and __all__), the return types
have to be the declared ones, and a mistake has to be caught rather than
waved through as Any.
"""
import datetime
import io

import azarashi
from azarashi import qzss_dc_report
from azarashi.network.receiver import Receiver
from azarashi.network.transmitter import Transmitter

report: azarashi.QzssDcReport = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')
received: datetime.datetime = report.timestamp
kind: str = report.message_type
message: bytes = report.message

if isinstance(report, qzss_dc_report.QzssDcReportJmaTsunami):
    for arrival, raw, what in zip(report.expected_tsunami_arrival_times, report.expected_tsunami_arrival_times_raw,
                                  report.expected_tsunami_arrival_time_types, strict=True):
        when: datetime.datetime | None = arrival
        hour: int = raw['hour']
        text: str = what
elif isinstance(report, qzss_dc_report.QzssDcReportJmaHypocenter):
    degrees: int = report.coordinates_of_hypocenter['lat_d']
    issued: str = report.get_report_time_str()
elif isinstance(report, qzss_dc_report.QzssDcReportJmaVolcano):
    observed: datetime.datetime | None = report.activity_time
elif isinstance(report, qzss_dc_report.QzssDcXtendedMessageBase):
    onset: datetime.datetime | None = report.a6a7_hazard_onset_datetime
    areas: list[str] = report.ex9_target_area_list
    hazard: int = report.camf.a4
    latitude: float = report.a12_ellipse_centre_latitude


def handler(report: azarashi.QzssDcReport) -> None:
    print(report)


with open('frames.ubx', 'rb') as frames:
    try:
        azarashi.decode_stream(frames, 'ublox', callback=handler, unique=60)
    except azarashi.QzssDcrDecoderTimeoutError:
        pass
    except EOFError:
        pass
    except azarashi.QzssDcrDecoderException as e:
        reason: str = e.message

lines = io.StringIO()
next_report: azarashi.QzssDcReport = azarashi.decode_stream(lines, ignore_dcx=False)

Transmitter('ff02::1', 2112).start(lines, 'nmea', unique=True)
Receiver(bind_iface='eth0').start(callback=handler, ignore_dcx=False)
