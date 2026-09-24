"""azarashi.qzss_dc_report, the report module of earlier versions, kept for code written for them.

It gives the earlier names of the report classes where they were, and the modules of the reports
today. New code uses azarashi.reports and the current class names.
"""
from ..reports import Report
from ..reports import base
from ..reports import dcr
from ..reports import dcx

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
    'Report',
    'base',
    'dcr',
    'dcx',
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
