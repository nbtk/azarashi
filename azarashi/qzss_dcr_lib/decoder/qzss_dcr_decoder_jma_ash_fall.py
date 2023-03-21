from .qzss_dcr_decoder_jma_common import QzssDcrDecoderJmaCommon
from ..definition import qzss_dcr_jma_ash_fall_warning_code
from ..definition import qzss_dcr_jma_volcano_name
from ..exception import QzssDcrDecoderException
from ..report import QzssDcReportJmaAshFall
from ..report import QzssDcReportJmaBase


class QzssDcrDecoderJmaAshFall(QzssDcrDecoderJmaCommon):
    schema = QzssDcReportJmaBase

    def decode(self):
        self.activity_time = self.extract_day_hour_min_field(53)

        dw1 = self.extract_field(69, 2)
        if dw1 == 1:
            self.ash_fall_warning_type = '速報'
        elif dw1 == 2:
            self.ash_fall_warning_type = '詳細'
        else:
            raise QzssDcrDecoderException(
                f'Undefined JMA Ash Fall Warning Type: {dw1}',
                self)

        vo = self.extract_field(71, 12)
        try:
            self.volcano_name = qzss_dcr_jma_volcano_name[vo]
        except KeyError:
            raise QzssDcrDecoderException(
                f'Undefined JMA Volcano Name: {vo}',
                self)

        self.expected_ash_fall_times = []
        self.ash_fall_warning_codes = []
        self.local_governments = []
        for i in range(4):
            offset = 83 + i * 29
            if self.extract_field(offset, 29) == 0:
                break

            ho = self.extract_field(offset, 3)
            if 1 > ho > 6:
                raise QzssDcrDecoderException(
                    f'Invalid JMA Expected Ash Fall Time: {ho}',
                    self)
            self.expected_ash_fall_times.append(ho)

            dw2 = self.extract_field(offset + 3, 3)
            try:
                self.ash_fall_warning_codes.append(qzss_dcr_jma_ash_fall_warning_code[dw2])
            except KeyError:
                raise QzssDcrDecoderException(
                    f'Undefined JMA Ash Fall Warning Code: {dw2}',
                    self)

            self.local_governments.append(self.extract_local_government(offset + 6))

        return QzssDcReportJmaAshFall(**self.get_params())
