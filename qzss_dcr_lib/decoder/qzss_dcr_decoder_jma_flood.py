from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.report import QzssDcReportJmaBase
from qzss_dcr_lib.report import QzssDcReportJmaFlood
from qzss_dcr_lib.definition import qzss_dcr_jma_flood_warning_level
from qzss_dcr_lib.definition import qzss_dcr_jma_flood_forecast_region


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
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Flood Warning Level: {lv}',
                        self.sentence)

            pl = self.extract_field(offset+4, 40) 
            try:
                self.flood_forecast_regions.append(qzss_dcr_jma_flood_forecast_region[pl])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Flood Forecast Region: {pl}',
                        self.sentence)

        return QzssDcReportJmaFlood(**self.get_params())
