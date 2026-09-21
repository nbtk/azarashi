from calendar import isleap
from calendar import monthrange
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from ...definitions.qzss.dcr.ash_fall_warning_code import ash_fall_warning_code
from ...definitions.qzss.dcr.ash_fall_warning_type import ash_fall_warning_type
from ...definitions.qzss.dcr.coastal_region import coastal_region_en
from ...definitions.qzss.dcr.day_hour_minute import days
from ...definitions.qzss.dcr.depth_of_hypocenter import depth_of_hypocenter
from ...definitions.qzss.dcr.disaster_category import disaster_category
from ...definitions.qzss.dcr.disaster_category import disaster_category_en
from ...definitions.qzss.dcr.eew_forecast_region import eew_forecast_region
from ...definitions.qzss.dcr.eew_magnitude import eew_magnitude
from ...definitions.qzss.dcr.epicenter_and_hypocenter import epicenter_and_hypocenter
from ...definitions.qzss.dcr.expected_ash_fall_time import expected_ash_fall_time
from ...definitions.qzss.dcr.day_hour_minute import expected_tsunami_arrival_time_undefined
from ...definitions.qzss.dcr.day_hour_minute import expected_tsunami_arrival_time_undefined_en
from ...definitions.qzss.dcr.flood_forecast_region import flood_forecast_region
from ...definitions.qzss.dcr.flood_warning_level import flood_warning_level
from ...definitions.qzss.dcr.day_hour_minute import hours
from ...definitions.qzss.dcr.hypocenter_magnitude import hypocenter_magnitude
from ...definitions.qzss.dcr.information_serial_code import information_serial_code
from ...definitions.qzss.dcr.information_type import information_type
from ...definitions.qzss.dcr.information_type import information_type_en
from ...definitions.qzss.dcr.latitude_and_longitude import latitude_and_longitude_minutes
from ...definitions.qzss.dcr.latitude_and_longitude import latitude_and_longitude_seconds
from ...definitions.qzss.dcr.latitude_and_longitude import latitude_and_longitude_undefined
from ...definitions.qzss.dcr.latitude_and_longitude import latitude_degrees
from ...definitions.qzss.dcr.local_government import local_government
from ...definitions.qzss.dcr.long_period_ground_motion_lower_limit import long_period_ground_motion_lower_limit
from ...definitions.qzss.dcr.long_period_ground_motion_upper_limit import long_period_ground_motion_upper_limit
from ...definitions.qzss.dcr.latitude_and_longitude import longitude_degrees
from ...definitions.qzss.dcr.marine_forecast_region import marine_forecast_region
from ...definitions.qzss.dcr.marine_warning_code import marine_warning_code
from ...definitions.qzss.dcr.day_hour_minute import minutes
from ...definitions.qzss.dcr.northwest_pacific_tsunami_height import northwest_pacific_tsunami_height_en
from ...definitions.qzss.dcr.notification_on_disaster_prevention import notification_on_disaster_prevention
from ...definitions.qzss.dcr.prefecture import prefecture
from ...definitions.qzss.dcr.report_classification import report_classification
from ...definitions.qzss.dcr.report_classification import report_classification_en
from ...definitions.qzss.dcr.seismic_intensity import seismic_intensity
from ...definitions.qzss.dcr.seismic_intensity_lower_limit import seismic_intensity_lower_limit
from ...definitions.qzss.dcr.seismic_intensity_upper_limit import seismic_intensity_upper_limit
from ...definitions.qzss.dcr.tsunami_forecast_region import tsunami_forecast_region
from ...definitions.qzss.dcr.tsunami_height import tsunami_height
from ...definitions.qzss.dcr.tsunami_warning_code import tsunami_warning_code
from ...definitions.qzss.dcr.tsunamigenic_potential import tsunamigenic_potential_en
from ...definitions.qzss.dcr.typhoon_central_pressure import typhoon_central_pressure
from ...definitions.qzss.dcr.typhoon_elapsed_time_from_reference_time import typhoon_elapsed_time_from_reference_time
from ...definitions.qzss.dcr.typhoon_intensity_category import typhoon_intensity_category
from ...definitions.qzss.dcr.typhoon_maximum_gust_wind_speed import typhoon_maximum_gust_wind_speed
from ...definitions.qzss.dcr.typhoon_maximum_wind_speed import typhoon_maximum_wind_speed
from ...definitions.qzss.dcr.typhoon_number import typhoon_number
from ...definitions.qzss.dcr.typhoon_reference_time_type import typhoon_reference_time_type
from ...definitions.qzss.dcr.typhoon_scale_category import typhoon_scale_category
from ...definitions.qzss.dcr.volcanic_warning_code import volcanic_warning_code
from ...definitions.qzss.dcr.volcano_name import volcano_name
from ...definitions.qzss.dcr.weather_forecast_region import weather_forecast_region
from ...definitions.qzss.dcr.weather_related_disaster_sub_category import weather_related_disaster_sub_category
from ...definitions.qzss.dcr.weather_warning_state import weather_warning_state
from ...definitions.code_table import CodeTable
from ...exceptions import AzarashiInvalidMessageError
from ...reports import Report
from ...reports import dcr
from ...reports.base import Coordinates
from ...reports.base import DayHourMinute
from .base import ContextDecoder, MessageDecoder
from .context import Jma


