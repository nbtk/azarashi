from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaWeather
from ..definition import qzss_dcr_jma_weather_warning_state
from ..definition import qzss_dcr_jma_weather_related_disaster_sub_category
from ..definition import qzss_dcr_jma_weather_forecast_region


class QzssDcrDecoderJmaWeather(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        ar = self.extract_field(53, 3)
        try:
            self.weather_warning_state = qzss_dcr_jma_weather_warning_state[ar]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Warning State: {ar}',
                    self.sentence)

        self.weather_related_disaster_sub_categories = []
        self.weather_forecast_regions = []
        for i in range(6):
            offset = 56 + i * 24

            if self.extract_field(offset, 24) == 0:
                break

            ww = self.extract_field(offset, 5) 
            try:
                self.weather_related_disaster_sub_categories.append(qzss_dcr_jma_weather_related_disaster_sub_category[ww])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Disaster Sub-Category: {ww}',
                        self.sentence)


            pl = self.extract_field(offset+5, 19) 
            try:
                self.weather_forecast_regions.append(qzss_dcr_jma_weather_forecast_region[pl])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Prefectural Forecast Region: {pl}',
                        self.sentence)

        return QzssDcReportJmaWeather(**self.get_params())
