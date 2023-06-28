from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_marine_forecast_region
from ..definition import qzss_dcr_jma_marine_warning_code
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaMarine


class QzssDcrDecoderJmaMarine(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.marine_warning_codes = []
        self.marine_warning_codes_raw = []
        self.marine_forecast_regions = []
        self.marine_forecast_regions_raw = []
        for i in range(8):
            offset = 53 + i * 19
            dw = self.extract_field(offset, 5)
            pl = self.extract_field(offset + 5, 14)
            if dw == 0 and pl == 0:
                break

            try:
                self.marine_warning_codes.append(qzss_dcr_jma_marine_warning_code[dw])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Marine Warning Code: {dw}',
                    self)
            self.marine_warning_codes_raw.append(dw)

            try:
                self.marine_forecast_regions.append(qzss_dcr_jma_marine_forecast_region[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Marine Forecast: {pl}',
                    self)
            self.marine_forecast_regions_raw.append(pl)

        return QzssDcReportJmaMarine(**self.get_params())
