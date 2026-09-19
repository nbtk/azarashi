from datetime import datetime

from ..reports.base import DayHourMinute
from ..reports import dcr
from .dcr_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_coastal_region_en
from ..definitions import qzss_dcr_jma_northwest_pacific_tsunami_height_en
from ..definitions import qzss_dcr_jma_tsunamigenic_potential_en


class QzssDcrDecoderJmaNorthwestPacificTsunami(QzssDcrDecoderJmaCommon):
    schema = dcr.Base

    def decode(self) -> dcr.NorthwestPacificTsunami:
        tp = self.extract_field(53, 3)
        self.tsunamigenic_potential_en = qzss_dcr_jma_tsunamigenic_potential_en[tp]
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
            self.tsunami_heights_en.append(qzss_dcr_jma_northwest_pacific_tsunami_height_en[th])
            self.tsunami_heights_raw.append(th)

            pl = self.extract_field(offset + 21, 7)
            self.coastal_regions_en.append(qzss_dcr_jma_coastal_region_en[pl])
            self.coastal_regions_raw.append(pl)

        return dcr.NorthwestPacificTsunami(**self.get_params())
