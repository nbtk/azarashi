from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_typhoon_central_pressure
from ..definition import qzss_dcr_jma_typhoon_intensity_category
from ..definition import qzss_dcr_jma_typhoon_maximum_gust_wind_speed
from ..definition import qzss_dcr_jma_typhoon_maximum_wind_speed
from ..definition import qzss_dcr_jma_typhoon_number
from ..definition import qzss_dcr_jma_typhoon_reference_time_type
from ..definition import qzss_dcr_jma_typhoon_scale_category
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaTyphoon


class QzssDcrDecoderJmaTyphoon(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaTyphoon:
        self.reference_time = self.extract_day_hour_min_field(53)

        dt = self.extract_field(69, 3)
        try:
            self.reference_time_type = qzss_dcr_jma_typhoon_reference_time_type[dt]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Type of Reference Time: {dt}',
                self) from err
        self.reference_time_type_raw = dt

        # the time elapsed from the analysis
        self.elapsed_time_from_reference_time = self.extract_field(80, 7)

        tn = self.extract_field(87, 7)
        try:
            self.typhoon_number = qzss_dcr_jma_typhoon_number[tn]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Typhoon Number: {tn}',
                self) from err
        self.typhoon_number_raw = tn

        sr = self.extract_field(94, 4)
        try:
            self.typhoon_scale_category = qzss_dcr_jma_typhoon_scale_category[sr]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Typhoon Scale Category: {sr}',
                self) from err
        self.typhoon_scale_category_raw = sr

        lc = self.extract_field(98, 4)
        try:
            self.typhoon_intensity_category = qzss_dcr_jma_typhoon_intensity_category[lc]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Typhoon Intensity Category: {lc}',
                self) from err
        self.typhoon_intensity_category_raw = lc

        self.coordinates_of_typhoon = self.extract_lat_lon_field(102)

        pr = self.extract_field(143, 11)
        try:
            self.central_pressure = qzss_dcr_jma_typhoon_central_pressure[pr]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Central Pressure: {pr}',
                self) from err
        self.central_pressure_raw = pr

        w1 = self.extract_field(154, 7)
        try:
            self.maximum_wind_speed = qzss_dcr_jma_typhoon_maximum_wind_speed[w1]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Maximum Wind Speed: {w1}',
                self) from err
        self.maximum_wind_speed_raw = w1

        w2 = self.extract_field(161, 7)
        try:
            self.maximum_gust_wind_speed = qzss_dcr_jma_typhoon_maximum_gust_wind_speed[w2]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Maximum Gust Wind Speed: {w2}',
                self) from err
        self.maximum_gust_wind_speed_raw = w2

        return QzssDcReportJmaTyphoon(**self.get_params())
