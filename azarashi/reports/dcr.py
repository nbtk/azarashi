"""The reports of a JMA-DC Report message (MT43)."""
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar

from .base import Coordinates, DayHourMinute, MessageBase
from ..definitions import qzss_dcr_jma_activity_time_undefined
from ..definitions import qzss_dcr_jma_occurrence_time_of_earthquake_undefined
from ..definitions import qzss_dcr_jma_page_number_and_total_page_undefined
from ..definitions import qzss_dcr_jma_page_numbers
from ..definitions import qzss_dcr_jma_total_pages
from ..definitions import qzss_dcr_jma_typhoon_reference_time_undefined
from ..exceptions import AzarashiInvalidMessageError

def _day_hour_minute_code(raw: DayHourMinute) -> int:
    """A time field of 16 bits (day 5, hour 5 and minute 6) as one number."""
    return raw['day'] << 11 | raw['hour'] << 6 | raw['minute']


class Base(MessageBase):
    def __init__(self,
                 version: int,
                 report_classification: str,
                 report_classification_en: str,
                 report_classification_no: int,
                 disaster_category: str,
                 disaster_category_en: str,
                 disaster_category_no: int,
                 report_time: datetime,
                 information_type: str,
                 information_type_en: str,
                 information_type_no: int,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.version = version
        self.report_classification = report_classification
        self.report_classification_en = report_classification_en
        self.report_classification_no = report_classification_no
        self.disaster_category = disaster_category
        self.disaster_category_en = disaster_category_en
        self.disaster_category_no = disaster_category_no
        self.report_time = report_time
        self.information_type = information_type
        self.information_type_en = information_type_en
        self.information_type_no = information_type_no

    def get_header(self) -> str:
        header = f'防災気象情報({self.disaster_category})' + \
                 f'({self.information_type})' + \
                 f'({self.report_classification})'
        if self.report_classification_no == 7:
            header += '\n*** これは訓練です ***'
        elif self.information_type_no == 2:
            header += '\n*** 取り消しされました ***'
        return header

    def get_header_en(self) -> str:
        header = f'JMA-DC Report ({self.disaster_category_en})' + \
                 f' ({self.information_type_en})' + \
                 f' ({self.report_classification_en})'
        if self.report_classification_no == 7:
            header += '\n*** TRAINING/TEST ***'
        elif self.information_type_no == 2:
            header += '\n*** CANCELLATION ***'
        return header

    def get_report_time_str(self, time_diff: int = 9) -> str:
        at = self.report_time + timedelta(hours=time_diff)
        return f'{at.month}月{at.day}日{at.hour}時{at.minute}分'

    def get_report_time_str_iso(self) -> str:
        return self.report_time.strftime('--%m-%dT%H:%MZ')

    @staticmethod
    def convert_dt_to_str(dt: datetime, time_diff: int = 9) -> str:
        dt += timedelta(hours=time_diff)
        return f'{dt.day}日{dt.hour}時{dt.minute}分'

    @classmethod
    def _convert_time_to_str(cls, dt: datetime | None, raw: DayHourMinute, undefined: str) -> str:
        return cls.convert_dt_to_str(dt) if dt is not None else undefined % _day_hour_minute_code(raw)

    @staticmethod
    def convert_dt_to_str_iso(dt: datetime) -> str:
        return dt.strftime('---%dT%H:%MZ')

    def convert_dt_to_ambiguous_time_str(self, td: datetime, du: int, time_diff: int = 9) -> str:
        lt = td + timedelta(hours=time_diff)
        try:
            return [f'{lt.month}月{lt.day}日{lt.hour}時{lt.minute}分',  # No ambiguity
                    f'{lt.month}月{lt.day}日{lt.hour}時{lt.minute}分頃',
                    # Approximate time(equivalent to Approximate time (minute))
                    f'{lt.month}月{lt.day}日{lt.hour}時{lt.minute}分頃',  # Approximate time(second)
                    f'{lt.month}月{lt.day}日{lt.hour}時{lt.minute}分頃',  # Approximate time(minute)
                    f'{lt.month}月{lt.day}日{lt.hour}時頃',  # Approximate time(hour)
                    f'{td.month}月{td.day}日頃',  # Approximate time(day): only the UTC day is valid, so it stays in UTC
                    f'{lt.month}月頃',  # Approximate time(month)
                    f'{lt.year}年頃',  # Approximate time(year)
                    ][du]
        except IndexError as err:
            raise AzarashiInvalidMessageError(
                f'Undefined JMA Ambiguity of Activity Time: {du}',
                self) from err

    @staticmethod
    def convert_lat_lon_to_str(coordinates: Coordinates) -> str:
        return f'{"北緯" if coordinates["lat_ns"] == 0 else "南緯"}' + \
            f'{coordinates["lat_d"]}度' + \
            f'{coordinates["lat_m"]}分' + \
            f'{coordinates["lat_s"]}秒 ' + \
            f'{"東経" if coordinates["lon_ew"] == 0 else "西経"}' + \
            f'{coordinates["lon_d"]}度' + \
            f'{coordinates["lon_m"]}分' + \
            f'{coordinates["lon_s"]}秒'


class EarthquakeEarlyWarning(Base):
    def __init__(self,
                 long_period_ground_motion_lower_limit: str | None,
                 long_period_ground_motion_lower_limit_raw: int,
                 long_period_ground_motion_upper_limit: str | None,
                 long_period_ground_motion_upper_limit_raw: int,
                 notifications_on_disaster_prevention: list[str],
                 notifications_on_disaster_prevention_raw: list[int],
                 occurrence_time_of_earthquake: datetime | None,
                 occurrence_time_of_earthquake_raw: DayHourMinute,
                 depth_of_hypocenter: str,
                 depth_of_hypocenter_raw: int,
                 magnitude: str,
                 magnitude_raw: int,
                 assumptive: bool,
                 seismic_epicenter: str,
                 seismic_epicenter_raw: int,
                 seismic_intensity_lower_limit: str,
                 seismic_intensity_lower_limit_raw: int,
                 seismic_intensity_upper_limit: str,
                 seismic_intensity_upper_limit_raw: int,
                 eew_forecast_regions: list[str],
                 eew_forecast_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.long_period_ground_motion_lower_limit = long_period_ground_motion_lower_limit
        self.long_period_ground_motion_lower_limit_raw = long_period_ground_motion_lower_limit_raw
        self.long_period_ground_motion_upper_limit = long_period_ground_motion_upper_limit
        self.long_period_ground_motion_upper_limit_raw = long_period_ground_motion_upper_limit_raw
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
        self.occurrence_time_of_earthquake_raw = occurrence_time_of_earthquake_raw
        self.depth_of_hypocenter = depth_of_hypocenter
        self.depth_of_hypocenter_raw = depth_of_hypocenter_raw
        self.magnitude = magnitude
        self.magnitude_raw = magnitude_raw
        self.assumptive = assumptive
        self.seismic_epicenter = seismic_epicenter
        self.seismic_epicenter_raw = seismic_epicenter_raw
        self.seismic_intensity_lower_limit = seismic_intensity_lower_limit
        self.seismic_intensity_lower_limit_raw = seismic_intensity_lower_limit_raw
        self.seismic_intensity_upper_limit = seismic_intensity_upper_limit
        self.seismic_intensity_upper_limit_raw = seismic_intensity_upper_limit_raw
        self.eew_forecast_regions = eew_forecast_regions
        self.eew_forecast_regions_raw = eew_forecast_regions_raw

    def __str__(self) -> str:
        occurred = self._convert_time_to_str(self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw,
                                             qzss_dcr_jma_occurrence_time_of_earthquake_undefined)
        report = f'{self.get_header()}\n' + \
                 '緊急地震速報\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        if self.assumptive is True:
            assumptive_str = '(仮定震源要素)'
        else:
            assumptive_str = ''

        report += f'\n\n発表時刻: {self.get_report_time_str()}\n\n' + \
                  f'震央地名: {self.seismic_epicenter}\n' + \
                  f'地震発生時刻: {occurred}\n' + \
                  f'深さ: {self.depth_of_hypocenter}{assumptive_str}\n' + \
                  f'マグニチュード: {self.magnitude}{assumptive_str}\n' + \
                  f'震度(下限): {self.seismic_intensity_lower_limit}\n' + \
                  f'震度(上限): {self.seismic_intensity_upper_limit}\n'
        if self.long_period_ground_motion_lower_limit is not None:
            report += f'長周期地震動階級(下限): {self.long_period_ground_motion_lower_limit}\n'
        if self.long_period_ground_motion_upper_limit is not None:
            report += f'長周期地震動階級(上限): {self.long_period_ground_motion_upper_limit}\n'
        report += '、'.join(self.eew_forecast_regions)
        return report


class Hypocenter(Base):
    def __init__(self,
                 notifications_on_disaster_prevention: list[str],
                 notifications_on_disaster_prevention_raw: list[int],
                 occurrence_time_of_earthquake: datetime | None,
                 occurrence_time_of_earthquake_raw: DayHourMinute,
                 depth_of_hypocenter: str,
                 depth_of_hypocenter_raw: int,
                 magnitude: str,
                 magnitude_raw: int,
                 seismic_epicenter: str,
                 seismic_epicenter_raw: int,
                 coordinates_of_hypocenter: str,
                 coordinates_of_hypocenter_raw: Coordinates,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
        self.occurrence_time_of_earthquake_raw = occurrence_time_of_earthquake_raw
        self.depth_of_hypocenter = depth_of_hypocenter
        self.depth_of_hypocenter_raw = depth_of_hypocenter_raw
        self.magnitude = magnitude
        self.magnitude_raw = magnitude_raw
        self.seismic_epicenter = seismic_epicenter
        self.seismic_epicenter_raw = seismic_epicenter_raw
        self.coordinates_of_hypocenter = coordinates_of_hypocenter
        self.coordinates_of_hypocenter_raw = coordinates_of_hypocenter_raw

    def __str__(self) -> str:
        occurred = self._convert_time_to_str(self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw,
                                             qzss_dcr_jma_occurrence_time_of_earthquake_undefined)
        report = f'{self.get_header()}\n' + \
                 f'{occurred}' + \
                 'ころ、地震がありました。\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        report += f'\n\n発表時刻: {self.get_report_time_str()}\n\n' + \
                  f'震央地名: {self.seismic_epicenter}\n' + \
                  f'緯度・経度: {self.coordinates_of_hypocenter}\n' + \
                  f'深さ: {self.depth_of_hypocenter}\n' + \
                  f'マグニチュード: {self.magnitude}'
        return report


class SeismicIntensity(Base):
    def __init__(self,
                 occurrence_time_of_earthquake: datetime | None,
                 occurrence_time_of_earthquake_raw: DayHourMinute,
                 seismic_intensities: list[str],
                 seismic_intensities_raw: list[int],
                 prefectures: list[str],
                 prefectures_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
        self.occurrence_time_of_earthquake_raw = occurrence_time_of_earthquake_raw
        self.seismic_intensities = seismic_intensities
        self.seismic_intensities_raw = seismic_intensities_raw
        self.prefectures = prefectures
        self.prefectures_raw = prefectures_raw

    def __str__(self) -> str:
        occurred = self._convert_time_to_str(self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw,
                                             qzss_dcr_jma_occurrence_time_of_earthquake_undefined)
        report = f'{self.get_header()}\n' + \
                 f'{occurred}' + \
                 'ころ、地震による強い揺れを感じました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.seismic_intensities)):
            report += f'\n\n震度: {self.seismic_intensities[i]}\n' + \
                      f'{self.prefectures[i]}'
        return report


#: The pages of an announcement are assembled in the class, which every stream and every thread shares,
#: and a report renders its text outside the lock that decoding holds, so both ends take this one.
_assembly_lock = threading.Lock()


class NankaiTroughEarthquake(Base):
    completed: ClassVar[bool] = False
    reports: ClassVar[dict[int, 'NankaiTroughEarthquake']] = {}  # page number -> page of the announcement being assembled
    announcement: ClassVar[tuple[datetime, int, int, int, int] | None] = None  # identifies the announcement being assembled

    def __init__(self,
                 information_serial_code: str,
                 information_serial_code_raw: int,
                 text_information: bytes,
                 page_number: int,
                 total_page: int,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.information_serial_code = information_serial_code
        self.information_serial_code_raw = information_serial_code_raw
        self.text_information = text_information
        self.page_number = page_number
        self.total_page = total_page

        cls = self.__class__
        if not self._has_page_position():
            return  # a page that cannot be placed must not break the announcement being assembled
        with _assembly_lock:
            if cls.announcement is not None and self._get_announcement() != cls.announcement:
                if self.report_time < cls.announcement[0]:
                    return  # a late page of an older announcement must not break the newer one
                cls.completed = False  # a newer announcement replaces the partial one
                cls.reports = {}

            ex_report = cls.reports.get(self.page_number)
            if ex_report is not None:
                if ex_report == self:
                    return
                else:
                    cls.completed = False
                    cls.reports = {}

            cls.announcement = self._get_announcement()
            cls.reports.update({self.page_number: self})
            if all(page in cls.reports for page in range(1, self.total_page + 1)):
                cls.completed = True

    def _has_page_position(self) -> bool:
        """Whether the page number and the total page place this page in the text."""
        return (self.page_number in qzss_dcr_jma_page_numbers and self.total_page in qzss_dcr_jma_total_pages
                and self.page_number <= self.total_page)

    def _get_announcement(self) -> tuple[datetime, int, int, int, int]:
        return (self.report_time,
                self.report_classification_no,
                self.information_type_no,
                self.information_serial_code_raw,
                self.total_page)

    def extract_text_information(self) -> str:
        cls = self.__class__
        if not self._has_page_position():
            return qzss_dcr_jma_page_number_and_total_page_undefined % (self.page_number << 6 | self.total_page)
        with _assembly_lock:  # a page of a newer announcement must not empty the pages while they are read
            if self._get_announcement() != cls.announcement:
                return f'受信中 ({self.page_number}) [-/{self.total_page}]'
            if cls.completed is not True:
                return f'受信中 ({self.page_number}) [{len(cls.reports)}/{self.total_page}]'

            msg_bytes = b''
            for i in range(1, self.total_page + 1):
                msg_bytes += cls.reports[i].text_information

        return msg_bytes.replace(b'\x00', b'').decode('utf-8', errors='ignore')  # a Te of 0 is no character

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 '南海トラフ地震に関連する情報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n' + \
                 f'地震関連情報: {self.information_serial_code}\n' + \
                 f'{self.extract_text_information()}'
        return report


@dataclass
class TsunamiForecast:
    """One region's forecast, copied from a Tsunami report at access time."""

    region: str
    region_code: int
    height: str
    height_code: int
    arrival_time: datetime | None
    arrival_time_raw: DayHourMinute
    arrival_time_type: str


class Tsunami(Base):
    def __init__(self,
                 notifications_on_disaster_prevention: list[str],
                 notifications_on_disaster_prevention_raw: list[int],
                 tsunami_warning_code: str,
                 tsunami_warning_code_raw: int,
                 expected_tsunami_arrival_times: list[datetime | None],
                 expected_tsunami_arrival_times_raw: list[DayHourMinute],
                 expected_tsunami_arrival_time_types: list[str],
                 tsunami_heights: list[str],
                 tsunami_heights_raw: list[int],
                 tsunami_forecast_regions: list[str],
                 tsunami_forecast_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.tsunami_warning_code = tsunami_warning_code
        self.tsunami_warning_code_raw = tsunami_warning_code_raw
        self.expected_tsunami_arrival_times = expected_tsunami_arrival_times
        self.expected_tsunami_arrival_times_raw = expected_tsunami_arrival_times_raw
        self.expected_tsunami_arrival_time_types = expected_tsunami_arrival_time_types
        self.tsunami_heights = tsunami_heights
        self.tsunami_heights_raw = tsunami_heights_raw
        self.tsunami_forecast_regions = tsunami_forecast_regions
        self.tsunami_forecast_regions_raw = tsunami_forecast_regions_raw

    @property
    def forecasts(self) -> tuple[TsunamiForecast, ...]:
        """A detached snapshot; inconsistent source-list lengths raise ValueError."""
        return tuple(
            TsunamiForecast(region, region_code, height, height_code, arrival, raw.copy(), kind)
            for region, region_code, height, height_code, arrival, raw, kind in zip(
                self.tsunami_forecast_regions, self.tsunami_forecast_regions_raw,
                self.tsunami_heights, self.tsunami_heights_raw,
                self.expected_tsunami_arrival_times, self.expected_tsunami_arrival_times_raw,
                self.expected_tsunami_arrival_time_types, strict=True)
        )

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 f'{self.tsunami_warning_code}を発表しました。\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        report += f'\n\n発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.expected_tsunami_arrival_times)):
            arrival_time = self.expected_tsunami_arrival_times[i]
            if arrival_time is None:
                ta = self.expected_tsunami_arrival_time_types[i]
            else:
                ta = self.convert_dt_to_str(arrival_time)
            report += f'\n\n津波到達予想時刻: {ta}\n' + \
                      f'津波の高さ: {self.tsunami_heights[i]}\n' + \
                      f'{self.tsunami_forecast_regions[i]}'
        return report


class NorthwestPacificTsunami(Base):
    def __init__(self,
                 tsunamigenic_potential_en: str,
                 tsunamigenic_potential_raw: int,
                 expected_tsunami_arrival_times: list[datetime | None],
                 expected_tsunami_arrival_times_raw: list[DayHourMinute],
                 expected_tsunami_arrival_time_types_en: list[str],
                 tsunami_heights_en: list[str],
                 tsunami_heights_raw: list[int],
                 coastal_regions_en: list[str],
                 coastal_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tsunamigenic_potential_en = tsunamigenic_potential_en
        self.tsunamigenic_potential_raw = tsunamigenic_potential_raw
        self.expected_tsunami_arrival_times = expected_tsunami_arrival_times
        self.expected_tsunami_arrival_times_raw = expected_tsunami_arrival_times_raw
        self.expected_tsunami_arrival_time_types_en = expected_tsunami_arrival_time_types_en
        self.tsunami_heights_en = tsunami_heights_en
        self.tsunami_heights_raw = tsunami_heights_raw
        self.coastal_regions_en = coastal_regions_en
        self.coastal_regions_raw = coastal_regions_raw

    def __str__(self) -> str:
        report = f'{self.get_header_en()}\n' + \
                 f'{self.tsunamigenic_potential_en}.\n\n' + \
                 f'Time of Issue: {self.get_report_time_str_iso()}'

        for i in range(len(self.expected_tsunami_arrival_times)):
            arrival_time = self.expected_tsunami_arrival_times[i]
            if arrival_time is None:
                ta = self.expected_tsunami_arrival_time_types_en[i]
            else:
                ta = self.convert_dt_to_str_iso(arrival_time)
            report += f'\n\nExpected Tsunami Arrival Time: {ta}\n' + \
                      f'Tsunami Height: {self.tsunami_heights_en[i]}\n' + \
                      f'Coastal Region: {self.coastal_regions_en[i]}'
        return report


class Volcano(Base):
    def __init__(self,
                 ambiguity_of_activity_time_no: int,
                 activity_time: datetime | None,
                 activity_time_raw: DayHourMinute,
                 volcanic_warning_code: str,
                 volcanic_warning_code_raw: int,
                 volcano_name: str,
                 volcano_name_raw: int,
                 local_governments: list[str],
                 local_governments_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ambiguity_of_activity_time_no = ambiguity_of_activity_time_no
        self.activity_time = activity_time
        self.activity_time_raw = activity_time_raw
        self.volcanic_warning_code = volcanic_warning_code
        self.volcanic_warning_code_raw = volcanic_warning_code_raw
        self.volcano_name = volcano_name
        self.volcano_name_raw = volcano_name_raw
        self.local_governments = local_governments
        self.local_governments_raw = local_governments_raw

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 '火山に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'火山名: {self.volcano_name}\n'
        du = self.ambiguity_of_activity_time_no
        if du < 6:  # an approximate month or year leaves no part of the activity time to show
            if self.activity_time is not None:
                activity_time = self.convert_dt_to_ambiguous_time_str(self.activity_time, du)
            else:
                activity_time = qzss_dcr_jma_activity_time_undefined % _day_hour_minute_code(self.activity_time_raw)
            report += f'日時: {activity_time}\n'
        report += f'現象: {self.volcanic_warning_code}\n\n'

        report += '、'.join(self.local_governments)
        return report


class AshFall(Base):
    def __init__(self,
                 activity_time: datetime | None,
                 activity_time_raw: DayHourMinute,
                 ash_fall_warning_type: str,
                 ash_fall_warning_type_raw: int,
                 volcano_name: str,
                 volcano_name_raw: int,
                 expected_ash_fall_times: list[str],
                 expected_ash_fall_times_raw: list[int],
                 ash_fall_warning_codes: list[str],
                 ash_fall_warning_codes_raw: list[int],
                 local_governments: list[str],
                 local_governments_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.activity_time = activity_time
        self.activity_time_raw = activity_time_raw
        self.ash_fall_warning_type = ash_fall_warning_type
        self.ash_fall_warning_type_raw = ash_fall_warning_type_raw
        self.volcano_name = volcano_name
        self.volcano_name_raw = volcano_name_raw
        self.expected_ash_fall_times = expected_ash_fall_times
        self.expected_ash_fall_times_raw = expected_ash_fall_times_raw
        self.ash_fall_warning_codes = ash_fall_warning_codes
        self.ash_fall_warning_codes_raw = ash_fall_warning_codes_raw
        self.local_governments = local_governments
        self.local_governments_raw = local_governments_raw

    def __str__(self) -> str:
        activity_time = self._convert_time_to_str(self.activity_time, self.activity_time_raw,
                                                  qzss_dcr_jma_activity_time_undefined)
        report = f'{self.get_header()}\n' + \
                 '降灰に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'{self.ash_fall_warning_type}\n' + \
                 f'火山名: {self.volcano_name}\n' + \
                 f'日時: {activity_time}'

        for i in range(len(self.expected_ash_fall_times)):
            report += '\n\n' + \
                      f'基点時刻からの時間: {self.expected_ash_fall_times[i]}\n' + \
                      f'現象: {self.ash_fall_warning_codes[i]}\n' + \
                      f'{self.local_governments[i]}'
        return report


class Weather(Base):
    def __init__(self,
                 weather_warning_state: str,
                 weather_warning_state_raw: int,
                 weather_related_disaster_sub_categories: list[str],
                 weather_related_disaster_sub_categories_raw: list[int],
                 weather_forecast_regions: list[str],
                 weather_forecast_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.weather_warning_state = weather_warning_state
        self.weather_warning_state_raw = weather_warning_state_raw
        self.weather_related_disaster_sub_categories = weather_related_disaster_sub_categories
        self.weather_related_disaster_sub_categories_raw = weather_related_disaster_sub_categories_raw
        self.weather_forecast_regions = weather_forecast_regions
        self.weather_forecast_regions_raw = weather_forecast_regions_raw

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 '気象に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.weather_related_disaster_sub_categories)):
            report += f'\n\n警報等情報要素: {self.weather_related_disaster_sub_categories[i]}' + \
                      f'({self.weather_warning_state})\n' + \
                      f'{self.weather_forecast_regions[i]}'
        return report


class Flood(Base):
    def __init__(self,
                 flood_warning_levels: list[str],
                 flood_warning_levels_raw: list[int],
                 flood_forecast_regions: list[str],
                 flood_forecast_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.flood_warning_levels = flood_warning_levels
        self.flood_warning_levels_raw = flood_warning_levels_raw
        self.flood_forecast_regions = flood_forecast_regions
        self.flood_forecast_regions_raw = flood_forecast_regions_raw

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 '河川の氾濫に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.flood_warning_levels)):
            report += f'\n\n警報レベル: {self.flood_warning_levels[i]}\n' + \
                      f'{self.flood_forecast_regions[i]}'
        return report


class Marine(Base):
    def __init__(self,
                 marine_warning_codes: list[str],
                 marine_warning_codes_raw: list[int],
                 marine_forecast_regions: list[str],
                 marine_forecast_regions_raw: list[int],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.marine_warning_codes = marine_warning_codes
        self.marine_warning_codes_raw = marine_warning_codes_raw
        self.marine_forecast_regions = marine_forecast_regions
        self.marine_forecast_regions_raw = marine_forecast_regions_raw

    def __str__(self) -> str:
        report = f'{self.get_header()}\n' + \
                 '海上警報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.marine_warning_codes)):
            report += f'\n\n警報等情報要素: {self.marine_warning_codes[i]}\n' + \
                      f'{self.marine_forecast_regions[i]}'
        return report


class Typhoon(Base):
    def __init__(self,
                 reference_time: datetime | None,
                 reference_time_raw: DayHourMinute,
                 reference_time_type: str,
                 reference_time_type_raw: int,
                 elapsed_time_from_reference_time: str,
                 elapsed_time_from_reference_time_raw: int,
                 typhoon_number: str,
                 typhoon_number_raw: int,
                 typhoon_scale_category: str,
                 typhoon_scale_category_raw: int,
                 typhoon_intensity_category: str,
                 typhoon_intensity_category_raw: int,
                 coordinates_of_typhoon: str,
                 coordinates_of_typhoon_raw: Coordinates,
                 central_pressure: str,
                 central_pressure_raw: int,
                 maximum_wind_speed: str,
                 maximum_wind_speed_raw: int,
                 maximum_gust_wind_speed: str,
                 maximum_gust_wind_speed_raw: int,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.reference_time = reference_time
        self.reference_time_raw = reference_time_raw
        self.reference_time_type = reference_time_type
        self.reference_time_type_raw = reference_time_type_raw
        # the time elapsed from the analysis
        self.elapsed_time_from_reference_time = elapsed_time_from_reference_time
        self.elapsed_time_from_reference_time_raw = elapsed_time_from_reference_time_raw
        self.typhoon_number = typhoon_number
        self.typhoon_number_raw = typhoon_number_raw
        self.typhoon_scale_category = typhoon_scale_category
        self.typhoon_scale_category_raw = typhoon_scale_category_raw
        self.typhoon_intensity_category = typhoon_intensity_category
        self.typhoon_intensity_category_raw = typhoon_intensity_category_raw
        self.coordinates_of_typhoon = coordinates_of_typhoon
        self.coordinates_of_typhoon_raw = coordinates_of_typhoon_raw
        self.central_pressure = central_pressure
        self.central_pressure_raw = central_pressure_raw
        self.maximum_wind_speed = maximum_wind_speed
        self.maximum_wind_speed_raw = maximum_wind_speed_raw
        self.maximum_gust_wind_speed = maximum_gust_wind_speed
        self.maximum_gust_wind_speed_raw = maximum_gust_wind_speed_raw

    def __str__(self) -> str:
        reference_time = self._convert_time_to_str(self.reference_time, self.reference_time_raw,
                                                   qzss_dcr_jma_typhoon_reference_time_undefined)
        report = f'{self.get_header()}\n' + \
                 '台風解析・予報情報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'台風番号: {self.typhoon_number}\n' + \
                 f'基点時刻: {reference_time}\n' + \
                 f'基点時刻分類: {self.reference_time_type}\n' + \
                 f'情報の基点時刻(実況)からの経過時間: {self.elapsed_time_from_reference_time}\n' + \
                 f'大きさ: {self.typhoon_scale_category}\n' + \
                 f'強さ: {self.typhoon_intensity_category}\n' + \
                 f'緯度・経度: {self.coordinates_of_typhoon}\n' + \
                 f'中心気圧: {self.central_pressure}\n' + \
                 f'最大風速: {self.maximum_wind_speed}\n' + \
                 f'最大瞬間風速: {self.maximum_gust_wind_speed}'
        return report
