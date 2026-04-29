from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_coastal_region_en
from ..definition import qzss_dcr_jma_northwest_pacific_tsunami_height_en
from ..definition import qzss_dcr_jma_tsunamigenic_potential_en
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaNorthwestPacificTsunami


class QzssDcrDecoderJmaNorthwestPacificTsunami(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        tp = self.extract_field(53, 3)
        try:
            self.tsunamigenic_potential_en = qzss_dcr_jma_tsunamigenic_potential_en[tp]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Tsunamigenic Potential : {tp}',
                self)
        self.tsunamigenic_potential_raw = tp

        self.expected_tsunami_arrival_times = []
        self.tsunami_heights_en = []
        self.tsunami_heights_raw = []
        self.coastal_regions_en = []
        self.coastal_regions_raw = []
        for i in range(5):
            offset = 56 + i * 28

            if self.extract_field(offset, 28) == 0:
                break

            self.expected_tsunami_arrival_times.append(self.extract_expected_tsunami_arrival_time(offset))

            th = self.extract_field(offset + 12, 9)
            try:
                self.tsunami_heights_en.append(qzss_dcr_jma_northwest_pacific_tsunami_height_en[th])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Northwest Pacific Tsunami Height: {th}',
                    self)
            self.tsunami_heights_raw.append(th)

            pl = self.extract_field(offset + 21, 7)
            try:
                self.coastal_regions_en.append(qzss_dcr_jma_coastal_region_en[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Coastal Region: {pl}',
                    self)
            self.coastal_regions_raw.append(pl)

        return QzssDcReportJmaNorthwestPacificTsunami(**self.get_params())
