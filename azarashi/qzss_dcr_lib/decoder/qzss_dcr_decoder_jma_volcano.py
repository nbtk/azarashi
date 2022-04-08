from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaVolcano
from ..definition import qzss_dcr_jma_volcano_name
from ..definition import qzss_dcr_jma_volcanic_warning_code


class QzssDcrDecoderJmaVolcano(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.ambiguity_of_activity_time_no = self.extract_field(50, 3)
        self.activity_time = self.extract_day_hour_min_field(53)

        dw = self.extract_field(69, 7)
        try:
            self.volcanic_warning_code = qzss_dcr_jma_volcanic_warning_code[dw]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Volcanic Warning Code: {dw}',
                    self.sentence)

        vo = self.extract_field(76, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Volcano Name: {vo}',
                    self.sentence)

        self.local_governments = []
        for i in range(5):
            offset = 88 + i * 23
            if self.extract_field(offset, 23) == 0:
                break

            self.local_governments.append(self.extract_local_government(offset))

        return QzssDcReportJmaVolcano(**self.get_params())
