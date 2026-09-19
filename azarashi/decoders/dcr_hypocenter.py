from ..reports import dcr
from .dcr_common import QzssDcrDecoderJmaCommon
from ..definitions import qzss_dcr_jma_hypocenter_magnitude


class QzssDcrDecoderJmaHypocenter(QzssDcrDecoderJmaCommon):
    schema = dcr.Base

    def decode(self) -> dcr.Hypocenter:
        self.notifications_on_disaster_prevention, self.notifications_on_disaster_prevention_raw =\
            self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_earthquake, self.occurrence_time_of_earthquake_raw = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter, self.depth_of_hypocenter_raw = self.extract_depth_field(96)
        self.magnitude, self.magnitude_raw = self.extract_magnitude_field(105, qzss_dcr_jma_hypocenter_magnitude)
        self.seismic_epicenter, self.seismic_epicenter_raw = self.extract_seismic_epicenter_field(112)
        self.coordinates_of_hypocenter, self.coordinates_of_hypocenter_raw = self.extract_lat_lon_field(122)
        return dcr.Hypocenter(**self.get_params())
