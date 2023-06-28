from copy import deepcopy
from datetime import datetime, timedelta

from ..exception import QzssDcrDecoderException


class QzssDcReportBase:
    def __init__(self,
                 sentence,
                 raw=None,
                 timestamp=None,
                 **kwargs):
        self.sentence = sentence
        if raw is None:
            self.raw = b''
        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.raw == other.raw

    def __str__(self):
        str(self.__dict__)

    def get_params(self):
        return deepcopy(self.__dict__)


class QzssDcReportMessagePartial(QzssDcReportBase):
    def __init__(self,
                 message,
                 nmea,
                 message_header=None,
                 satellite_id=None,
                 satellite_prn=None,
                 sentence=None,
                 **kwargs):
        if sentence is None:
            sentence = message
        super().__init__(sentence, **kwargs)
        self.message = message
        self.nmea = nmea
        self.message_header = message_header
        self.satellite_id = satellite_id
        self.satellite_prn = satellite_prn
        self.raw = self.message[1:27] + bytes((self.message[27] & 0xF0,))


class QzssDcReportMessageBase(QzssDcReportMessagePartial):
    def __init__(self,
                 preamble,
                 message_type,
                 report_classification,
                 report_classification_en,
                 report_classification_no,
                 **kwargs):
        super().__init__(**kwargs)
        self.preamble = preamble
        self.message_type = message_type
        self.report_classification = report_classification
        self.report_classification_en = report_classification_en
        self.report_classification_no = report_classification_no


class QzssDcReportJmaBase(QzssDcReportMessageBase):
    def __init__(self,
                 version,
                 disaster_category,
                 disaster_category_en,
                 disaster_category_no,
                 report_time,
                 information_type,
                 information_type_en,
                 information_type_no,
                 **kwargs):
        super().__init__(**kwargs)
        self.version = version
        self.disaster_category = disaster_category
        self.disaster_category_en = disaster_category_en
        self.disaster_category_no = disaster_category_no
        self.report_time = report_time
        self.information_type = information_type
        self.information_type_en = information_type_en
        self.information_type_no = information_type_no

    def get_header(self):
        header = f'防災気象情報({self.disaster_category})' + \
                 f'({self.information_type})' + \
                 f'({self.report_classification})'
        if self.report_classification_no == 7:
            header += '\n*** これは訓練です ***'
        elif self.information_type_no == 2:
            header += '\n*** 取り消しされました ***'
        return header

    def get_header_en(self):
        header = f'JMA-DC Report ({self.disaster_category_en})' + \
                 f' ({self.information_type_en})' + \
                 f' ({self.report_classification_en})'
        if self.report_classification_no == 7:
            header += '\n*** TRAINING/TEST ***'
        elif self.information_type_no == 2:
            header += '\n*** CANCELLATION ***'
        return header

    def get_report_time_str(self, time_diff=9):
        at = self.report_time + timedelta(hours=time_diff)
        return f'{at.month}月{at.day}日{at.hour}時{at.minute}分'

    def get_report_time_str_iso(self):
        return self.report_time.strftime('--%m-%dT%H:%MZ')

    @staticmethod
    def convert_dt_to_str(dt, time_diff=9):
        dt += timedelta(hours=time_diff)
        return f'{dt.day}日{dt.hour}時{dt.minute}分'

    @staticmethod
    def convert_dt_to_str_iso(dt):
        return dt.strftime('---%dT%H:%MZ')

    def convert_dt_to_ambiguous_time_str(self, td, du):
        try:
            return [f'{td.month}月{td.day}日{td.hour}時{td.minute}分',  # No ambiguity
                    f'{td.month}月{td.day}日{td.hour}時{td.minute}分頃',
                    # Approximate time(equivalent to Approximate time (minute))
                    f'{td.month}月{td.day}日{td.hour}時{td.minute}分',  # Approximate time(second)
                    f'{td.month}月{td.day}日{td.hour}時{td.minute}分頃',  # Approximate time(minute)
                    f'{td.month}月{td.day}日{td.hour}時頃',  # Approximate time(hour)
                    f'{td.month}月{td.day}日頃',  # Approximate time(day)
                    f'{td.month}月頃',  # Approximate time(month)
                    f'{td.year}年頃',  # Approximate time(year)
                    ][du]
        except:
            raise QzssDcrDecoderException(
                f'Undefined JMA Ambiguity of Activity Time: {du}',
                self)

    @staticmethod
    def convert_lat_lon_to_str(coordinates):
        return f'{"北緯" if coordinates["lat_ns"] == 0 else "南緯"}' + \
            f'{coordinates["lat_d"]}度' + \
            f'{coordinates["lat_m"]}分' + \
            f'{coordinates["lat_s"]}秒 ' + \
            f'{"東経" if coordinates["lon_ew"] == 0 else "西経"}' + \
            f'{coordinates["lon_d"]}度' + \
            f'{coordinates["lon_m"]}分' + \
            f'{coordinates["lon_s"]}秒'


