from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaHypocenter


class QzssDcrDecoderJmaHypocenter(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.notifications_on_disaster_prevention = self.extract_notification_on_disaster_prevention_fields(53)
        self.occurrence_time_of_eathquake = self.extract_day_hour_min_field(80)
        self.depth_of_hypocenter = self.extract_depth_field(96)
        self.magnitude = self.extract_magnitude_field(105)
        self.seismic_epicenter = self.extract_seismic_epicenter_field(112)
        self.coordinates_of_hypocenter = self.extract_lat_lon_field(122)
        return QzssDcReportJmaHypocenter(**self.get_params())