class Decoder(MessageDecoder):
    def decode(self) -> Report:
        self.version = self.extract_field(214, 6)
        if self.version != 1:
            raise AzarashiInvalidMessageError(
                f'Unsupported JMA-DC Report Version: {self.version}',
                self)

        rc = self.extract_field(14, 3)
        self.report_classification = report_classification[rc]
        self.report_classification_en = report_classification_en[rc]
        self.report_classification_no = rc

        dc = self.extract_field(17, 4)
        try:
            self.disaster_category = disaster_category[dc]
            self.disaster_category_en = disaster_category_en[dc]
        except KeyError as err:
            raise AzarashiInvalidMessageError(
                f'Undefined Disaster Category: {dc}',
                self) from err
        self.disaster_category_no = dc

        at_mo = self.extract_field(21, 4)
        if at_mo < 1 or at_mo > 12:
            raise AzarashiInvalidMessageError(
                f'Invalid Report Time: {at_mo} as month',
                self)
        at_d = self.extract_field(25, 5)
        if at_d < 1 or at_d > 31:
            raise AzarashiInvalidMessageError(
                f'Invalid Report Time: {at_d} as day',
                self)
        at_h = self.extract_field(30, 5)
        if at_h > 23:
            raise AzarashiInvalidMessageError(
                f'Invalid Report Time: {at_h} as hour',
                self)
        at_mi = self.extract_field(35, 6)
        if at_mi > 59:
            raise AzarashiInvalidMessageError(
                f'Invalid Report Time: {at_mi} as minute',
                self)

        at_y = self.timestamp.year
        if at_mo - self.timestamp.month > 6:
            at_y -= 1
        elif self.timestamp.month - at_mo > 6:
            at_y += 1

        if at_mo == 2 and at_d == 29 and not isleap(at_y):  # take the leap day closest to the reception time
            earlier = next(y for y in range(at_y - 1, at_y - 9, -1) if isleap(y))
            later = next(y for y in range(at_y + 1, at_y + 9) if isleap(y))
            at_y = min(earlier, later,
                       key=lambda y: abs(datetime(y, 2, 29, at_h, at_mi, tzinfo=UTC) - self.timestamp))
        if at_d > monthrange(at_y, at_mo)[1]:
            raise AzarashiInvalidMessageError(
                f'Invalid Report Time: {at_d} as day of month {at_mo}',
                self)

        self.report_time = datetime(year=at_y,
                                    month=at_mo,
                                    day=at_d,
                                    hour=at_h,
                                    minute=at_mi,
                                    tzinfo=UTC)

        it = self.extract_field(41, 2)
        self.information_type = information_type[it]
        self.information_type_en = information_type_en[it]
        self.information_type_no = it

        next_decoder: type[Common]
        if dc == 1:
            next_decoder = EarthquakeEarlyWarning
        elif dc == 2:
            next_decoder = Hypocenter
        elif dc == 3:
            next_decoder = SeismicIntensity
        elif dc == 4:
            next_decoder = NankaiTroughEarthquake
        elif dc == 5:
            next_decoder = Tsunami
        elif dc == 6:
            next_decoder = NorthwestPacificTsunami
        elif dc == 8:
            next_decoder = Volcano
        elif dc == 9:
            next_decoder = AshFall
        elif dc == 10:
            next_decoder = Weather
        elif dc == 11:
            next_decoder = Flood
        elif dc == 12:
            next_decoder = Typhoon
        elif dc == 14:
            next_decoder = Marine
        else:
            raise AzarashiInvalidMessageError(
                f'Unsupported Disaster Category: {self.disaster_category}',
                self)

        return next_decoder(Jma(
            **self.context.params(),
            version=self.version,
            report_classification=self.report_classification,
            report_classification_en=self.report_classification_en,
            report_classification_no=self.report_classification_no,
            disaster_category=self.disaster_category,
            disaster_category_en=self.disaster_category_en,
            disaster_category_no=self.disaster_category_no,
            report_time=self.report_time,
            information_type=self.information_type,
            information_type_en=self.information_type_en,
            information_type_no=self.information_type_no,
        )).decode()


