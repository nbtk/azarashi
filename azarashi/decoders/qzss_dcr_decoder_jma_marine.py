from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_marine_forecast_region
from ..definitions import qzss_dcr_jma_marine_warning_code
from ..reports import QzssDcReportJmaBase
from ..reports import QzssDcReportJmaMarine


class QzssDcrDecoderJmaMarine(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaMarine:
        self.marine_warning_codes: list[str] = []
        self.marine_warning_codes_raw: list[int] = []
        self.marine_forecast_regions: list[str] = []
        self.marine_forecast_regions_raw: list[int] = []
        for i in range(8):
            offset = 53 + i * 19
            dw = self.extract_field(offset, 5)
            pl = self.extract_field(offset + 5, 14)
            if dw == 0 and pl == 0:
                break

            self.marine_warning_codes.append(qzss_dcr_jma_marine_warning_code[dw])
            self.marine_warning_codes_raw.append(dw)

            self.marine_forecast_regions.append(qzss_dcr_jma_marine_forecast_region[pl])
            self.marine_forecast_regions_raw.append(pl)

        return QzssDcReportJmaMarine(**self.get_params())
