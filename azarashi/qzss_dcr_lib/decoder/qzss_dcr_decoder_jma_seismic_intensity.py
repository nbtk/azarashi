from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_prefecture
from ..definition import qzss_dcr_jma_seismic_intensity
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaSeismicIntensity


class QzssDcrDecoderJmaSeismicIntensity(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.occurrence_time_of_earthquake = self.extract_day_hour_min_field(53)
        self.seismic_intensities = []
        self.seismic_intensities_raw = []
        self.prefectures = []
        self.prefectures_raw = []
        for i in range(16):
            offset = 69 + i * 9
            es = self.extract_field(offset, 3)
            pl = self.extract_field(offset + 3, 6)
            if es == 0 and pl == 0:
                break

            try:
                self.seismic_intensities.append(qzss_dcr_jma_seismic_intensity[es])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Seismic Intensity: {es}',
                    self)
            self.seismic_intensities_raw.append(es)

            try:
                self.prefectures.append(qzss_dcr_jma_prefecture[pl])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Prefecture: {pl}',
                    self)
            self.prefectures_raw.append(pl)

        return QzssDcReportJmaSeismicIntensity(**self.get_params())
