from ..reports import dcr
from .dcr_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_typhoon_central_pressure
from ..definitions import qzss_dcr_jma_typhoon_elapsed_time_from_reference_time
from ..definitions import qzss_dcr_jma_typhoon_intensity_category
from ..definitions import qzss_dcr_jma_typhoon_maximum_gust_wind_speed
from ..definitions import qzss_dcr_jma_typhoon_maximum_wind_speed
from ..definitions import qzss_dcr_jma_typhoon_number
from ..definitions import qzss_dcr_jma_typhoon_reference_time_type
from ..definitions import qzss_dcr_jma_typhoon_scale_category


class QzssDcrDecoderJmaTyphoon(QzssDcrDecoderJmaCommon):
    schema = dcr.Base

    def decode(self) -> dcr.Typhoon:
        self.reference_time, self.reference_time_raw = self.extract_day_hour_min_field(53)

        dt = self.extract_field(69, 3)
        self.reference_time_type = qzss_dcr_jma_typhoon_reference_time_type[dt]
        self.reference_time_type_raw = dt

        # the time elapsed from the analysis
        du = self.extract_field(80, 7)
        self.elapsed_time_from_reference_time = qzss_dcr_jma_typhoon_elapsed_time_from_reference_time[du]
        self.elapsed_time_from_reference_time_raw = du

        tn = self.extract_field(87, 7)
        self.typhoon_number = qzss_dcr_jma_typhoon_number[tn]
        self.typhoon_number_raw = tn

        sr = self.extract_field(94, 4)
        self.typhoon_scale_category = qzss_dcr_jma_typhoon_scale_category[sr]
        self.typhoon_scale_category_raw = sr

        lc = self.extract_field(98, 4)
        self.typhoon_intensity_category = qzss_dcr_jma_typhoon_intensity_category[lc]
        self.typhoon_intensity_category_raw = lc

        self.coordinates_of_typhoon, self.coordinates_of_typhoon_raw = self.extract_lat_lon_field(102)

        pr = self.extract_field(143, 11)
        self.central_pressure = qzss_dcr_jma_typhoon_central_pressure[pr]
        self.central_pressure_raw = pr

        w1 = self.extract_field(154, 7)
        self.maximum_wind_speed = qzss_dcr_jma_typhoon_maximum_wind_speed[w1]
        self.maximum_wind_speed_raw = w1

        w2 = self.extract_field(161, 7)
        self.maximum_gust_wind_speed = qzss_dcr_jma_typhoon_maximum_gust_wind_speed[w2]
        self.maximum_gust_wind_speed_raw = w2

        return dcr.Typhoon(**self.get_params())
