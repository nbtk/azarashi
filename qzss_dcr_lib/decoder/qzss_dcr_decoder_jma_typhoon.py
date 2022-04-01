from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.report import QzssDcReportJmaBase
from qzss_dcr_lib.report import QzssDcReportJmaTyphoon
from qzss_dcr_lib.definition import qzss_dcr_jma_typhoon_reference_time_type
from qzss_dcr_lib.definition import qzss_dcr_jma_typhoon_scale_category
from qzss_dcr_lib.definition import qzss_dcr_jma_typhoon_intensity_category


class QzssDcrDecoderJmaTyphoon(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.reference_time = self.extract_day_hour_min_field(53)

        dt = self.extract_field(69, 3)
        try:
            self.reference_time_type = qzss_dcr_jma_typhoon_reference_time_type[dt]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Type of Reference Time: {dt}',
                    self.sentence)

        self.elapsed_time_from_reference_time = self.extract_field(80, 7)

        tn = self.extract_field(87, 7)
        if tn < 1 or tn > 99:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Typhoon Number: {tn}',
                    self.sentence)
        self.typhoon_number = f'{tn}号'

        sr = self.extract_field(94, 4)
        try: 
            self.typhoon_scale_category = qzss_dcr_jma_typhoon_scale_category[sr]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Typhoon Scale Category: {sr}',
                    self.sentence)

        lc = self.extract_field(98, 4)
        try:
            self.typhoon_intencity_category = qzss_dcr_jma_typhoon_intensity_category[lc]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Typhoon Intensity Category: {lc}',
                    self.sentence)

        self.coordinates_of_typhoon = self.extract_lat_lon_field(102)

        pr = self.extract_field(143, 11) 
        if pr > 1100:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Central Pressure: {pr}',
                    self.sentence)
        self.central_pressure = f'{pr}hPa'

        w1 = self.extract_field(154, 7) 
        if w1 == 0:
            self.maximum_wind_speed = '不明'
        elif w1 < 15 or w1 > 105:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Maximum Wind Speed: {w1}',
                    self.sentence)
        else:
            self.maximum_wind_speed = f'{w1}m/s'

        w2 = self.extract_field(161, 7) 
        if w2 == 0:
            self.maximum_gust_wind_speed = '不明'
        elif w2 < 15 or w2 > 105:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Maximum Gust Wind Speed: {w2}',
                    self.sentence)
        else:
            self.maximum_gust_wind_speed = f'{w2}m/s'

        return QzssDcReportJmaTyphoon(**self.get_params())