class Common(ContextDecoder[Jma]):
    @property
    def preamble(self) -> str:
        return self.context.preamble

    @property
    def message_type(self) -> str:
        return self.context.message_type

    @property
    def version(self) -> int:
        return self.context.version

    @property
    def report_classification(self) -> str:
        return self.context.report_classification

    @property
    def report_classification_en(self) -> str:
        return self.context.report_classification_en

    @property
    def report_classification_no(self) -> int:
        return self.context.report_classification_no

    @property
    def disaster_category(self) -> str:
        return self.context.disaster_category

    @property
    def disaster_category_en(self) -> str:
        return self.context.disaster_category_en

    @property
    def disaster_category_no(self) -> int:
        return self.context.disaster_category_no

    @property
    def report_time(self) -> datetime:
        return self.context.report_time

    @property
    def information_type(self) -> str:
        return self.context.information_type

    @property
    def information_type_en(self) -> str:
        return self.context.information_type_en

    @property
    def information_type_no(self) -> int:
        return self.context.information_type_no

    def extract_day_hour_min_raw(self, slider: int) -> DayHourMinute:
        return {'day': self.extract_field(slider, 5),
                'hour': self.extract_field(slider + 5, 5),
                'minute': self.extract_field(slider + 10, 6)}

    def extract_day_hour_min_field(self, slider: int) -> tuple[datetime | None, DayHourMinute]:
        raw = self.extract_day_hour_min_raw(slider)
        dt_d, dt_h, dt_mi = raw['day'], raw['hour'], raw['minute']
        if dt_d not in days or dt_h not in hours or dt_mi not in minutes:
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
        return local_government[lg], lg

    def extract_notification_on_disaster_prevention_fields(self, slider: int) -> tuple[list[str], list[int]]:
        notifications: list[str] = []
        cos: list[int] = []
        for i in range(3):
            co = self.extract_field(slider + i * 9, 9)
            if co == 0:
                break
            notifications.append(notification_on_disaster_prevention[co])
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
        if (coordinates['lat_d'] in latitude_degrees
                and coordinates['lat_m'] in latitude_and_longitude_minutes
                and coordinates['lat_s'] in latitude_and_longitude_seconds
                and coordinates['lon_d'] in longitude_degrees
                and coordinates['lon_m'] in latitude_and_longitude_minutes
                and coordinates['lon_s'] in latitude_and_longitude_seconds):
            return dcr.Base.convert_lat_lon_to_str(coordinates), coordinates
        # with one part outside its range, the other parts cannot be trusted as a position either
        return latitude_and_longitude_undefined % self.extract_field(slider, 41), coordinates

    def extract_depth_field(self, slider: int) -> tuple[str, int]:
        de = self.extract_field(slider, 9)
        return depth_of_hypocenter[de], de

    def extract_magnitude_field(self, slider: int, magnitudes: CodeTable[int, str]) -> tuple[str, int]:
        ma = self.extract_field(slider, 7)
        return magnitudes[ma], ma

    def extract_seismic_epicenter_field(self, slider: int) -> tuple[str, int]:
        ep = self.extract_field(slider, 10)
        return epicenter_and_hypocenter[ep], ep

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
            return None, raw, expected_tsunami_arrival_time_undefined % self.extract_field(slider, 12)
        return arrival_time, raw, '津波の到達予想時刻'

    def extract_northwest_pacific_tsunami_arrival_time_field(self, slider: int) -> tuple[datetime | None, DayHourMinute, str]:
        """Expected arrival time of JMA-DC Report (Northwest Pacific Tsunami) with its raw values and type."""
        raw = self.extract_expected_tsunami_arrival_time_raw(slider)
        if (raw['hour'], raw['minute']) == (31, 63):  # has arrived or the arrival time is unknown
            return None, raw, 'Arrived or Unknown'
        arrival_time = self.extract_expected_tsunami_arrival_time(slider)
        if arrival_time is None:
            return None, raw, expected_tsunami_arrival_time_undefined_en % self.extract_field(slider, 12)
        return arrival_time, raw, 'Expected Tsunami Arrival Time'

    def extract_expected_tsunami_arrival_time(self, slider: int) -> datetime | None:
        """The arrival time, or None when the hour and minute are not a time."""
        raw = self.extract_expected_tsunami_arrival_time_raw(slider)
        if raw['hour'] not in hours or raw['minute'] not in minutes:
            return None

        ta_dt = self.report_time + timedelta(raw['day'])

        return datetime(year=ta_dt.year,
                        month=ta_dt.month,
                        day=ta_dt.day,
                        hour=raw['hour'],
                        minute=raw['minute'],
                        tzinfo=UTC)


