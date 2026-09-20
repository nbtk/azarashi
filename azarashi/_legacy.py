"""The names azarashi went by before, kept so that code written against them still runs.

Nothing inside the package uses them. Deleting this module, the two lines that name it in
__init__.py and the entries it adds to __all__ takes every one of them away at once.
"""
from . import reports as qzss_dc_report
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiNotImplementedError
from .reports import base
from .reports import dcx
from .reports import dcr

QzssDcrDecoderException = AzarashiInvalidMessageError
QzssDcrDecoderNotImplementedError = AzarashiNotImplementedError

QzssDcReportBase = base.Base
QzssDcReportJmaAshFall = dcr.AshFall
QzssDcReportJmaBase = dcr.Base
QzssDcReportJmaEarthquakeEarlyWarning = dcr.EarthquakeEarlyWarning
QzssDcReportJmaFlood = dcr.Flood
QzssDcReportJmaHypocenter = dcr.Hypocenter
QzssDcReportJmaMarine = dcr.Marine
QzssDcReportJmaNankaiTroughEarthquake = dcr.NankaiTroughEarthquake
QzssDcReportJmaNorthwestPacificTsunami = dcr.NorthwestPacificTsunami
QzssDcReportJmaSeismicIntensity = dcr.SeismicIntensity
QzssDcReportJmaTsunami = dcr.Tsunami
QzssDcReportJmaTyphoon = dcr.Typhoon
QzssDcReportJmaVolcano = dcr.Volcano
QzssDcReportJmaWeather = dcr.Weather
QzssDcReportMessageBase = base.MessageBase
QzssDcReportMessagePartial = base.MessagePartial
QzssDcXtendedMessageBase = dcx.Base
QzssDcxJAlert = dcx.JAlert
QzssDcxLAlert = dcx.LAlert
QzssDcxMTInfo = dcx.MTInfo
QzssDcxNullMsg = dcx.NullMsg
QzssDcxOutsideJapan = dcx.OutsideJapan
QzssDcxUnknown = dcx.Unknown

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
