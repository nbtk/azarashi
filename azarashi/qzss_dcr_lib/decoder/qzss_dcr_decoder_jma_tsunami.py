from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaTsunami
from ..definition import qzss_dcr_jma_tsunami_warning_code
from ..definition import qzss_dcr_jma_tsunami_height
from ..definition import qzss_dcr_jma_tsunami_forecast_region


class QzssDcrDecoderJmaTsunami(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.notifications_on_disaster_prevention = self.extract_notification_on_disaster_prevention_fields(53)
        dw = self.extract_field(80, 4)
        try:
            self.tsunami_warning_code = qzss_dcr_jma_tsunami_warning_code[dw]
        except KeyError:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Tsunami Warning Code: {dw}',
                    self.sentence)

        self.expected_tsunami_arrival_times = []
        self.tsunami_heights = []
        self.tsunami_forecast_regions = []
        for i in range(5):
            offset = 84 + i * 26
            if self.extract_field(offset, 26) == 0:
                break

            self.expected_tsunami_arrival_times.append(self.extract_expected_tsunami_arrival_time(offset))

            th = self.extract_field(offset+12, 4) 
            try:
                self.tsunami_heights.append(qzss_dcr_jma_tsunami_height[th])
            except KeyError:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Tsunami Height: {th}',
                        self.sentence)

            pl = self.extract_field(offset+16, 10) 
            try:
                self.tsunami_forecast_regions.append(qzss_dcr_jma_tsunami_forecast_region[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Tsunami Forecast Region: {pl}',
                        self.sentence)

        return QzssDcReportJmaTsunami(**self.get_params())
