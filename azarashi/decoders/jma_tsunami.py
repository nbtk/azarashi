from datetime import datetime

from ..reports.base import DayHourMinute
from ..reports import jma
from .jma_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_tsunami_forecast_region
from ..definitions import qzss_dcr_jma_tsunami_height
from ..definitions import qzss_dcr_jma_tsunami_warning_code


class QzssDcrDecoderJmaTsunami(QzssDcrDecoderJmaCommon):
    schema = jma.Base

    def decode(self) -> jma.Tsunami:
        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        dw = self.extract_field(80, 4)
        self.tsunami_warning_code = qzss_dcr_jma_tsunami_warning_code[dw]
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
            self.tsunami_heights.append(qzss_dcr_jma_tsunami_height[th])
            self.tsunami_heights_raw.append(th)

            pl = self.extract_field(offset + 16, 10)
            self.tsunami_forecast_regions.append(qzss_dcr_jma_tsunami_forecast_region[pl])
            self.tsunami_forecast_regions_raw.append(pl)

        return jma.Tsunami(**self.get_params())
