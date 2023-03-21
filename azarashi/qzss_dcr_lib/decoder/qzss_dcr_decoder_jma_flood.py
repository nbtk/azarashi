from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_flood_forecast_region
from ..definition import qzss_dcr_jma_flood_warning_level
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaFlood


class QzssDcrDecoderJmaFlood(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.flood_warning_levels = []
        self.flood_forecast_regions = []
        for i in range(3):
            offset = 53 + i * 44

            if self.extract_field(offset, 44) == 0:
                break

            lv = self.extract_field(offset, 4)
            try:
                self.flood_warning_levels.append(qzss_dcr_jma_flood_warning_level[lv])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Flood Warning Level: {lv}',
                    self)

            pl = self.extract_field(offset + 4, 40)
            try:
                self.flood_forecast_regions.append(qzss_dcr_jma_flood_forecast_region[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Flood Forecast Region: {pl}',
                    self)

        return QzssDcReportJmaFlood(**self.get_params())
