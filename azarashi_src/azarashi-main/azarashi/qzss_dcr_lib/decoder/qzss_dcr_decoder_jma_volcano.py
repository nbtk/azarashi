from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_volcanic_warning_code
from ..definition import qzss_dcr_jma_volcano_name
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaVolcano


class QzssDcrDecoderJmaVolcano(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.ambiguity_of_activity_time_no = self.extract_field(50, 3)
        self.activity_time = self.extract_day_hour_min_field(53)

        dw = self.extract_field(69, 7)
        try:
            self.volcanic_warning_code = qzss_dcr_jma_volcanic_warning_code[dw]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcanic Warning Code: {dw}',
                self)
        self.volcanic_warning_code_raw = dw

        vo = self.extract_field(76, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcano Name: {vo}',
                self)
        self.volcano_name_raw = vo

        self.local_governments = []
        self.local_governments_raw = []
        for i in range(5):
            offset = 88 + i * 23
            if self.extract_field(offset, 23) == 0:
                break
            local_government, lg = self.extract_local_government(offset)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return QzssDcReportJmaVolcano(**self.get_params())
