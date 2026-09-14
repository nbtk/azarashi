from calendar import monthrange
from datetime import datetime
from datetime import UTC

from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_days
from ..definition import qzss_dcr_jma_hours
from ..definition import qzss_dcr_jma_minutes
from ..definition import qzss_dcr_jma_volcanic_warning_code
from ..definition import qzss_dcr_jma_volcano_name
from ..exception import QzssDcrDecoderException
from ..report import DayHourMinute
from ..report import QzssDcReportJmaBase
from ..report import QzssDcReportJmaVolcano


class QzssDcrDecoderJmaVolcano(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaVolcano:
        self.ambiguity_of_activity_time_no = self.extract_field(50, 3)
        self.activity_time_raw = self.extract_day_hour_min_raw(53)
        self.activity_time = self.extract_activity_time(self.activity_time_raw, self.ambiguity_of_activity_time_no)

        dw = self.extract_field(69, 7)
        try:
            self.volcanic_warning_code = qzss_dcr_jma_volcanic_warning_code[dw]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcanic Warning Code: {dw}',
                self) from err
        self.volcanic_warning_code_raw = dw

        vo = self.extract_field(76, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcano Name: {vo}',
                self) from err
        self.volcano_name_raw = vo

        self.local_governments: list[str] = []
        self.local_governments_raw: list[int] = []
        for i in range(5):
            offset = 88 + i * 23
            if self.extract_field(offset, 23) == 0:
                break
            local_government, lg = self.extract_local_government(offset)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return QzssDcReportJmaVolcano(**self.get_params())

    def extract_activity_time(self, raw: DayHourMinute, ambiguity: int) -> datetime | None:
        """Observed activity time (UTC) with the parts that the ambiguity marks as not valid set to 0.

        None when the ambiguity marks no part as valid, or when the valid parts are not a time.
        """
        if ambiguity >= 6:  # approximate month or year: day, hour and minute are not valid
            return None
        day = raw['day']
        hour = raw['hour'] if ambiguity <= 4 else 0  # approximate day: hour and minute are not valid
        minute = raw['minute'] if ambiguity <= 3 else 0  # approximate hour: minute is not valid
        if day not in qzss_dcr_jma_days or hour not in qzss_dcr_jma_hours or minute not in qzss_dcr_jma_minutes:
            return None

        # the activity was observed by the time of the report: take the latest such date with this day
        year, month = self.report_time.year, self.report_time.month
        if day > self.report_time.day:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)
        while day > monthrange(year, month)[1]:
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)

        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=UTC)
