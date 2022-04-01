from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.report import QzssDcReportJmaBase
from qzss_dcr_lib.report import QzssDcReportJmaSeismicIntensity
from qzss_dcr_lib.definition import qzss_dcr_jma_seismic_intensity
from qzss_dcr_lib.definition import qzss_dcr_jma_prefecture


class QzssDcrDecoderJmaSeismicIntensity(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.occurrence_time_of_eathquake = self.extract_day_hour_min_field(53)
        self.seismic_intensities = []
        self.prefectures = []
        for i in range(16):
            offset = 69 + i * 9
            es = self.extract_field(offset, 3)
            pl = self.extract_field(offset+3, 6)
            if es == 0 and pl == 0:
                break

            try:
                self.seismic_intensities.append(qzss_dcr_jma_seismic_intensity[es])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Seismic Intensity: {es}',
                        self.sentence)

            try:
                self.prefectures.append(qzss_dcr_jma_prefecture[pl])
            except:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Prefecture: {pl}',
                        self.sentence)

        return QzssDcReportJmaSeismicIntensity(**self.get_params())
