from calendar import monthrange
from datetime import datetime

from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_volcanic_warning_code
from ..definition import qzss_dcr_jma_volcano_name
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaVolcano


class QzssDcrDecoderJmaVolcano(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.ambiguity_of_activity_time_no = self.extract_field(50, 3)
        self.activity_time_raw = {'day': self.extract_field(53, 5),
                                  'hour': self.extract_field(58, 5),
                                  'minute': self.extract_field(63, 6)}
        self.activity_time = self.extract_activity_time(self.activity_time_raw, self.ambiguity_of_activity_time_no)

        dw = self.extract_field(69, 7)
        try:
            self.volcanic_warning_code = qzss_dcr_jma_volcanic_warning_code[dw]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcanic Warning Code: {dw}',
                self)
        self.volcanic_warning_code_raw = dw

        vo = self.extract_field(76, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcano Name: {vo}',
                self)
        self.volcano_name_raw = vo

        self.local_governments = []
        self.local_governments_raw = []
        for i in range(5):
            offset = 88 + i * 23
            if self.extract_field(offset, 23) == 0:
                break
            local_government, lg = self.extract_local_government(offset)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return QzssDcReportJmaVolcano(**self.get_params())

    def extract_activity_time(self, raw, ambiguity):
        """Observed activity time (UTC) with the parts that the ambiguity marks as not valid set to 0."""
        if ambiguity >= 6:  # approximate month or year: day, hour and minute are not valid
            return None
        day = raw['day']
        hour = raw['hour'] if ambiguity <= 4 else 0  # approximate day: hour and minute are not valid
        minute = raw['minute'] if ambiguity <= 3 else 0  # approximate hour: minute is not valid
        if day < 1 or day > 31:
            raise QzssDcrDecoderException(
                f'Invalid Time: {day} as day',
                self)
        if hour > 23:
            raise QzssDcrDecoderException(
                f'Invalid Time: {hour} as hour',
                self)
        if minute > 59:
            raise QzssDcrDecoderException(
                f'Invalid Time: {minute} as minute',
                self)

        # the activity was observed by the time of the report: take the latest such date with this day
        year, month = self.report_time.year, self.report_time.month
        if day > self.report_time.day:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)
        while day > monthrange(year, month)[1]:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)

        return datetime(year=year, month=month, day=day, hour=hour, minute=minute)