class QzssDcReportJmaEarthquakeEarlyWarning(QzssDcReportJmaBase):
    def __init__(self,
                 notifications_on_disaster_prevention,
                 notifications_on_disaster_prevention_raw,
                 occurrence_time_of_earthquake,
                 depth_of_hypocenter,
                 depth_of_hypocenter_raw,
                 magnitude,
                 magnitude_raw,
                 assumptive,
                 seismic_epicenter,
                 seismic_epicenter_raw,
                 seismic_intensity_lower_limit,
                 seismic_intensity_lower_limit_raw,
                 seismic_intensity_upper_limit,
                 seismic_intensity_upper_limit_raw,
                 eew_forecast_regions,
                 eew_forecast_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
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

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '緊急地震速報\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        if self.assumptive is True:
            assumptive_str = '(仮定震源要素)'
        else:
            assumptive_str = ''

        report += f'\n\n発表時刻: {self.get_report_time_str()}\n\n' + \
                  f'震央地名: {self.seismic_epicenter}\n' + \
                  f'地震発生時刻: {self.convert_dt_to_str(self.occurrence_time_of_earthquake)}\n' + \
                  f'深さ: {self.depth_of_hypocenter}{assumptive_str}\n' + \
                  f'マグニチュード: {self.magnitude}{assumptive_str}\n' + \
                  f'震度(下限): {self.seismic_intensity_lower_limit}\n' + \
                  f'震度(上限): {self.seismic_intensity_upper_limit}\n'
        report += '、'.join(self.eew_forecast_regions)
        return report


class QzssDcReportJmaHypocenter(QzssDcReportJmaBase):
    def __init__(self,
                 notifications_on_disaster_prevention,
                 notifications_on_disaster_prevention_raw,
                 occurrence_time_of_earthquake,
                 depth_of_hypocenter,
                 depth_of_hypocenter_raw,
                 magnitude,
                 magnitude_raw,
                 seismic_epicenter,
                 seismic_epicenter_raw,
                 coordinates_of_hypocenter,
                 **kwargs):
        super().__init__(**kwargs)
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
        self.depth_of_hypocenter = depth_of_hypocenter
        self.depth_of_hypocenter_raw = depth_of_hypocenter_raw
        self.magnitude = magnitude
        self.magnitude_raw = magnitude_raw
        self.seismic_epicenter = seismic_epicenter
        self.seismic_epicenter_raw = seismic_epicenter_raw
        self.coordinates_of_hypocenter = coordinates_of_hypocenter

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 f'{self.convert_dt_to_str(self.occurrence_time_of_earthquake)}' + \
                 'ころ、地震がありました。\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        report += f'\n\n発表時刻: {self.get_report_time_str()}\n\n' + \
                  f'震央地名: {self.seismic_epicenter}\n' + \
                  f'緯度・経度: {self.convert_lat_lon_to_str(self.coordinates_of_hypocenter)}\n' + \
                  f'深さ: {self.depth_of_hypocenter}\n' + \
                  f'マグニチュード: {self.magnitude}'
        return report


class QzssDcReportJmaSeismicIntensity(QzssDcReportJmaBase):
    def __init__(self,
                 occurrence_time_of_earthquake,
                 seismic_intensities,
                 seismic_intensities_raw,
                 prefectures,
                 prefectures_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.occurrence_time_of_earthquake = occurrence_time_of_earthquake
        self.seismic_intensities = seismic_intensities
        self.seismic_intensities_raw = seismic_intensities_raw
        self.prefectures = prefectures
        self.prefectures_raw = prefectures_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 f'{self.convert_dt_to_str(self.occurrence_time_of_earthquake)}' + \
                 'ころ、地震による強い揺れを感じました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.seismic_intensities)):
            report += f'\n\n震度: {self.seismic_intensities[i]}\n' + \
                      f'{self.prefectures[i]}'
        return report


class QzssDcReportJmaNankaiTroughEarthquake(QzssDcReportJmaBase):
    completed = False
    reports = {}

    def __init__(self,
                 information_serial_code,
                 information_serial_code_raw,
                 text_information,
                 page_number,
                 total_page,
                 **kwargs):
        super().__init__(**kwargs)
        self.information_serial_code = information_serial_code
        self.information_serial_code_raw = information_serial_code_raw
        self.text_information = text_information
        self.page_number = page_number
        self.total_page = total_page

        cls = self.__class__
        ex_report = cls.reports.get(self.page_number)
        if ex_report is not None:
            if ex_report == self:
                return
            else:
                cls.completed = False
                cls.reports = {}

        cls.reports.update({self.page_number: self})
        if len(cls.reports) == self.total_page:
            cls.completed = True

    def extract_text_information(self):
        cls = self.__class__
        if cls.completed is not True:
            return f'受信中 ({self.page_number}) [{len(cls.reports)}/{self.total_page}]'

        cls = self.__class__
        msg_bytes = b''
        for i in range(1, self.total_page + 1):
            msg_bytes += cls.reports[i].text_information

        return msg_bytes.decode('utf-8', errors='ignore')

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 f'南海トラフ地震に関連する情報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n' + \
                 f'地震関連情報: {self.information_serial_code}\n' + \
                 f'{self.extract_text_information()}'
        return report


class QzssDcReportJmaTsunami(QzssDcReportJmaBase):
    def __init__(self,
                 notifications_on_disaster_prevention,
                 notifications_on_disaster_prevention_raw,
                 tsunami_warning_code,
                 tsunami_warning_code_raw,
                 expected_tsunami_arrival_times,
                 tsunami_heights,
                 tsunami_heights_raw,
                 tsunami_forecast_regions,
                 tsunami_forecast_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.notifications_on_disaster_prevention = notifications_on_disaster_prevention
        self.notifications_on_disaster_prevention_raw = notifications_on_disaster_prevention_raw
        self.tsunami_warning_code = tsunami_warning_code
        self.tsunami_warning_code_raw = tsunami_warning_code_raw
        self.expected_tsunami_arrival_times = expected_tsunami_arrival_times
        self.tsunami_heights = tsunami_heights
        self.tsunami_heights_raw = tsunami_heights_raw
        self.tsunami_forecast_regions = tsunami_forecast_regions
        self.tsunami_forecast_regions_raw = tsunami_forecast_regions_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 f'{self.tsunami_warning_code}を発表しました。\n'

        report += '\n'.join(self.notifications_on_disaster_prevention)

        report += f'\n\n発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.expected_tsunami_arrival_times)):
            if self.expected_tsunami_arrival_times[i] is None:
                ta = '不明'
            else:
                ta = self.convert_dt_to_str(self.expected_tsunami_arrival_times[i])
            report += f'\n\n津波到達予想時刻: {ta}\n' + \
                      f'津波の高さ: {self.tsunami_heights[i]}\n' + \
                      f'{self.tsunami_forecast_regions[i]}'
        return report


class QzssDcReportJmaNorthwestPacificTsunami(QzssDcReportJmaBase):
    def __init__(self,
                 tsunamigenic_potential_en,
                 tsunamigenic_potential_raw,
                 expected_tsunami_arrival_times,
                 tsunami_heights_en,
                 tsunami_heights_raw,
                 coastal_regions_en,
                 coastal_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.tsunamigenic_potential_en = tsunamigenic_potential_en
        self.tsunamigenic_potential_raw = tsunamigenic_potential_raw
        self.expected_tsunami_arrival_times = expected_tsunami_arrival_times
        self.tsunami_heights_en = tsunami_heights_en
        self.tsunami_heights_raw = tsunami_heights_raw
        self.coastal_regions_en = coastal_regions_en
        self.coastal_regions_raw = coastal_regions_raw

    def __str__(self):
        report = f'{self.get_header_en()}\n' + \
                 f'{self.tsunamigenic_potential_en}.\n\n' + \
                 f'Time of Issue: {self.get_report_time_str_iso()}'

        for i in range(len(self.expected_tsunami_arrival_times)):
            if self.expected_tsunami_arrival_times[i] is None:
                ta = 'Unknown'
            else:
                ta = self.convert_dt_to_str(self.expected_tsunami_arrival_times[i])
            report += f'\n\nExpected Tsunami Arrival Time: {ta}\n' + \
                      f'Tsunami Height: {self.tsunami_heights_en[i]}\n' + \
                      f'Coastal Region: {self.coastal_regions_en[i]}'
        return report


class QzssDcReportJmaVolcano(QzssDcReportJmaBase):
    def __init__(self,
                 ambiguity_of_activity_time_no,
                 activity_time,
                 volcanic_warning_code,
                 volcanic_warning_code_raw,
                 volcano_name,
                 volcano_name_raw,
                 local_governments,
                 local_governments_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.ambiguity_of_activity_time_no = ambiguity_of_activity_time_no
        self.activity_time = activity_time
        self.volcanic_warning_code = volcanic_warning_code
        self.volcanic_warning_code_raw = volcanic_warning_code_raw
        self.volcano_name = volcano_name
        self.volcano_name_raw = volcano_name_raw
        self.local_governments = local_governments
        self.local_governments_raw = local_governments_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '火山に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'火山名: {self.volcano_name}\n' + \
                 f'日時: {self.convert_dt_to_ambiguous_time_str(self.activity_time, self.ambiguity_of_activity_time_no)}\n' + \
                 f'現象: {self.volcanic_warning_code}\n\n'

        report += '、'.join(self.local_governments)
        return report


class QzssDcReportJmaAshFall(QzssDcReportJmaBase):
    def __init__(self,
                 activity_time,
                 ash_fall_warning_type,
                 ash_fall_warning_type_raw,
                 volcano_name,
                 volcano_name_raw,
                 expected_ash_fall_times,
                 ash_fall_warning_codes,
                 ash_fall_warning_codes_raw,
                 local_governments,
                 local_governments_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.activity_time = activity_time
        self.ash_fall_warning_type = ash_fall_warning_type
        self.ash_fall_warning_type_raw = ash_fall_warning_type_raw
        self.volcano_name = volcano_name
        self.volcano_name_raw = volcano_name_raw
        self.expected_ash_fall_times = expected_ash_fall_times
        self.ash_fall_warning_codes = ash_fall_warning_codes
        self.ash_fall_warning_codes_raw = ash_fall_warning_codes_raw
        self.local_governments = local_governments
        self.local_governments_raw = local_governments_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '降灰に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'{self.ash_fall_warning_type}\n' + \
                 f'火山名: {self.volcano_name}\n' + \
                 f'日時: {self.convert_dt_to_str(self.activity_time)}'

        for i in range(len(self.expected_ash_fall_times)):
            report += '\n\n' + \
                      f'基点時刻からの時間: {self.expected_ash_fall_times[i]}時間\n' + \
                      f'現象: {self.ash_fall_warning_codes[i]}\n' + \
                      f'{self.local_governments[i]}'
        return report


class QzssDcReportJmaWeather(QzssDcReportJmaBase):
    def __init__(self,
                 weather_warning_state,
                 weather_warning_state_raw,
                 weather_related_disaster_sub_categories,
                 weather_related_disaster_sub_categories_raw,
                 weather_forecast_regions,
                 weather_forecast_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.weather_warning_state = weather_warning_state
        self.weather_warning_state_raw = weather_warning_state_raw
        self.weather_related_disaster_sub_categories = weather_related_disaster_sub_categories
        self.weather_related_disaster_sub_categories_raw = weather_related_disaster_sub_categories_raw
        self.weather_forecast_regions = weather_forecast_regions
        self.weather_forecast_regions_raw = weather_forecast_regions_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '気象に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.weather_related_disaster_sub_categories)):
            report += f'\n\n警報等情報要素: {self.weather_related_disaster_sub_categories[i]}' + \
                      f'({self.weather_warning_state})\n' + \
                      f'{self.weather_forecast_regions[i]}'
        return report


class QzssDcReportJmaFlood(QzssDcReportJmaBase):
    def __init__(self,
                 flood_warning_levels,
                 flood_warning_levels_raw,
                 flood_forecast_regions,
                 flood_forecast_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.flood_warning_levels = flood_warning_levels
        self.flood_warning_levels_raw = flood_warning_levels_raw
        self.flood_forecast_regions = flood_forecast_regions
        self.flood_forecast_regions_raw = flood_forecast_regions_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '河川の氾濫に関連する情報をお知らせします。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.flood_warning_levels)):
            report += f'\n\n警報レベル: {self.flood_warning_levels[i]}\n' + \
                      f'{self.flood_forecast_regions[i]}'
        return report


class QzssDcReportJmaMarine(QzssDcReportJmaBase):
    def __init__(self,
                 marine_warning_codes,
                 marine_warning_codes_raw,
                 marine_forecast_regions,
                 marine_forecast_regions_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.marine_warning_codes = marine_warning_codes
        self.marine_warning_codes_raw = marine_warning_codes_raw
        self.marine_forecast_regions = marine_forecast_regions
        self.marine_forecast_regions_raw = marine_forecast_regions_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '海上警報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}'

        for i in range(len(self.marine_warning_codes)):
            report += f'\n\n警報等情報要素: {self.marine_warning_codes[i]}\n' + \
                      f'{self.marine_forecast_regions[i]}'
        return report


class QzssDcReportJmaTyphoon(QzssDcReportJmaBase):
    def __init__(self,
                 reference_time,
                 reference_time_type,
                 reference_time_type_raw,
                 elapsed_time_from_reference_time,
                 typhoon_number,
                 typhoon_number_raw,
                 typhoon_scale_category,
                 typhoon_scale_category_raw,
                 typhoon_intencity_category,
                 typhoon_intencity_category_raw,
                 coordinates_of_typhoon,
                 central_pressure,
                 central_pressure_raw,
                 maximum_wind_speed,
                 maximum_wind_speed_raw,
                 maximum_gust_wind_speed,
                 maximum_gust_wind_speed_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.reference_time = reference_time
        self.reference_time_type = reference_time_type
        self.reference_time_type_raw = reference_time_type_raw
        self.elapsed_time_from_reference_time = elapsed_time_from_reference_time
        self.typhoon_number = typhoon_number
        self.typhoon_number_raw = typhoon_number_raw
        self.typhoon_scale_category = typhoon_scale_category
        self.typhoon_scale_category_raw = typhoon_scale_category_raw
        self.typhoon_intencity_category = typhoon_intencity_category
        self.typhoon_intencity_category_raw = typhoon_intencity_category_raw
        self.coordinates_of_typhoon = coordinates_of_typhoon
        self.central_pressure = central_pressure
        self.central_pressure_raw = central_pressure_raw
        self.maximum_wind_speed = maximum_wind_speed
        self.maximum_wind_speed_raw = maximum_wind_speed_raw
        self.maximum_gust_wind_speed = maximum_gust_wind_speed
        self.maximum_gust_wind_speed_raw = maximum_gust_wind_speed_raw

    def __str__(self):
        report = f'{self.get_header()}\n' + \
                 '台風解析・予報情報が発表されました。\n\n' + \
                 f'発表時刻: {self.get_report_time_str()}\n\n' + \
                 f'台風番号: {self.typhoon_number}\n' + \
                 f'基点時刻: {self.convert_dt_to_str(self.reference_time)}\n' + \
                 f'基点時刻分類: {self.reference_time_type}\n' + \
                 f'情報の基点時刻からの経過時間: {self.elapsed_time_from_reference_time}時間後\n' + \
                 f'大きさ: {self.typhoon_scale_category}\n' + \
                 f'強さ: {self.typhoon_intencity_category}\n' + \
                 f'緯度・経度: {self.convert_lat_lon_to_str(self.coordinates_of_typhoon)}\n' + \
                 f'中心気圧: {self.central_pressure}\n' + \
                 f'最大風速: {self.maximum_wind_speed}\n' + \
                 f'最大瞬間風速: {self.maximum_gust_wind_speed}'
        return report


class QzssDcReportOtherOrganization(QzssDcReportMessageBase):
    def __init__(self,
                 organization_code,
                 organization_code_raw,
                 **kwargs):
        super().__init__(**kwargs)
        self.organization_code = organization_code
        self.organization_code_raw = organization_code_raw

    def __str__(self):
        return f'Disaster Crisis Report ({self.organization_code})'
