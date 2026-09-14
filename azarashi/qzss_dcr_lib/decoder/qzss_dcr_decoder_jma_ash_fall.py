from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_ash_fall_warning_code
from ..definition import qzss_dcr_jma_ash_fall_warning_type
from ..definition import qzss_dcr_jma_expected_ash_fall_time
from ..definition import qzss_dcr_jma_volcano_name
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaAshFall
from ..report import QzssDcReportJmaBase


class QzssDcrDecoderJmaAshFall(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self) -> QzssDcReportJmaAshFall:
        self.activity_time = self.extract_day_hour_min_field(53)

        dw1 = self.extract_field(69, 2)
        try:
            self.ash_fall_warning_type = qzss_dcr_jma_ash_fall_warning_type[dw1]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Ash Fall Warning Type: {dw1}',
                self) from err
        self.ash_fall_warning_type_raw = dw1

        vo = self.extract_field(71, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except KeyError as err:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcano Name: {vo}',
                self) from err
        self.volcano_name_raw = vo

        self.expected_ash_fall_times: list[str] = []
        self.expected_ash_fall_times_raw: list[int] = []
        self.ash_fall_warning_codes: list[str] = []
        self.ash_fall_warning_codes_raw: list[int] = []
        self.local_governments: list[str] = []
        self.local_governments_raw: list[int] = []
        for i in range(4):
            offset = 83 + i * 29
            if self.extract_field(offset, 29) == 0:
                break

            ho = self.extract_field(offset, 3)
            try:
                self.expected_ash_fall_times.append(qzss_dcr_jma_expected_ash_fall_time[ho])
            except KeyError as err:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Expected Ash Fall Time: {ho}',
                    self) from err
            self.expected_ash_fall_times_raw.append(ho)

            dw2 = self.extract_field(offset + 3, 3)
            try:
                self.ash_fall_warning_codes.append(qzss_dcr_jma_ash_fall_warning_code[dw2])
            except KeyError as err:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Ash Fall Warning Code: {dw2}',
                    self) from err
            self.ash_fall_warning_codes_raw.append(dw2)

            local_government, lg = self.extract_local_government(offset + 6)
            self.local_governments.append(local_government)
            self.local_governments_raw.append(lg)

        return QzssDcReportJmaAshFall(**self.get_params())
