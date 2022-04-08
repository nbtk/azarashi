from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaNorthwestPacificTsunami
from ..definition import qzss_dcr_jma_tsunamigenic_potential_en
from ..definition import qzss_dcr_jma_northwest_pacific_tsunami_height_en
from ..definition import qzss_dcr_jma_coastal_region_en


class QzssDcrDecoderJmaNorthwestPacificTsunami(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        tp = self.extract_field(53, 3)
        try:
            self.tsunamigenic_potential_en = qzss_dcr_jma_tsunamigenic_potential_en[tp]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Tsunamigenic Potential : {tp}',
                    self.sentence)

        self.expected_tsunami_arrival_times = []
        self.tsunami_heights_en = []
        self.coastal_regions_en = []
        for i in range(5):
            offset = 56 + i * 28

            if self.extract_field(offset, 28) == 0:
                break

            self.expected_tsunami_arrival_times.append(self.extract_expected_tsunami_arrival_time(offset))

            th = self.extract_field(offset+12, 9) 
            try:
                self.tsunami_heights_en.append(qzss_dcr_jma_northwest_pacific_tsunami_height_en[th])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Northwest Pacific Tsunami Height: {th}',
                        self.sentence)

            pl = self.extract_field(offset+21, 7) 
            try:
                self.coastal_regions_en.append(qzss_dcr_jma_coastal_region_en[pl])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Coastal Region: {pl}',
                        self.sentence)

        return QzssDcReportJmaNorthwestPacificTsunami(**self.get_params())
