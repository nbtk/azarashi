"""What the package exports and ships."""
import importlib
import inspect
import os
import pathlib
import re

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
    assert "package_data={'azarashi': ['py.typed'], 'azarashi.json': ['schemas/*.json']}" in setup
    assert "'Typing :: Typed'" in setup


def test_the_earlier_names_are_all_in_one_module():
    # Compatibility aliases belong in _legacy.py and the package exports only.
    # Internal modules must use the current names.
    legacy = importlib.import_module('azarashi._legacy')
    assert set(legacy.__all__) <= set(azarashi.__all__)
    assert all(getattr(azarashi, name) is getattr(legacy, name) for name in legacy.__all__)
    for path in (ROOT / 'azarashi').rglob('*.py'):
        if path.name in ('__init__.py', '_legacy.py'):
            continue
        assert '_legacy' not in path.read_text(encoding='utf-8'), f'{path} would keep the earlier names alive'


def test_no_earlier_name_is_used_inside_the_package():
    legacy = importlib.import_module('azarashi._legacy')
    # __init__.py names them in __all__ on purpose, which is the block that goes with the module
    used = [f'{path.relative_to(ROOT)}: {name}'
            for path in (ROOT / 'azarashi').rglob('*.py') if path.name not in ('_legacy.py', '__init__.py')
            for name in legacy.__all__ if re.search(rf'\b{name}\b', path.read_text(encoding='utf-8'))]
    assert used == []
