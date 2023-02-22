from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaNankaiTroughEarthquake
from ..definition import qzss_dcr_jma_information_serial_code


class QzssDcrDecoderJmaNankaiTroughEarthquake(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        ie = self.extract_field(53, 4)
        try:
            self.information_serial_code = qzss_dcr_jma_information_serial_code[ie]
        except KeyError:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Information Serial Code: {ie}',
                    self.sentence)
        te = []
        for i in range(18):
            te.append(self.extract_field(57 + i * 8, 8))

        self.text_information = bytes(te)
        self.page_number = self.extract_field(201, 6)
        self.total_page = self.extract_field(207, 6)

        return QzssDcReportJmaNankaiTroughEarthquake(**self.get_params())
