from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from qzss_dcr_lib.exception import QzssDcrDecoderException
from qzss_dcr_lib.report import QzssDcReportMessageBase
from qzss_dcr_lib.report import QzssDcReportOtherOrganization 
from qzss_dcr_lib.definition import qzss_dcr_organization_code


class QzssDcrDecoderOtherOrganization(QzssDcrDecoderBase):
    schema = QzssDcReportMessageBase

    def decode(self):
        oc = self.extract_field(17, 6)
        try: 
            self.organization_code = qzss_dcr_organization_code[oc]
        except:
            raise QzssDcrDecoderException(
                    f'Undefined Organization Code : {oc}',
                    self.sentence)

        raise QzssDcrDecoderException(
                f'Decoder Not Implemented (The DC Report was Sent from {self.organization_code})',
                       self.sentence)

        return QzssDcReportOtherOrganization(**self.get_params())