class EarthquakeEarlyWarning(Common):
    def decode(self) -> dcr.EarthquakeEarlyWarning:
        lgll = self.extract_field(47, 3)
        self.long_period_ground_motion_lower_limit = long_period_ground_motion_lower_limit[lgll]
        self.long_period_ground_motion_lower_limit_raw = lgll

        lgul = self.extract_field(50, 3)
        self.long_period_ground_motion_upper_limit = long_period_ground_motion_upper_limit[lgul]
        self.long_period_ground_motion_upper_limit_raw = lgul

        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter, self.depth_of_hypocenter_raw = self.extract_depth_field(96)
        self.magnitude, self.magnitude_raw = self.extract_magnitude_field(105, eew_magnitude)
        self.seismic_epicenter, self.seismic_epicenter_raw = self.extract_seismic_epicenter_field(112)

        if self.depth_of_hypocenter_raw == 10 and self.magnitude_raw == 10:
            self.assumptive = True
        else:
            self.assumptive = False

        ll = self.extract_field(122, 4)
        self.seismic_intensity_lower_limit = seismic_intensity_lower_limit[ll]
        self.seismic_intensity_lower_limit_raw = ll

        ul = self.extract_field(126, 4)
        self.seismic_intensity_upper_limit = seismic_intensity_upper_limit[ul]
        self.seismic_intensity_upper_limit_raw = ul

        self.eew_forecast_regions: list[str] = []
        self.eew_forecast_regions_raw: list[int] = []
        for i in range(80):
            if self.extract_field(130 + i, 1) == 1:
                self.eew_forecast_regions.append(eew_forecast_region[i + 1])
                self.eew_forecast_regions_raw.append(i + 1)

        return dcr.EarthquakeEarlyWarning(
            **self.context.params(),
            long_period_ground_motion_lower_limit=self.long_period_ground_motion_lower_limit,
            long_period_ground_motion_lower_limit_raw=self.long_period_ground_motion_lower_limit_raw,
            long_period_ground_motion_upper_limit=self.long_period_ground_motion_upper_limit,
            long_period_ground_motion_upper_limit_raw=self.long_period_ground_motion_upper_limit_raw,
            notifications_on_disaster_prevention=self.notifications_on_disaster_prevention,
            notifications_on_disaster_prevention_raw=self.notifications_on_disaster_prevention_raw,
            occurrence_time_of_earthquake=self.occurrence_time_of_earthquake,
            occurrence_time_of_earthquake_raw=self.occurrence_time_of_earthquake_raw,
            depth_of_hypocenter=self.depth_of_hypocenter,
            depth_of_hypocenter_raw=self.depth_of_hypocenter_raw,
            magnitude=self.magnitude,
            magnitude_raw=self.magnitude_raw,
            assumptive=self.assumptive,
            seismic_epicenter=self.seismic_epicenter,
            seismic_epicenter_raw=self.seismic_epicenter_raw,
            seismic_intensity_lower_limit=self.seismic_intensity_lower_limit,
            seismic_intensity_lower_limit_raw=self.seismic_intensity_lower_limit_raw,
            seismic_intensity_upper_limit=self.seismic_intensity_upper_limit,
            seismic_intensity_upper_limit_raw=self.seismic_intensity_upper_limit_raw,
            eew_forecast_regions=self.eew_forecast_regions,
            eew_forecast_regions_raw=self.eew_forecast_regions_raw,
        )


class Hypocenter(Common):
    def decode(self) -> dcr.Hypocenter:
        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter, self.depth_of_hypocenter_raw = self.extract_depth_field(96)
        self.magnitude, self.magnitude_raw = self.extract_magnitude_field(105, hypocenter_magnitude)
        self.seismic_epicenter, self.seismic_epicenter_raw = self.extract_seismic_epicenter_field(112)
        self.coordinates_of_hypocenter, self.coordinates_of_hypocenter_raw = self.extract_lat_lon_field(122)
        return dcr.Hypocenter(
            **self.context.params(),
            notifications_on_disaster_prevention=self.notifications_on_disaster_prevention,
            notifications_on_disaster_prevention_raw=self.notifications_on_disaster_prevention_raw,
            occurrence_time_of_earthquake=self.occurrence_time_of_earthquake,
            occurrence_time_of_earthquake_raw=self.occurrence_time_of_earthquake_raw,
            depth_of_hypocenter=self.depth_of_hypocenter,
            depth_of_hypocenter_raw=self.depth_of_hypocenter_raw,
            magnitude=self.magnitude,
            magnitude_raw=self.magnitude_raw,
            seismic_epicenter=self.seismic_epicenter,
            seismic_epicenter_raw=self.seismic_epicenter_raw,
            coordinates_of_hypocenter=self.coordinates_of_hypocenter,
            coordinates_of_hypocenter_raw=self.coordinates_of_hypocenter_raw,
        )


