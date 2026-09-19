from ..reports import dcr
from .dcr_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_information_serial_code


class QzssDcrDecoderJmaNankaiTroughEarthquake(QzssDcrDecoderJmaCommon):
    schema = dcr.Base

    def decode(self) -> dcr.NankaiTroughEarthquake:
        ie = self.extract_field(53, 4)
        self.information_serial_code = qzss_dcr_jma_information_serial_code[ie]
        self.information_serial_code_raw = ie

        te: list[int] = []
        for i in range(18):
            te.append(self.extract_field(57 + i * 8, 8))

        self.text_information = bytes(te)
        self.page_number = self.extract_field(201, 6)
        self.total_page = self.extract_field(207, 6)

        return dcr.NankaiTroughEarthquake(**self.get_params())
