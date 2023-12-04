from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_eew_forecast_region
from ..definition import qzss_dcr_jma_long_period_ground_motion_lower_limit
from ..definition import qzss_dcr_jma_long_period_ground_motion_upper_limit
from ..definition import qzss_dcr_jma_seismic_intensity_lower_limit
from ..definition import qzss_dcr_jma_seismic_intensity_upper_limit
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaEarthquakeEarlyWarning


class QzssDcrDecoderJmaEarthquakeEarlyWarning(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        lgll = self.extract_field(47, 3)
        try:
            self.long_period_ground_motion_lower_limit = qzss_dcr_jma_long_period_ground_motion_lower_limit[lgll]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Expected Maximal Long-period Earthquake Ground Motion Lower Limit : {lgll}',
                self)
        self.long_period_ground_motion_lower_limit_raw = lgll 

        lgul = self.extract_field(50, 3)
        try:
            self.long_period_ground_motion_upper_limit = qzss_dcr_jma_long_period_ground_motion_upper_limit[lgul]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Expected Maximal Long-period Earthquake Ground Motion Upper Limit : {lgul}',
                self)
        self.long_period_ground_motion_upper_limit_raw = lgul

        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_earthquake = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter, self.depth_of_hypocenter_raw = self.extract_depth_field(96)
        self.magnitude, self.magnitude_raw = self.extract_magnitude_field(105)
        self.seismic_epicenter, self.seismic_epicenter_raw = self.extract_seismic_epicenter_field(112)

        if self.depth_of_hypocenter_raw == 10 and self.magnitude_raw == 10:
            self.assumptive = True
        else:
            self.assumptive = False

        ll = self.extract_field(122, 4)
        try:
            self.seismic_intensity_lower_limit = qzss_dcr_jma_seismic_intensity_lower_limit[ll]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Seismic Intensity Lower Limit : {ll}',
                self)
        self.seismic_intensity_lower_limit_raw = ll

        ul = self.extract_field(126, 4)
        try:
            self.seismic_intensity_upper_limit = qzss_dcr_jma_seismic_intensity_upper_limit[ul]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Seismic Intensity Upper Limit : {ul}',
                self)
        self.seismic_intensity_upper_limit_raw = ul

        self.eew_forecast_regions = []
        self.eew_forecast_regions_raw = []
        for i in range(80):
            if self.extract_field(130 + i, 1) == 1:
                try:
                    self.eew_forecast_regions.append(qzss_dcr_jma_eew_forecast_region[i + 1])
                except KeyError:
                    raise QzssDcrDecoderException(
                        f'Undefined JMA EEW Forecast Region: {i + 1}',
                        self)
                self.eew_forecast_regions_raw.append(i + 1)

        return QzssDcReportJmaEarthquakeEarlyWarning(**self.get_params())
