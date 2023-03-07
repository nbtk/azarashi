from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..exception import QzssDcrDecoderException
from ..definition import qzss_dcr_jma_local_government
from ..definition import qzss_dcr_jma_notification_on_disaster_prevention
from ..definition import qzss_dcr_jma_epicenter_and_hypocenter
from datetime import datetime
from datetime import timedelta


class QzssDcrDecoderJmaCommon(QzssDcrDecoderBase):
    def extract_day_hour_min_field(self, slider):
        dt_d = self.extract_field(slider, 5)
        if dt_d < 1 or dt_d > 31:
            raise QzssDcrDecoderException(
                    f'Invalid Time: {dt_d} as day',
                    self)
        dt_h = self.extract_field(slider+5, 5)
        if dt_h > 23:
            raise QzssDcrDecoderException(
                    f'Invalid Time: {dt_h} as hour',
                    self)
        dt_mi = self.extract_field(slider+10, 6)
        if dt_mi > 59:
            raise QzssDcrDecoderException(
                    f'Invalid Time: {dt_mi} as minute',
                    self)

        dt_y = self.report_time.year
        dt_mo = self.report_time.month
        if dt_d - self.report_time.day > 15:
            if dt_mo == 1:
                dt_mo = 12
                dt_y -= 1
            else:
                dt_mo -= 1
        elif self.report_time.day - dt_d > 15:
            if dt_mo == 12:
                dt_mo = 1
                dt_y += 1
            else:
                dt_mo += 1
        if dt_mo == 2 and dt_d == 29:
            while dt_y % 4 != 0 or \
                    (dt_y % 100 == 0 and dt_y % 400 != 0):
                dt_y += 1

        return datetime(year=dt_y,
                        month=dt_mo,
                        day=dt_d,
                        hour=dt_h,
                        minute=dt_mi)

    def extract_local_government(self, slider):
        lg = self.extract_field(slider, 23)
        try:
            return qzss_dcr_jma_local_government[lg]
        except KeyError:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Local Government: {lg}',
                    self)

    def extract_notification_on_disaster_prevention_fields(self, slider):
        cos = []
        for i in range(3):
            co = self.extract_field(slider+i*9, 9)
            if co == 0:
                break
            try:
                cos.append(qzss_dcr_jma_notification_on_disaster_prevention[co])
            except KeyError:
                raise QzssDcrDecoderException(
                        f'Undefined JMA Notifications on Disaster Prevention: {co}',
                        self)
        return cos

    def extract_lat_lon_field(self, slider):
        lat_ns = self.extract_field(slider, 1)
        lat_d = self.extract_field(slider+1, 7)
        if lat_d > 89:
            raise QzssDcrDecoderException(
                    f'Invalid Latitude: {lat_d} as degree',
                    self)
        lat_m = self.extract_field(slider+8, 6)
        if lat_m > 59:
            raise QzssDcrDecoderException(
                    f'Invalid Latitude: {lat_m} as minute',
                    self)
        lat_s = self.extract_field(slider+14, 6)
        if lat_s > 59:
            raise QzssDcrDecoderException(
                    f'Invalid Latitude: {lat_s} as second',
                    self)

        lon_ew = self.extract_field(slider+20, 1)
        lon_d = self.extract_field(slider+21, 8)
        if lon_d > 179:
            raise QzssDcrDecoderException(
                    f'Invalid Longitude: {lon_d} as degree',
                    self)
        lon_m = self.extract_field(slider+29, 6)
        if lon_m > 59:
            raise QzssDcrDecoderException(
                    f'Invalid Longitude: {lon_d} as minute',
                    self)
        lon_s = self.extract_field(slider+35, 6)
        if lon_s > 59:
            raise QzssDcrDecoderException(
                    f'Invalid Longitude: {lon_s} as second',
                    self)

        return {'lat_ns': lat_ns, 'lat_d': lat_d, 'lat_m': lat_m, 'lat_s': lat_s,
                'lon_ew': lon_ew, 'lon_d': lon_d, 'lon_m': lon_m, 'lon_s': lon_s}

    def extract_depth_field(self, slider):
        de = self.extract_field(slider, 9)
        if de == 501:
            return '500kmより深い'
        elif de == 511:
            return '不明'
        elif 501 < de < 511:
            raise QzssDcrDecoderException(
                    f'Invalid Depth of Hypocenter: {de}',
                    self)
        else:
            return f'{de}km'

    def extract_magnitude_field(self, slider):
        ma = self.extract_field(slider, 7)
        if ma == 101:
            return '10.0より大きい'
        elif ma == 126:
            return '不明(8.0より大きい)'
        elif ma == 127:
            return '不明'
        elif ma < 1 or (101 < ma < 126):
            raise QzssDcrDecoderException(
                    f'Invalid Magnitude: {ma / 10}',
                    self)
        else:
            return f'{ma / 10}'

    def extract_seismic_epicenter_field(self, slider):
        ep = self.extract_field(slider, 10)
        try:
            return qzss_dcr_jma_epicenter_and_hypocenter[ep]
        except KeyError:
            raise QzssDcrDecoderException(
                    f'Undefined JMA Seismic Epicenter: {ep}',
                    self)

    def extract_expected_tsunami_arrival_time(self, slider):
        ta_h = self.extract_field(slider+1, 5)
        if ta_h == 31:
            return None
        elif ta_h > 23:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Expected Tsunami Arrivale Time: {ta_h} as hour',
                    self)

        ta_m = self.extract_field(slider+6, 6)
        if ta_m == 63:
            return None
        elif ta_m > 59:
            raise QzssDcrDecoderException(
                    f'Invalid JMA Expected Tsunami Arrivale Time: {ta_m} as minute',
                    self)

        ta_dt = self.report_time + timedelta(self.extract_field(slider, 1))

        return datetime(year=ta_dt.year,
                        month=ta_dt.month,
                        day=ta_dt.day,
                        hour=ta_h,
                        minute=ta_m)
