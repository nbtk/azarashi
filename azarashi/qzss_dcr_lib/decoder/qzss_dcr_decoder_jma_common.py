from calendar import monthrange
from datetime import datetime
from datetime import timedelta
from datetime import UTC

from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..definition import qzss_dcr_jma_days
from ..definition import qzss_dcr_jma_depth_of_hypocenter
from ..definition import qzss_dcr_jma_epicenter_and_hypocenter
from ..definition import qzss_dcr_jma_expected_tsunami_arrival_time_undefined
from ..definition import qzss_dcr_jma_expected_tsunami_arrival_time_undefined_en
from ..definition import qzss_dcr_jma_hours
from ..definition import qzss_dcr_jma_latitude_and_longitude_minutes
from ..definition import qzss_dcr_jma_latitude_and_longitude_seconds
from ..definition import qzss_dcr_jma_latitude_and_longitude_undefined
from ..definition import qzss_dcr_jma_latitude_degrees
from ..definition import qzss_dcr_jma_local_government
from ..definition import qzss_dcr_jma_longitude_degrees
from ..definition import qzss_dcr_jma_minutes
from ..definition import qzss_dcr_jma_notification_on_disaster_prevention
from ..definition.qzss_dcr_definition import QzssDcrDefinition
from ..report import Coordinates
from ..report import DayHourMinute
from ..report import QzssDcReportJmaBase