class SeismicIntensity(Common):
    def decode(self) -> dcr.SeismicIntensity:
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(53)
        self.seismic_intensities: list[str] = []
        self.seismic_intensities_raw: list[int] = []
        self.prefectures: list[str] = []
        self.prefectures_raw: list[int] = []
        for i in range(16):
            offset = 69 + i * 9
            es = self.extract_field(offset, 3)
            pl = self.extract_field(offset + 3, 6)
            if es == 0 and pl == 0:
                break

            self.seismic_intensities.append(seismic_intensity[es])
            self.seismic_intensities_raw.append(es)

            self.prefectures.append(prefecture[pl])
            self.prefectures_raw.append(pl)

        return dcr.SeismicIntensity(
            **self.context.params(),
            occurrence_time_of_earthquake=self.occurrence_time_of_earthquake,
            occurrence_time_of_earthquake_raw=self.occurrence_time_of_earthquake_raw,
            seismic_intensities=self.seismic_intensities,
            seismic_intensities_raw=self.seismic_intensities_raw,
            prefectures=self.prefectures,
            prefectures_raw=self.prefectures_raw,
        )


class NankaiTroughEarthquake(Common):
    def decode(self) -> dcr.NankaiTroughEarthquake:
        ie = self.extract_field(53, 4)
        self.information_serial_code = information_serial_code[ie]
        self.information_serial_code_raw = ie

        te: list[int] = []
        for i in range(18):
            te.append(self.extract_field(57 + i * 8, 8))

        self.text_information = bytes(te)
        self.page_number = self.extract_field(201, 6)
        self.total_page = self.extract_field(207, 6)

        return dcr.NankaiTroughEarthquake(
            **self.context.params(),
            information_serial_code=self.information_serial_code,
            information_serial_code_raw=self.information_serial_code_raw,
            text_information=self.text_information,
            page_number=self.page_number,
            total_page=self.total_page,
        )


class Tsunami(Common):
    def decode(self) -> dcr.Tsunami:
        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        dw = self.extract_field(80, 4)
        self.tsunami_warning_code = tsunami_warning_code[dw]
        self.tsunami_warning_code_raw = dw

        self.expected_tsunami_arrival_times: list[datetime | None] = []
        self.expected_tsunami_arrival_times_raw: list[DayHourMinute] = []
        self.expected_tsunami_arrival_time_types: list[str] = []
        self.tsunami_heights: list[str] = []
        self.tsunami_heights_raw: list[int] = []
        self.tsunami_forecast_regions: list[str] = []
        self.tsunami_forecast_regions_raw: list[int] = []
        for i in range(5):
            offset = 84 + i * 26
            if self.extract_field(offset, 26) == 0:
                break

            ta, ta_raw, ta_type = self.extract_expected_tsunami_arrival_time_field(offset)
            self.expected_tsunami_arrival_times.append(ta)
            self.expected_tsunami_arrival_times_raw.append(ta_raw)
            self.expected_tsunami_arrival_time_types.append(ta_type)

            th = self.extract_field(offset + 12, 4)
            self.tsunami_heights.append(tsunami_height[th])
            self.tsunami_heights_raw.append(th)

            pl = self.extract_field(offset + 16, 10)
            self.tsunami_forecast_regions.append(tsunami_forecast_region[pl])
            self.tsunami_forecast_regions_raw.append(pl)

        return dcr.Tsunami(
            **self.context.params(),
            notifications_on_disaster_prevention=self.notifications_on_disaster_prevention,
            notifications_on_disaster_prevention_raw=self.notifications_on_disaster_prevention_raw,
            tsunami_warning_code=self.tsunami_warning_code,
            tsunami_warning_code_raw=self.tsunami_warning_code_raw,
            expected_tsunami_arrival_times=self.expected_tsunami_arrival_times,
            expected_tsunami_arrival_times_raw=self.expected_tsunami_arrival_times_raw,
            expected_tsunami_arrival_time_types=self.expected_tsunami_arrival_time_types,
            tsunami_heights=self.tsunami_heights,
            tsunami_heights_raw=self.tsunami_heights_raw,
            tsunami_forecast_regions=self.tsunami_forecast_regions,
            tsunami_forecast_regions_raw=self.tsunami_forecast_regions_raw,
        )


