"""Correct uses of the installed package, which mypy --strict and pyright must accept.

CI builds and installs the wheel before checking this file, so it also fails when the
annotations do not reach callers (py.typed, __all__).
"""
import datetime
import io

import azarashi
from azarashi import qzss_dc_report
from azarashi import reports
from azarashi.network.receiver import Receiver
from azarashi.network.transmitter import Transmitter

report: azarashi.Report = azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05')
received: datetime.datetime = report.timestamp
kind: str = report.message_type
message: bytes = report.message
network_report: azarashi.Report = azarashi.decode(bytes((55,)) + message, msg_type='net')

if isinstance(report, reports.dcr.Tsunami):
    for arrival, raw, what in zip(report.expected_tsunami_arrival_times, report.expected_tsunami_arrival_times_raw,
                                  report.expected_tsunami_arrival_time_types, strict=True):
        when: datetime.datetime | None = arrival
        hour: int = raw['hour']
        text: str = what
elif isinstance(report, reports.dcr.Hypocenter):
    position: str = report.coordinates_of_hypocenter
    occurred: datetime.datetime | None = report.occurrence_time_of_earthquake
    occurred_day: int = report.occurrence_time_of_earthquake_raw['day']
    degrees: int = report.coordinates_of_hypocenter_raw['lat_d']
    issued: str = report.get_report_time_str()
elif isinstance(report, reports.dcr.Volcano):
    observed: datetime.datetime | None = report.activity_time
elif isinstance(report, reports.dcx.AlertBase):
    onset: datetime.datetime | None = report.a6a7_hazard_onset_datetime
    category: str = report.a4_hazard_category  # always set on an alert
    areas: list[str] | None = report.ex9_target_area_list
    hazard: int = report.camf.a4
    latitude: float | None = report.a12_ellipse_centre_latitude
elif isinstance(report, qzss_dc_report.dcx.NullMsg):  # the earlier module name; an alert field here is a type error
    null_kind: str = report.dcx_message_type


def handler(report: azarashi.Report) -> None:
    print(report)


with open('frames.ubx', 'rb') as frames:
    try:
        azarashi.decode_stream(frames, 'ublox', callback=handler, unique=60)
    except azarashi.AzarashiTimeoutError:
        pass
    except EOFError:
        pass
    except azarashi.AzarashiInvalidMessageError as e:
        reason: str = e.message

with open('frames.ubx', 'rb') as frames:  # the same code written with the earlier names
    try:
        azarashi.decode_stream(frames, 'ublox', callback=handler, unique=60)
    except EOFError:
        pass
    except azarashi.QzssDcrDecoderException as old:
        earlier_reason: str = old.message

lines = io.StringIO()
next_report: azarashi.Report = azarashi.decode_stream(lines, ignore_dcx=False)

Transmitter('ff02::1', 2112).start(lines, 'nmea', unique=True)
Receiver(bind_iface='eth0').start(callback=handler, ignore_dcx=False)
