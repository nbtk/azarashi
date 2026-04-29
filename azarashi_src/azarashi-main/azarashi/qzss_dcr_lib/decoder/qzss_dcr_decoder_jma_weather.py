from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_weather_forecast_region
from ..definition import qzss_dcr_jma_weather_related_disaster_sub_category
from ..definition import qzss_dcr_jma_weather_warning_state
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaWeather


class QzssDcrDecoderJmaWeather(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        ar = self.extract_field(53, 3)
        try:
            self.weather_warning_state = qzss_dcr_jma_weather_warning_state[ar]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Warning State: {ar}',
                self)
        self.weather_warning_state_raw = ar

        self.weather_related_disaster_sub_categories = []
        self.weather_related_disaster_sub_categories_raw = []
        self.weather_forecast_regions = []
        self.weather_forecast_regions_raw = []
        for i in range(6):
            offset = 56 + i * 24

            if self.extract_field(offset, 24) == 0:
                break

            ww = self.extract_field(offset, 5)
            try:
                self.weather_related_disaster_sub_categories.append(
                    qzss_dcr_jma_weather_related_disaster_sub_category[ww])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Disaster Sub-Category: {ww}',
                    self)
            self.weather_related_disaster_sub_categories_raw.append(ww)

            pl = self.extract_field(offset + 5, 19)
            try:
                self.weather_forecast_regions.append(qzss_dcr_jma_weather_forecast_region[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Prefectural Forecast Region: {pl}',
                    self)
            self.weather_forecast_regions_raw.append(pl)

        return QzssDcReportJmaWeather(**self.get_params())