class NorthwestPacificTsunami(Common):
    def decode(self) -> dcr.NorthwestPacificTsunami:
        tp = self.extract_field(53, 3)
        self.tsunamigenic_potential_en = tsunamigenic_potential_en[tp]
        self.tsunamigenic_potential_raw = tp

        self.expected_tsunami_arrival_times: list[datetime | None] = []
        self.expected_tsunami_arrival_times_raw: list[DayHourMinute] = []
        self.expected_tsunami_arrival_time_types_en: list[str] = []
        self.tsunami_heights_en: list[str] = []
        self.tsunami_heights_raw: list[int] = []
        self.coastal_regions_en: list[str] = []
        self.coastal_regions_raw: list[int] = []
        for i in range(5):
            offset = 56 + i * 28

            if self.extract_field(offset, 28) == 0:
                break

            ta, ta_raw, ta_type = self.extract_northwest_pacific_tsunami_arrival_time_field(offset)
            self.expected_tsunami_arrival_times.append(ta)
            self.expected_tsunami_arrival_times_raw.append(ta_raw)
            self.expected_tsunami_arrival_time_types_en.append(ta_type)

            th = self.extract_field(offset + 12, 9)
            self.tsunami_heights_en.append(northwest_pacific_tsunami_height_en[th])
            self.tsunami_heights_raw.append(th)

            pl = self.extract_field(offset + 21, 7)
            self.coastal_regions_en.append(coastal_region_en[pl])
            self.coastal_regions_raw.append(pl)

        return dcr.NorthwestPacificTsunami(
            **self.context.params(),
            tsunamigenic_potential_en=self.tsunamigenic_potential_en,
            tsunamigenic_potential_raw=self.tsunamigenic_potential_raw,
            expected_tsunami_arrival_times=self.expected_tsunami_arrival_times,
            expected_tsunami_arrival_times_raw=self.expected_tsunami_arrival_times_raw,
            expected_tsunami_arrival_time_types_en=self.expected_tsunami_arrival_time_types_en,
            tsunami_heights_en=self.tsunami_heights_en,
            tsunami_heights_raw=self.tsunami_heights_raw,
            coastal_regions_en=self.coastal_regions_en,
            coastal_regions_raw=self.coastal_regions_raw,
        )


class Volcano(Common):
    def decode(self) -> dcr.Volcano:
        self.ambiguity_of_activity_time_no = self.extract_field(50, 3)
        self.activity_time_raw = self.extract_day_hour_min_raw(53)
        self.activity_time = self.extract_activity_time(self.activity_time_raw, self.ambiguity_of_activity_time_no)

        dw = self.extract_field(69, 7)
        self.volcanic_warning_code = volcanic_warning_code[dw]
        self.volcanic_warning_code_raw = dw

        vo = self.extract_field(76, 12)
        self.volcano_name = volcano_name[vo]
        self.volcano_name_raw = vo

        self.local_governments: list[str] = []
        self.local_governments_raw: list[int] = []
        for i in range(5):
            offset = 88 + i * 23
            if self.extract_field(offset, 23) == 0:
                break
            local_government, lg = self.extract_local_government(offset)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return dcr.Volcano(
            **self.context.params(),
            ambiguity_of_activity_time_no=self.ambiguity_of_activity_time_no,
            activity_time=self.activity_time,
            activity_time_raw=self.activity_time_raw,
            volcanic_warning_code=self.volcanic_warning_code,
            volcanic_warning_code_raw=self.volcanic_warning_code_raw,
            volcano_name=self.volcano_name,
            volcano_name_raw=self.volcano_name_raw,
            local_governments=self.local_governments,
            local_governments_raw=self.local_governments_raw,
        )

    def extract_activity_time(self, raw: DayHourMinute, ambiguity: int) -> datetime | None:
        """Observed activity time (UTC) with the parts that the ambiguity marks as not valid set to 0.

        None when the ambiguity marks no part as valid, or when the valid parts are not a time.
        """
        if ambiguity >= 6:  # approximate month or year: day, hour and minute are not valid
            return None
        day = raw['day']
        hour = raw['hour'] if ambiguity <= 4 else 0  # approximate day: hour and minute are not valid
        minute = raw['minute'] if ambiguity <= 3 else 0  # approximate hour: minute is not valid
        if day not in days or hour not in hours or minute not in minutes:
            return None

        # the activity was observed by the time of the report: take the latest such date with this day
        year, month = self.report_time.year, self.report_time.month
        if day > self.report_time.day:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)
        while day > monthrange(year, month)[1]:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)

        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=UTC)


