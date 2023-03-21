from datetime import datetime

from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from .qzss_dcr_decoder_jma_ash_fall import QzssDcrDecoderJmaAshFall
from .qzss_dcr_decoder_jma_earthquake_early_warning import QzssDcrDecoderJmaEarthquakeEarlyWarning
from .qzss_dcr_decoder_jma_flood import QzssDcrDecoderJmaFlood
from .qzss_dcr_decoder_jma_hypocenter import QzssDcrDecoderJmaHypocenter
from .qzss_dcr_decoder_jma_marine import QzssDcrDecoderJmaMarine
from .qzss_dcr_decoder_jma_nankai_trough_earthquake import QzssDcrDecoderJmaNankaiTroughEarthquake
from .qzss_dcr_decoder_jma_northwest_pacific_tsunami import QzssDcrDecoderJmaNorthwestPacificTsunami
from .qzss_dcr_decoder_jma_seismic_intensity import QzssDcrDecoderJmaSeismicIntensity
from .qzss_dcr_decoder_jma_tsunami import QzssDcrDecoderJmaTsunami
from .qzss_dcr_decoder_jma_typhoon import QzssDcrDecoderJmaTyphoon
from .qzss_dcr_decoder_jma_volcano import QzssDcrDecoderJmaVolcano
from .qzss_dcr_decoder_jma_weather import QzssDcrDecoderJmaWeather
from ..definition import qzss_dcr_jma_disaster_category
from ..definition import qzss_dcr_jma_disaster_category_en
from ..definition import qzss_dcr_jma_information_type
from ..definition import qzss_dcr_jma_information_type_en
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportMessageBase


class QzssDcrDecoderJma(QzssDcrDecoderBase):
    schema = QzssDcReportMessageBase

    def decode(self):
        self.version = self.extract_field(214, 6)
        if self.version != 1:
            raise QzssDcrDecoderException(
                f'Unsupported JMA-DC Report Version: {self.version}',
                self)

        dc = self.extract_field(17, 4)
        try:
            self.disaster_category = qzss_dcr_jma_disaster_category[dc]
            self.disaster_category_en = qzss_dcr_jma_disaster_category_en[dc]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined Disaster Category: {dc}',
                self)
        self.disaster_category_no = dc

        at_mo = self.extract_field(21, 4)
        if at_mo < 1 or at_mo > 12:
            raise QzssDcrDecoderException(
                f'Invalid Report Time: {at_mo} as month',
                self)
        at_d = self.extract_field(25, 5)
        if at_d < 1 or at_d > 31:
            raise QzssDcrDecoderException(
                f'Invalid Report Time: {at_d} as day',
                self)
        at_h = self.extract_field(30, 5)
        if at_h > 23:
            raise QzssDcrDecoderException(
                f'Invalid Report Time: {at_h} as hour',
                self)
        at_mi = self.extract_field(35, 6)
        if at_mi > 59:
            raise QzssDcrDecoderException(
                f'Invalid Report Time: {at_mi} as minute',
                self)

        at_y = self.timestamp.year
        if at_mo - self.timestamp.month > 6:
            at_y -= 1
        elif self.timestamp.month - at_mo > 6:
            at_y += 1

        if at_mo == 2 and at_d == 29:
            while at_y % 4 != 0 or (at_y % 100 == 0 and at_y % 400 != 0):
                at_y += 1

        self.report_time = datetime(year=at_y,
                                    month=at_mo,
                                    day=at_d,
                                    hour=at_h,
                                    minute=at_mi)

        it = self.extract_field(41, 2)
        try:
            self.information_type = qzss_dcr_jma_information_type[it]
            self.information_type_en = qzss_dcr_jma_information_type_en[it]
        except KeyError:
            raise QzssDcrDecoderException(
                'Undefined Information Type: {it}',
                self)
        self.information_type_no = it

        if dc == 1:
            next_decoder = QzssDcrDecoderJmaEarthquakeEarlyWarning
        elif dc == 2:
            next_decoder = QzssDcrDecoderJmaHypocenter
        elif dc == 3:
            next_decoder = QzssDcrDecoderJmaSeismicIntensity
        elif dc == 4:
            next_decoder = QzssDcrDecoderJmaNankaiTroughEarthquake
        elif dc == 5:
            next_decoder = QzssDcrDecoderJmaTsunami
        elif dc == 6:
            next_decoder = QzssDcrDecoderJmaNorthwestPacificTsunami
        elif dc == 8:
            next_decoder = QzssDcrDecoderJmaVolcano
        elif dc == 9:
            next_decoder = QzssDcrDecoderJmaAshFall
        elif dc == 10:
            next_decoder = QzssDcrDecoderJmaWeather
        elif dc == 11:
            next_decoder = QzssDcrDecoderJmaFlood
        elif dc == 12:
            next_decoder = QzssDcrDecoderJmaTyphoon
        elif dc == 14:
            next_decoder = QzssDcrDecoderJmaMarine
        else:
            raise QzssDcrDecoderException(
                f'Unsupported Disaster Category: {self.disaster_category}',
                self)

        return next_decoder(**self.get_params()).decode()
