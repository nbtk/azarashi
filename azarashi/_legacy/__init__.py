"""The names of earlier versions, kept so that code written for them runs unchanged.

New code uses the current names. Every earlier name lives in this package, here and in
qzss_dc_report.py, and the package azarashi hands them out; nothing inside azarashi uses them.
"""
from . import qzss_dc_report
from ..exceptions import AzarashiInvalidMessageError
from ..exceptions import AzarashiNotImplementedError
from .qzss_dc_report import QzssDcReportBase
from .qzss_dc_report import QzssDcReportJmaAshFall
from .qzss_dc_report import QzssDcReportJmaBase
from .qzss_dc_report import QzssDcReportJmaEarthquakeEarlyWarning
from .qzss_dc_report import QzssDcReportJmaFlood
from .qzss_dc_report import QzssDcReportJmaHypocenter
from .qzss_dc_report import QzssDcReportJmaMarine
from .qzss_dc_report import QzssDcReportJmaNankaiTroughEarthquake
from .qzss_dc_report import QzssDcReportJmaNorthwestPacificTsunami
from .qzss_dc_report import QzssDcReportJmaSeismicIntensity
from .qzss_dc_report import QzssDcReportJmaTsunami
from .qzss_dc_report import QzssDcReportJmaTyphoon
from .qzss_dc_report import QzssDcReportJmaVolcano
from .qzss_dc_report import QzssDcReportJmaWeather
from .qzss_dc_report import QzssDcReportMessageBase
from .qzss_dc_report import QzssDcReportMessagePartial
from .qzss_dc_report import QzssDcXtendedMessageBase
from .qzss_dc_report import QzssDcxJAlert
from .qzss_dc_report import QzssDcxLAlert
from .qzss_dc_report import QzssDcxMTInfo
from .qzss_dc_report import QzssDcxNullMsg
from .qzss_dc_report import QzssDcxOutsideJapan
from .qzss_dc_report import QzssDcxUnknown

QzssDcrDecoderException = AzarashiInvalidMessageError
QzssDcrDecoderNotImplementedError = AzarashiNotImplementedError


__all__ = [
    'qzss_dc_report',
    'QzssDcrDecoderException',
    'QzssDcrDecoderNotImplementedError',
    'QzssDcReportBase',
    'QzssDcReportJmaAshFall',
    'QzssDcReportJmaBase',
    'QzssDcReportJmaEarthquakeEarlyWarning',
    'QzssDcReportJmaFlood',
    'QzssDcReportJmaHypocenter',
    'QzssDcReportJmaMarine',
    'QzssDcReportJmaNankaiTroughEarthquake',
    'QzssDcReportJmaNorthwestPacificTsunami',
    'QzssDcReportJmaSeismicIntensity',
    'QzssDcReportJmaTsunami',
    'QzssDcReportJmaTyphoon',
    'QzssDcReportJmaVolcano',
    'QzssDcReportJmaWeather',
    'QzssDcReportMessageBase',
    'QzssDcReportMessagePartial',
    'QzssDcXtendedMessageBase',
    'QzssDcxJAlert',
    'QzssDcxLAlert',
    'QzssDcxMTInfo',
    'QzssDcxNullMsg',
    'QzssDcxOutsideJapan',
    'QzssDcxUnknown',
]