class AshFall(Common):
    def decode(self) -> dcr.AshFall:
        self.activity_time, self.activity_time_raw = self.extract_day_hour_min_field(53)

        dw1 = self.extract_field(69, 2)
        self.ash_fall_warning_type = ash_fall_warning_type[dw1]
        self.ash_fall_warning_type_raw = dw1

        vo = self.extract_field(71, 12)
        self.volcano_name = volcano_name[vo]
        self.volcano_name_raw = vo

        self.expected_ash_fall_times: list[str] = []
        self.expected_ash_fall_times_raw: list[int] = []
        self.ash_fall_warning_codes: list[str] = []
        self.ash_fall_warning_codes_raw: list[int] = []
        self.local_governments: list[str] = []
        self.local_governments_raw: list[int] = []
        for i in range(4):
            offset = 83 + i * 29
            if self.extract_field(offset, 29) == 0:
                break

            ho = self.extract_field(offset, 3)
            self.expected_ash_fall_times.append(expected_ash_fall_time[ho])
            self.expected_ash_fall_times_raw.append(ho)

            dw2 = self.extract_field(offset + 3, 3)
            self.ash_fall_warning_codes.append(ash_fall_warning_code[dw2])
            self.ash_fall_warning_codes_raw.append(dw2)

            local_government, lg = self.extract_local_government(offset + 6)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return dcr.AshFall(
            **self.context.params(),
            activity_time=self.activity_time,
            activity_time_raw=self.activity_time_raw,
            ash_fall_warning_type=self.ash_fall_warning_type,
            ash_fall_warning_type_raw=self.ash_fall_warning_type_raw,
            volcano_name=self.volcano_name,
            volcano_name_raw=self.volcano_name_raw,
            expected_ash_fall_times=self.expected_ash_fall_times,
            expected_ash_fall_times_raw=self.expected_ash_fall_times_raw,
            ash_fall_warning_codes=self.ash_fall_warning_codes,
            ash_fall_warning_codes_raw=self.ash_fall_warning_codes_raw,
            local_governments=self.local_governments,
            local_governments_raw=self.local_governments_raw,
        )


class Weather(Common):
    def decode(self) -> dcr.Weather:
        ar = self.extract_field(53, 3)
        self.weather_warning_state = weather_warning_state[ar]
        self.weather_warning_state_raw = ar

        self.weather_related_disaster_sub_categories: list[str] = []
        self.weather_related_disaster_sub_categories_raw: list[int] = []
        self.weather_forecast_regions: list[str] = []
        self.weather_forecast_regions_raw: list[int] = []
        for i in range(6):
            offset = 56 + i * 24

            if self.extract_field(offset, 24) == 0:
                break

            ww = self.extract_field(offset, 5)
            self.weather_related_disaster_sub_categories.append(
                weather_related_disaster_sub_category[ww])
            self.weather_related_disaster_sub_categories_raw.append(ww)

            pl = self.extract_field(offset + 5, 19)
            self.weather_forecast_regions.append(weather_forecast_region[pl])
            self.weather_forecast_regions_raw.append(pl)

        return dcr.Weather(
            **self.context.params(),
            weather_warning_state=self.weather_warning_state,
            weather_warning_state_raw=self.weather_warning_state_raw,
            weather_related_disaster_sub_categories=self.weather_related_disaster_sub_categories,
            weather_related_disaster_sub_categories_raw=self.weather_related_disaster_sub_categories_raw,
            weather_forecast_regions=self.weather_forecast_regions,
            weather_forecast_regions_raw=self.weather_forecast_regions_raw,
        )


class Flood(Common):
    def decode(self) -> dcr.Flood:
        self.flood_warning_levels: list[str] = []
        self.flood_warning_levels_raw: list[int] = []
        self.flood_forecast_regions: list[str] = []
        self.flood_forecast_regions_raw: list[int] = []
        for i in range(3):
            offset = 53 + i * 44

            if self.extract_field(offset, 44) == 0:
                break

            lv = self.extract_field(offset, 4)
            self.flood_warning_levels.append(flood_warning_level[lv])
            self.flood_warning_levels_raw.append(lv)

            pl = self.extract_field(offset + 4, 40)
            self.flood_forecast_regions.append(flood_forecast_region[pl])
            self.flood_forecast_regions_raw.append(pl)

        return dcr.Flood(
            **self.context.params(),
            flood_warning_levels=self.flood_warning_levels,
            flood_warning_levels_raw=self.flood_warning_levels_raw,
            flood_forecast_regions=self.flood_forecast_regions,
            flood_forecast_regions_raw=self.flood_forecast_regions_raw,
        )


