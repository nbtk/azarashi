from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..definition import qzss_dcr_organization_code
from ..exception import QzssDcrDecoderException
from ..exception import QzssDcrDecoderNotImplementedError
from ..report import QzssDcReportMessageBase
from ..report import QzssDcReportOtherOrganization


class QzssDcrDecoderOtherOrganization(QzssDcrDecoderBase):
    schema = QzssDcReportMessageBase

    def decode(self):
        oc = self.extract_field(17, 6)
        try:
            self.organization_code = qzss_dcr_organization_code[oc]
        except:
            raise QzssDcrDecoderException(
                f'Undefined Organization Code : {oc}',
                self)
        self.organization_code_raw = oc

        raise QzssDcrDecoderNotImplementedError(
            f'Decoder Not Implemented (The DC Report was Sent from {self.organization_code})',
            self)

        # TODO: will be implemented.
        return QzssDcReportOtherOrganization(**self.get_params())