class QzssDcrDecoderJmaCommon(QzssDcrDecoderBase):
    report_time: datetime

    def extract_day_hour_min_raw(self, slider: int) -> DayHourMinute:
        return {'day': self.extract_field(slider, 5),
                'hour': self.extract_field(slider + 5, 5),
                'minute': self.extract_field(slider + 10, 6)}

    def extract_day_hour_min_field(self, slider: int) -> tuple[datetime | None, DayHourMinute]:
        raw = self.extract_day_hour_min_raw(slider)
        dt_d, dt_h, dt_mi = raw['day'], raw['hour'], raw['minute']
        if dt_d not in qzss_dcr_jma_days or dt_h not in qzss_dcr_jma_hours or dt_mi not in qzss_dcr_jma_minutes:
            return None, raw

        dt_y = self.report_time.year
        dt_mo = self.report_time.month
        if dt_d - self.report_time.day > 15:
            if dt_mo == 1:
                dt_mo = 12
                dt_y -= 1
            else:
                dt_mo -= 1
        elif self.report_time.day - dt_d > 15:
            if dt_mo == 12:
                dt_mo = 1
                dt_y += 1
            else:
                dt_mo += 1
        if dt_d > monthrange(dt_y, dt_mo)[1]:  # e.g. the 31st taken as a day of February
            return None, raw

        return datetime(year=dt_y,
                        month=dt_mo,
                        day=dt_d,
                        hour=dt_h,
                        minute=dt_mi,
                        tzinfo=UTC), raw

    def extract_local_government(self, slider: int) -> tuple[str, int]:
        lg = self.extract_field(slider, 23)
        return qzss_dcr_jma_local_government[lg], lg

    def extract_notification_on_disaster_prevention_fields(self, slider: int) -> tuple[list[str], list[int]]:
        notifications: list[str] = []
        cos: list[int] = []
        for i in range(3):
            co = self.extract_field(slider + i * 9, 9)
            if co == 0:
                break
            notifications.append(qzss_dcr_jma_notification_on_disaster_prevention[co])
            cos.append(co)
        return notifications, cos

    def extract_lat_lon_field(self, slider: int) -> tuple[str, Coordinates]:
        coordinates: Coordinates = {
            'lat_ns': self.extract_field(slider, 1),
            'lat_d': self.extract_field(slider + 1, 7),
            'lat_m': self.extract_field(slider + 8, 6),
            'lat_s': self.extract_field(slider + 14, 6),
            'lon_ew': self.extract_field(slider + 20, 1),
            'lon_d': self.extract_field(slider + 21, 8),
            'lon_m': self.extract_field(slider + 29, 6),
            'lon_s': self.extract_field(slider + 35, 6),
        }
        if (coordinates['lat_d'] in qzss_dcr_jma_latitude_degrees
                and coordinates['lat_m'] in qzss_dcr_jma_latitude_and_longitude_minutes
                and coordinates['lat_s'] in qzss_dcr_jma_latitude_and_longitude_seconds
                and coordinates['lon_d'] in qzss_dcr_jma_longitude_degrees
                and coordinates['lon_m'] in qzss_dcr_jma_latitude_and_longitude_minutes
                and coordinates['lon_s'] in qzss_dcr_jma_latitude_and_longitude_seconds):
            return QzssDcReportJmaBase.convert_lat_lon_to_str(coordinates), coordinates
        # with one part outside its range, the other parts cannot be trusted as a position either
        return qzss_dcr_jma_latitude_and_longitude_undefined % self.extract_field(slider, 41), coordinates

    def extract_depth_field(self, slider: int) -> tuple[str, int]:
        de = self.extract_field(slider, 9)
        return qzss_dcr_jma_depth_of_hypocenter[de], de

    def extract_magnitude_field(self, slider: int, magnitudes: QzssDcrDefinition[int, str]) -> tuple[str, int]:
        ma = self.extract_field(slider, 7)
        return magnitudes[ma], ma

    def extract_seismic_epicenter_field(self, slider: int) -> tuple[str, int]:
        ep = self.extract_field(slider, 10)
        return qzss_dcr_jma_epicenter_and_hypocenter[ep], ep

    def extract_expected_tsunami_arrival_time_raw(self, slider: int) -> DayHourMinute:
        return {'day': self.extract_field(slider, 1),
                'hour': self.extract_field(slider + 1, 5),
                'minute': self.extract_field(slider + 6, 6)}

    def extract_expected_tsunami_arrival_time_field(self, slider: int) -> tuple[datetime | None, DayHourMinute, str]:
        """Expected arrival time of JMA-DC Report (Tsunami) with its raw values and type."""
        raw = self.extract_expected_tsunami_arrival_time_raw(slider)
        if (raw['hour'], raw['minute']) == (31, 63):  # has arrived (estimated or observed)
            return None, raw, '津波到達中と推測'
        if (raw['day'], raw['hour'], raw['minute']) == (0, 30, 62):  # no data
            return None, raw, '該当情報なし'
        arrival_time = self.extract_expected_tsunami_arrival_time(slider)
        if arrival_time is None:
            return None, raw, qzss_dcr_jma_expected_tsunami_arrival_time_undefined % self.extract_field(slider, 12)
        return arrival_time, raw, '津波の到達予想時刻'

    def extract_northwest_pacific_tsunami_arrival_time_field(self, slider: int) -> tuple[datetime | None, DayHourMinute, str]:
        """Expected arrival time of JMA-DC Report (Northwest Pacific Tsunami) with its raw values and type."""
        raw = self.extract_expected_tsunami_arrival_time_raw(slider)
        if (raw['hour'], raw['minute']) == (31, 63):  # has arrived or the arrival time is unknown
            return None, raw, 'Arrived or Unknown'
        arrival_time = self.extract_expected_tsunami_arrival_time(slider)
        if arrival_time is None:
            return None, raw, qzss_dcr_jma_expected_tsunami_arrival_time_undefined_en % self.extract_field(slider, 12)
        return arrival_time, raw, 'Expected Tsunami Arrival Time'

    def extract_expected_tsunami_arrival_time(self, slider: int) -> datetime | None:
        """The arrival time, or None when the hour and minute are not a time."""
        raw = self.extract_expected_tsunami_arrival_time_raw(slider)
        if raw['hour'] not in qzss_dcr_jma_hours or raw['minute'] not in qzss_dcr_jma_minutes:
            return None

        ta_dt = self.report_time + timedelta(raw['day'])

        return datetime(year=ta_dt.year,
                        month=ta_dt.month,
                        day=ta_dt.day,
                        hour=raw['hour'],
                        minute=raw['minute'],
                        tzinfo=UTC)
