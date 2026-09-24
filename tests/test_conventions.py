"""What the package exports and ships."""
import importlib
import inspect
import os
import pathlib
import re

import pytest

import azarashi
from azarashi import exceptions

ROOT = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent
LEGACY = ROOT / 'azarashi' / '_legacy'  # every earlier name, and nothing else


def _outside_legacy():
    """The package's modules but _legacy/ and the package __init__.py, which names the earlier names in __all__."""
    return [path for path in (ROOT / 'azarashi').rglob('*.py')
            if LEGACY not in path.parents and path != ROOT / 'azarashi' / '__init__.py']


def test_every_public_name_is_declared():
    # with py.typed, mypy takes a name imported into __init__.py as private unless __all__ lists it
    modules = {'reports', 'qzss_dc_report'}  # the report modules the package hands out, today's and the earlier one
    public = {name for name in dir(azarashi)
              if not name.startswith('_') and not (inspect.ismodule(getattr(azarashi, name)) and name not in modules)}
    assert public - set(azarashi.__all__) == set()
    assert modules <= public  # a module dropped from __init__.py would otherwise go unnoticed


def test_every_declared_name_exists():
    assert all(hasattr(azarashi, name) for name in azarashi.__all__)


def test_every_exception_is_exported():
    defined = {name for name, cls in vars(exceptions).items()
               if isinstance(cls, type) and issubclass(cls, BaseException) and cls.__module__ == exceptions.__name__}
    assert defined and defined <= set(azarashi.__all__)


def test_the_typing_marker_is_there_and_ships():
    assert (ROOT / 'azarashi' / 'py.typed').is_file()
    setup = (ROOT / 'setup.py').read_text(encoding='utf-8')
    assert "package_data={'azarashi': ['py.typed'], 'azarashi.json': ['schemas/*.json']}" in setup
    assert "'Typing :: Typed'" in setup


def test_the_earlier_names_are_all_in_one_module():
    # Earlier names belong in _legacy/, and the package exports only. Internal modules use the current names.
    legacy = importlib.import_module('azarashi._legacy')
    assert set(legacy.__all__) <= set(azarashi.__all__)
    assert all(getattr(azarashi, name) is getattr(legacy, name) for name in legacy.__all__)
    for path in _outside_legacy():
        assert '_legacy' not in path.read_text(encoding='utf-8'), f'{path} would keep the earlier names alive'


def test_no_earlier_name_is_used_inside_the_package():
    legacy = importlib.import_module('azarashi._legacy')
    # __init__.py names them in __all__ on purpose, which is the block that goes with the module
    used = [f'{path.relative_to(ROOT)}: {name}'
            for path in _outside_legacy()
            for name in legacy.__all__ if re.search(rf'\b{name}\b', path.read_text(encoding='utf-8'))]
    assert used == []


#: every report class of azarashi.qzss_dc_report in v0.16.4, and the class it is now
EARLIER_REPORT_CLASSES = {
    'QzssDcReportBase': 'base.Base',
    'QzssDcReportMessageBase': 'base.MessageBase',
    'QzssDcReportMessagePartial': 'base.MessagePartial',
    'QzssDcReportJmaBase': 'dcr.Base',
    'QzssDcReportJmaAshFall': 'dcr.AshFall',
    'QzssDcReportJmaEarthquakeEarlyWarning': 'dcr.EarthquakeEarlyWarning',
    'QzssDcReportJmaFlood': 'dcr.Flood',
    'QzssDcReportJmaHypocenter': 'dcr.Hypocenter',
    'QzssDcReportJmaMarine': 'dcr.Marine',
    'QzssDcReportJmaNankaiTroughEarthquake': 'dcr.NankaiTroughEarthquake',
    'QzssDcReportJmaNorthwestPacificTsunami': 'dcr.NorthwestPacificTsunami',
    'QzssDcReportJmaSeismicIntensity': 'dcr.SeismicIntensity',
    'QzssDcReportJmaTsunami': 'dcr.Tsunami',
    'QzssDcReportJmaTyphoon': 'dcr.Typhoon',
    'QzssDcReportJmaVolcano': 'dcr.Volcano',
    'QzssDcReportJmaWeather': 'dcr.Weather',
    'QzssDcXtendedMessageBase': 'dcx.Base',
    'QzssDcxJAlert': 'dcx.JAlert',
    'QzssDcxLAlert': 'dcx.LAlert',
    'QzssDcxMTInfo': 'dcx.MTInfo',
    'QzssDcxNullMsg': 'dcx.NullMsg',
    'QzssDcxOutsideJapan': 'dcx.OutsideJapan',
    'QzssDcxUnknown': 'dcx.Unknown',
}


@pytest.mark.parametrize('earlier, current', EARLIER_REPORT_CLASSES.items())
def test_an_earlier_report_class_is_found_where_it_was(earlier, current):
    module, name = current.split('.')
    cls = getattr(getattr(azarashi.reports, module), name)
    assert getattr(azarashi.qzss_dc_report, earlier) is cls  # azarashi.qzss_dc_report.QzssDcxLAlert, as in v0.16.4
    assert getattr(azarashi, earlier) is cls


def test_the_earlier_report_module_gives_the_report_modules_of_today():
    assert (azarashi.qzss_dc_report.base, azarashi.qzss_dc_report.dcr, azarashi.qzss_dc_report.dcx) == (
        azarashi.reports.base, azarashi.reports.dcr, azarashi.reports.dcx)
    assert azarashi.qzss_dc_report.Report == azarashi.reports.Report
