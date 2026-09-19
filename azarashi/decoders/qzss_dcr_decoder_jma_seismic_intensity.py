from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_prefecture
from ..definitions import qzss_dcr_jma_seismic_intensity
from ..reports import QzssDcReportJmaBase
from ..reports import QzssDcReportJmaSeismicIntensity


class QzssDcrDecoderJmaSeismicIntensity(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaSeismicIntensity:
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(53)
        self.seismic_intensities: list[str] = []
        self.seismic_intensities_raw: list[int] = []
        self.prefectures: list[str] = []
        self.prefectures_raw: list[int] = []
        for i in range(16):
            offset = 69 + i * 9
            es = self.extract_field(offset, 3)
            pl = self.extract_field(offset + 3, 6)
            if es == 0 and pl == 0:
                break

            self.seismic_intensities.append(qzss_dcr_jma_seismic_intensity[es])
            self.seismic_intensities_raw.append(es)

            self.prefectures.append(qzss_dcr_jma_prefecture[pl])
            self.prefectures_raw.append(pl)

        return QzssDcReportJmaSeismicIntensity(**self.get_params())
