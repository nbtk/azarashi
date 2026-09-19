from ..reports import jma
from .jma_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_weather_forecast_region
from ..definitions import qzss_dcr_jma_weather_related_disaster_sub_category
from ..definitions import qzss_dcr_jma_weather_warning_state


class QzssDcrDecoderJmaWeather(QzssDcrDecoderJmaCommon):
    schema = jma.Base

    def decode(self) -> jma.Weather:
        ar = self.extract_field(53, 3)
        self.weather_warning_state = qzss_dcr_jma_weather_warning_state[ar]
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
                qzss_dcr_jma_weather_related_disaster_sub_category[ww])
            self.weather_related_disaster_sub_categories_raw.append(ww)

            pl = self.extract_field(offset + 5, 19)
            self.weather_forecast_regions.append(qzss_dcr_jma_weather_forecast_region[pl])
            self.weather_forecast_regions_raw.append(pl)

        return jma.Weather(**self.get_params())
