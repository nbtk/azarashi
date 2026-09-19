from . import reports
from ._legacy import *  # every earlier name; delete with the module
from .api import decode
from .api import decode_stream
from .exceptions import AzarashiDecodeError
from .exceptions import AzarashiError
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiNotImplementedError
from .exceptions import AzarashiTimeoutError
from .reports import Report

__all__ = [
    # the two entry points
    'decode',
    'decode_stream',

    # the report classes, and the type of what the entry points return
    'reports',
    'Report',

    # every exception azarashi defines
    'AzarashiError',
    'AzarashiDecodeError',
    'AzarashiInvalidMessageError',
    'AzarashiNotImplementedError',
    'AzarashiTimeoutError',

    # every earlier name; delete this block with _legacy.py
    'qzss_dc_report',
    'QzssDcReport',
    'QzssDcrDecoderException',
    'QzssDcrDecoderNotImplementedError',
    'QzssDcrDecoderTimeoutError',
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
    'QzssDcxAlertBase',
    'QzssDcxCamf',
    'QzssDcxJAlert',
    'QzssDcxLAlert',
    'QzssDcxMTInfo',
    'QzssDcxNullMsg',
    'QzssDcxOutsideJapan',
    'QzssDcxUnknown',
]
