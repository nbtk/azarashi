"""The names azarashi went by before, kept so that code written against them still runs.

Nothing inside the package uses them. Deleting this module, the two lines that name it in
__init__.py and the entries it adds to __all__ takes every one of them away at once.
"""
from . import reports as qzss_dc_report
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiNotImplementedError
from .exceptions import AzarashiTimeoutError
from .reports import Report as QzssDcReport
from .reports import base
from .reports import dcx
from .reports import jma

QzssDcrDecoderException = AzarashiInvalidMessageError
QzssDcrDecoderNotImplementedError = AzarashiNotImplementedError
QzssDcrDecoderTimeoutError = AzarashiTimeoutError

QzssDcReportBase = base.Base
QzssDcReportJmaAshFall = jma.AshFall
QzssDcReportJmaBase = jma.Base
QzssDcReportJmaEarthquakeEarlyWarning = jma.EarthquakeEarlyWarning
QzssDcReportJmaFlood = jma.Flood
QzssDcReportJmaHypocenter = jma.Hypocenter
QzssDcReportJmaMarine = jma.Marine
QzssDcReportJmaNankaiTroughEarthquake = jma.NankaiTroughEarthquake
QzssDcReportJmaNorthwestPacificTsunami = jma.NorthwestPacificTsunami
QzssDcReportJmaSeismicIntensity = jma.SeismicIntensity
QzssDcReportJmaTsunami = jma.Tsunami
QzssDcReportJmaTyphoon = jma.Typhoon
QzssDcReportJmaVolcano = jma.Volcano
QzssDcReportJmaWeather = jma.Weather
QzssDcReportMessageBase = base.MessageBase
QzssDcReportMessagePartial = base.MessagePartial
QzssDcXtendedMessageBase = dcx.Base
QzssDcxAlertBase = dcx.AlertBase
QzssDcxCamf = dcx.Camf
QzssDcxJAlert = dcx.JAlert
QzssDcxLAlert = dcx.LAlert
QzssDcxMTInfo = dcx.MTInfo
QzssDcxNullMsg = dcx.NullMsg
QzssDcxOutsideJapan = dcx.OutsideJapan
QzssDcxUnknown = dcx.Unknown

__all__ = [
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
