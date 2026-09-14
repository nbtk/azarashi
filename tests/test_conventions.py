"""What the package exports and ships."""
import inspect
import os
import pathlib

import azarashi
from azarashi.qzss_dcr_lib.exception import qzss_dcr_exception

ROOT = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent


def test_every_public_name_is_declared():
    # with py.typed, mypy takes a name imported into __init__.py as private unless __all__ lists it
    public = {name for name in dir(azarashi)
              if not name.startswith('_') and not (inspect.ismodule(getattr(azarashi, name)) and name != 'qzss_dc_report')}
    assert public - set(azarashi.__all__) == set()


def test_every_declared_name_exists():
    assert all(hasattr(azarashi, name) for name in azarashi.__all__)


def test_every_exception_is_exported():
    exceptions = {name for name, cls in vars(qzss_dcr_exception).items()
                  if isinstance(cls, type) and issubclass(cls, BaseException) and cls.__module__ == qzss_dcr_exception.__name__}
    assert exceptions and exceptions <= set(azarashi.__all__)


def test_the_typing_marker_is_there_and_ships():
    assert (ROOT / 'azarashi' / 'py.typed').is_file()
    setup = (ROOT / 'setup.py').read_text(encoding='utf-8')
    assert "package_data={'azarashi': ['py.typed']}" in setup
    assert "'Typing :: Typed'" in setup
