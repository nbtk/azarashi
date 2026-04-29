from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_typhoon_intensity_category
from ..definition import qzss_dcr_jma_typhoon_reference_time_type
from ..definition import qzss_dcr_jma_typhoon_scale_category
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaTyphoon


class QzssDcrDecoderJmaTyphoon(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.reference_time = self.extract_day_hour_min_field(53)

        dt = self.extract_field(69, 3)
        try:
            self.reference_time_type = qzss_dcr_jma_typhoon_reference_time_type[dt]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Type of Reference Time: {dt}',
                self)
        self.reference_time_type_raw = dt

        # the time elapsed from the analysis
        self.elapsed_time_from_reference_time = self.extract_field(80, 7)

        tn = self.extract_field(87, 7)
        if tn < 1 or tn > 99:
            raise QzssDcrDecoderException(
                f'Invalid JMA Typhoon Number: {tn}',
                self)
        self.typhoon_number = f'{tn}号'
        self.typhoon_number_raw = tn

        sr = self.extract_field(94, 4)
        try:
            self.typhoon_scale_category = qzss_dcr_jma_typhoon_scale_category[sr]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Typhoon Scale Category: {sr}',
                self)
        self.typhoon_scale_category_raw = sr

        lc = self.extract_field(98, 4)
        try:
            self.typhoon_intensity_category = qzss_dcr_jma_typhoon_intensity_category[lc]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Typhoon Intensity Category: {lc}',
                self)
        self.typhoon_intensity_category_raw = lc

        self.coordinates_of_typhoon = self.extract_lat_lon_field(102)

        pr = self.extract_field(143, 11)
        if pr > 1100:
            raise QzssDcrDecoderException(
                f'Invalid JMA Central Pressure: {pr}',
                self)
        self.central_pressure = f'{pr}hPa'
        self.central_pressure_raw = pr

        w1 = self.extract_field(154, 7)
        if w1 == 0:
            self.maximum_wind_speed = '不明'
        elif w1 < 15 or w1 > 105:
            raise QzssDcrDecoderException(
                f'Invalid JMA Maximum Wind Speed: {w1}',
                self)
        else:
            self.maximum_wind_speed = f'{w1}m/s'
        self.maximum_wind_speed_raw = w1

        w2 = self.extract_field(161, 7)
        if w2 == 0:
            self.maximum_gust_wind_speed = '不明'
        elif w2 < 15 or w2 > 105:
            raise QzssDcrDecoderException(
                f'Invalid JMA Maximum Gust Wind Speed: {w2}',
                self)
        else:
            self.maximum_gust_wind_speed = f'{w2}m/s'
        self.maximum_gust_wind_speed_raw = w2

        return QzssDcReportJmaTyphoon(**self.get_params())
