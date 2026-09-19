"""What the package exports and ships."""
import inspect
import os
import pathlib

import azarashi
from azarashi import exceptions

ROOT = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent


def test_every_public_name_is_declared():
    # with py.typed, mypy takes a name imported into __init__.py as private unless __all__ lists it
    modules = {'reports', 'qzss_dc_report'}  # the two names of the one module the package hands out
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
    assert "package_data={'azarashi': ['py.typed']}" in setup
    assert "'Typing :: Typed'" in setup
