from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaEarthquakeEarlyWarning
from ..definition import qzss_dcr_jma_notification_on_disaster_prevention
from ..definition import qzss_dcr_jma_epicenter_and_hypocenter
from ..definition import qzss_dcr_jma_seismic_intensity_lower_limit
from ..definition import qzss_dcr_jma_seismic_intensity_upper_limit
from ..definition import qzss_dcr_jma_eew_forecast_region


class QzssDcrDecoderJmaEarthquakeEarlyWarning(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.notifications_on_disaster_prevention = self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_eathquake = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter = self.extract_depth_field(96)
        self.magnitude = self.extract_magnitude_field(105)
        self.seismic_epicenter = self.extract_seismic_epicenter_field(112)

        de = self.extract_field(96, 9)
        ma = self.extract_field(105, 7)
        if de == 10 and ma == 10:
            self.assumptive = True
        else:
            self.assumptive = False

        ll = self.extract_field(122, 4)
        try:
            self.seismic_intensity_lower_limit = qzss_dcr_jma_seismic_intensity_lower_limit[ll]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Seismic Intensity Lower Limit : {ll}',
                    self.sentence)

        ul = self.extract_field(126, 4)
        try:
            self.seismic_intensity_upper_limit = qzss_dcr_jma_seismic_intensity_upper_limit[ul]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Seismic Intensity Upper Limit : {ul}',
                    self.sentence)

        self.eew_forecast_regions = []
        for i in range(80):
            if self.extract_field(130 + i, 1) == 1:
                try:
                    self.eew_forecast_regions.append(qzss_dcr_jma_eew_forecast_region[i+1])
                except:
                    raise QzssDcrDecoderException(
                            f'Undefined JMA EEW Forecast Region: {i+1}',
                            self.sentence)

        return QzssDcReportJmaEarthquakeEarlyWarning(**self.get_params())
