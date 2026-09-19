from .jma_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_eew_forecast_region
from ..definitions import qzss_dcr_jma_eew_magnitude
from ..definitions import qzss_dcr_jma_long_period_ground_motion_lower_limit
from ..definitions import qzss_dcr_jma_long_period_ground_motion_upper_limit
from ..definitions import qzss_dcr_jma_seismic_intensity_lower_limit
from ..definitions import qzss_dcr_jma_seismic_intensity_upper_limit
from ..reports import QzssDcReportJmaBase
from ..reports import QzssDcReportJmaEarthquakeEarlyWarning


class QzssDcrDecoderJmaEarthquakeEarlyWarning(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaEarthquakeEarlyWarning:
        lgll = self.extract_field(47, 3)
        self.long_period_ground_motion_lower_limit = qzss_dcr_jma_long_period_ground_motion_lower_limit[lgll]
        self.long_period_ground_motion_lower_limit_raw = lgll

        lgul = self.extract_field(50, 3)
        self.long_period_ground_motion_upper_limit = qzss_dcr_jma_long_period_ground_motion_upper_limit[lgul]
        self.long_period_ground_motion_upper_limit_raw = lgul

        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter, self.depth_of_hypocenter_raw = self.extract_depth_field(96)
        self.magnitude, self.magnitude_raw = self.extract_magnitude_field(105, qzss_dcr_jma_eew_magnitude)
        self.seismic_epicenter, self.seismic_epicenter_raw = self.extract_seismic_epicenter_field(112)

        if self.depth_of_hypocenter_raw == 10 and self.magnitude_raw == 10:
            self.assumptive = True
        else:
            self.assumptive = False

        ll = self.extract_field(122, 4)
        self.seismic_intensity_lower_limit = qzss_dcr_jma_seismic_intensity_lower_limit[ll]
        self.seismic_intensity_lower_limit_raw = ll

        ul = self.extract_field(126, 4)
        self.seismic_intensity_upper_limit = qzss_dcr_jma_seismic_intensity_upper_limit[ul]
        self.seismic_intensity_upper_limit_raw = ul

        self.eew_forecast_regions: list[str] = []
        self.eew_forecast_regions_raw: list[int] = []
        for i in range(80):
            if self.extract_field(130 + i, 1) == 1:
                self.eew_forecast_regions.append(qzss_dcr_jma_eew_forecast_region[i + 1])
                self.eew_forecast_regions_raw.append(i + 1)

        return QzssDcReportJmaEarthquakeEarlyWarning(**self.get_params())