class Marine(Common):
    def decode(self) -> dcr.Marine:
        self.marine_warning_codes: list[str] = []
        self.marine_warning_codes_raw: list[int] = []
        self.marine_forecast_regions: list[str] = []
        self.marine_forecast_regions_raw: list[int] = []
        for i in range(8):
            offset = 53 + i * 19
            dw = self.extract_field(offset, 5)
            pl = self.extract_field(offset + 5, 14)
            if dw == 0 and pl == 0:
                break

            self.marine_warning_codes.append(marine_warning_code[dw])
            self.marine_warning_codes_raw.append(dw)

            self.marine_forecast_regions.append(marine_forecast_region[pl])
            self.marine_forecast_regions_raw.append(pl)

        return dcr.Marine(
            **self.context.params(),
            marine_warning_codes=self.marine_warning_codes,
            marine_warning_codes_raw=self.marine_warning_codes_raw,
            marine_forecast_regions=self.marine_forecast_regions,
            marine_forecast_regions_raw=self.marine_forecast_regions_raw,
        )


class Typhoon(Common):
    def decode(self) -> dcr.Typhoon:
        self.reference_time, self.reference_time_raw = self.extract_day_hour_min_field(53)

        dt = self.extract_field(69, 3)
        self.reference_time_type = typhoon_reference_time_type[dt]
        self.reference_time_type_raw = dt

        # the time elapsed from the analysis
        du = self.extract_field(80, 7)
        self.elapsed_time_from_reference_time = typhoon_elapsed_time_from_reference_time[du]
        self.elapsed_time_from_reference_time_raw = du

        tn = self.extract_field(87, 7)
        self.typhoon_number = typhoon_number[tn]
        self.typhoon_number_raw = tn

        sr = self.extract_field(94, 4)
        self.typhoon_scale_category = typhoon_scale_category[sr]
        self.typhoon_scale_category_raw = sr

        lc = self.extract_field(98, 4)
        self.typhoon_intensity_category = typhoon_intensity_category[lc]
        self.typhoon_intensity_category_raw = lc

        self.coordinates_of_typhoon, self.coordinates_of_typhoon_raw = self.extract_lat_lon_field(102)

        pr = self.extract_field(143, 11)
        self.central_pressure = typhoon_central_pressure[pr]
        self.central_pressure_raw = pr

        w1 = self.extract_field(154, 7)
        self.maximum_wind_speed = typhoon_maximum_wind_speed[w1]
        self.maximum_wind_speed_raw = w1

        w2 = self.extract_field(161, 7)
        self.maximum_gust_wind_speed = typhoon_maximum_gust_wind_speed[w2]
        self.maximum_gust_wind_speed_raw = w2

        return dcr.Typhoon(
            **self.context.params(),
            reference_time=self.reference_time,
            reference_time_raw=self.reference_time_raw,
            reference_time_type=self.reference_time_type,
            reference_time_type_raw=self.reference_time_type_raw,
            elapsed_time_from_reference_time=self.elapsed_time_from_reference_time,
            elapsed_time_from_reference_time_raw=self.elapsed_time_from_reference_time_raw,
            typhoon_number=self.typhoon_number,
            typhoon_number_raw=self.typhoon_number_raw,
            typhoon_scale_category=self.typhoon_scale_category,
            typhoon_scale_category_raw=self.typhoon_scale_category_raw,
            typhoon_intensity_category=self.typhoon_intensity_category,
            typhoon_intensity_category_raw=self.typhoon_intensity_category_raw,
            coordinates_of_typhoon=self.coordinates_of_typhoon,
            coordinates_of_typhoon_raw=self.coordinates_of_typhoon_raw,
            central_pressure=self.central_pressure,
            central_pressure_raw=self.central_pressure_raw,
            maximum_wind_speed=self.maximum_wind_speed,
            maximum_wind_speed_raw=self.maximum_wind_speed_raw,
            maximum_gust_wind_speed=self.maximum_gust_wind_speed,
            maximum_gust_wind_speed_raw=self.maximum_gust_wind_speed_raw,
        )
