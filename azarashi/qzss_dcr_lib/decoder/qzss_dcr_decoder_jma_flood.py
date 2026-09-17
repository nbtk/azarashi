from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_flood_forecast_region
from ..definition import qzss_dcr_jma_flood_warning_level
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaFlood


class QzssDcrDecoderJmaFlood(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaFlood:
        self.flood_warning_levels: list[str] = []
        self.flood_warning_levels_raw: list[int] = []
        self.flood_forecast_regions: list[str] = []
        self.flood_forecast_regions_raw: list[int] = []
        for i in range(3):
            offset = 53 + i * 44

            if self.extract_field(offset, 44) == 0:
                break

            lv = self.extract_field(offset, 4)
            self.flood_warning_levels.append(qzss_dcr_jma_flood_warning_level[lv])
            self.flood_warning_levels_raw.append(lv)

            pl = self.extract_field(offset + 4, 40)
            self.flood_forecast_regions.append(qzss_dcr_jma_flood_forecast_region[pl])
            self.flood_forecast_regions_raw.append(pl)

        return QzssDcReportJmaFlood(**self.get_params())
