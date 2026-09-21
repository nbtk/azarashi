"""Compatibility aliases for earlier public names.

Aliases are defined here and re-exported by the package. Internal code uses the current names.
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
