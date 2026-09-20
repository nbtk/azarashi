from . import reports
from ._legacy import *  # every earlier name; delete with the module
from .api import decode
from .api import decode_stream
from .exceptions import AzarashiDecodeError
from .exceptions import AzarashiDisconnectedError
from .exceptions import AzarashiException
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiNoMoreData
from .exceptions import AzarashiNotImplementedError
from .exceptions import AzarashiReadOn
from .exceptions import AzarashiReopenStream
from .exceptions import AzarashiStopReading
from .exceptions import AzarashiStreamClosedError
from .exceptions import AzarashiTimeoutError
from .reports import Report

__all__ = [
    # the two entry points
    'decode',
    'decode_stream',

    # the report classes, and the type of what the entry points return
    'reports',
    'Report',

    # every exception azarashi defines, in the order of the hierarchy: the three that say what
    # to do next, and under each the ones that say what happened
    'AzarashiException',
    'AzarashiReadOn',
    'AzarashiDecodeError',
    'AzarashiInvalidMessageError',
    'AzarashiNotImplementedError',
    'AzarashiTimeoutError',
    'AzarashiReopenStream',
    'AzarashiDisconnectedError',
    'AzarashiStreamClosedError',
    'AzarashiStopReading',
    'AzarashiNoMoreData',

    # every earlier name; delete this block with _legacy.py
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
