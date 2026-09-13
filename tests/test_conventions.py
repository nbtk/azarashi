"""Rules about the package that a reader cannot check by reading one file.

Each check reads what the code is - the package namespace, the syntax tree, the files that
ship - rather than how it is worded.
"""
import ast
import inspect
import os
import pathlib

import azarashi
from azarashi.qzss_dcr_lib.exception import qzss_dcr_exception

ROOT = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent
SOURCES = sorted((ROOT / 'azarashi').rglob('*.py'))


def test_every_public_name_is_declared():
    # py.typed makes a type checker read the annotations, and mypy's re-export rule then takes a name
    # imported into __init__.py as private unless __all__ names it
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


def _raises_without_cause():
    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for handler in (n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)):
            for node in ast.walk(handler):
                if isinstance(node, ast.Raise) and node.exc is not None and node.cause is None:
                    yield f'{path.relative_to(ROOT)}:{node.lineno}'


def test_a_raise_inside_a_handler_says_how_the_two_relate():
    # without `from`, Python reports the second exception as a failure while handling the first
    assert list(_raises_without_cause()) == []


def test_the_check_looks_at_something():
    handlers = [n for path in SOURCES for n in ast.walk(ast.parse(path.read_text(encoding='utf-8')))
                if isinstance(n, ast.ExceptHandler)]
    assert len(handlers) > 40 and len(SOURCES) > 90


def test_every_function_is_annotated():
    missing = []
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                arguments += [a for a in (node.args.vararg, node.args.kwarg) if a is not None]
                unannotated = [a.arg for a in arguments if a.annotation is None and a.arg not in ('self', 'cls')]
                if unannotated or node.returns is None:
                    missing.append(f'{path.relative_to(ROOT)}:{node.lineno} {node.name}')
    assert missing == []
