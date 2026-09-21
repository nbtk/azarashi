"""Code tables: CodeTable lookups, and conventions that every table follows."""
import ast
import importlib
import pathlib
import pkgutil
import unicodedata
import warnings

import pytest

from azarashi import decoders
from azarashi import definitions
from azarashi.definitions.code_table import CodeTable
from azarashi.definitions.qzss.dcx.message_type import MessageType


def _prefecture(code):
    return code // 100


def test_defined_codes():
    table = CodeTable({1: 'one'}, undefined='code %d')
    assert (table[1], table.get(1), 1 in table, 2 in table) == ('one', 'one', True, False)


def test_undefined_string_is_formatted_with_the_code():
    assert CodeTable({1: 'one'}, undefined='code %d')[2] == 'code 2'


def test_undefined_value_that_is_not_a_string_is_returned_as_is():
    assert CodeTable({1: 184}, undefined=183)[2] == 183


def test_without_undefined_a_missing_code_is_a_key_error():
    table = CodeTable({1: 'one'})
    with pytest.raises(KeyError):
        table[2]
    assert table.get(2) is None


def test_prefix_names_a_missing_code_after_its_group():
    table = CodeTable({101: 'one'}, prefix={1: 'group one (%d)'}, prefix_extractor=_prefecture,
                              undefined='code %d')
    assert (table[101], table[102], table[202]) == ('one', 'group one (102)', 'code 202')


def test_prefix_without_undefined():
    table = CodeTable({101: 'one'}, prefix={1: 'group one (%d)'}, prefix_extractor=_prefecture)
    assert table[102] == 'group one (102)'
    with pytest.raises(KeyError):
        table[202]


@pytest.mark.parametrize('kwargs, message', [
    ({'prefix': {1: '%d'}}, 'prefix and prefix_extractor should be both set or both None'),
    ({'prefix_extractor': _prefecture}, 'prefix and prefix_extractor should be both set or both None'),
    ({'prefix': {1: '%d'}, 'prefix_extractor': _prefecture, 'undefined': 0}, 'prefix is ignored when undefined is not a string'),
])
def test_inconsistent_settings_warn(kwargs, message):
    with pytest.warns(RuntimeWarning, match=message):
        CodeTable({}, **kwargs)


def test_consistent_settings_do_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        CodeTable({}, prefix={1: '%d'}, prefix_extractor=_prefecture, undefined='%d')
        CodeTable({}, undefined=0)


def _tables():
    for module_info in pkgutil.walk_packages(definitions.__path__, definitions.__name__ + '.'):
        relative = module_info.name.removeprefix(definitions.__name__ + '.')
        module = importlib.import_module(module_info.name)
        for name, value in vars(module).items():
            if isinstance(value, CodeTable):
                yield f'{relative}.{name}', value
            elif isinstance(value, dict) and value and all(isinstance(v, CodeTable) for v in value.values()):
                for key, table in value.items():
                    yield f'{relative}.{name}[{key}]', table


TABLES = dict(_tables())


def test_tables_are_found():
    assert len(TABLES) > 80


@pytest.mark.parametrize('name', sorted(TABLES))
def test_table_texts_are_nfc(name):
    table = TABLES[name]
    texts = [v for v in table.values() if isinstance(v, str)]
    texts += [t for t in (table.undefined, *(table.prefix or {}).values()) if isinstance(t, str)]
    for text in texts:
        assert unicodedata.normalize('NFC', text) == text, text  # e.g. no か followed by a combining dakuten


@pytest.mark.parametrize('name', sorted(TABLES))
def test_undefined_codes_are_named(name):
    table = TABLES[name]
    if table.undefined is None:  # codes that the decoders reject
        assert name in {'qzss.dcr.disaster_category.disaster_category',
                        'qzss.dcr.disaster_category.disaster_category_en',
                        'qzss.l1s.message_types',
                        'qzss.ubx.svid_to_prn'}
    elif isinstance(table.undefined, str):
        key = next((k for k in range(1 << 16) if k not in table), None) if not name.startswith('qzss.dcx.message_type') \
            else None
        if key is not None:
            assert f'{key}' in table[key]
    for text in (table.prefix or {}).values():
        assert text.count('%d') == 1


def _tables_of(node, module):
    return {sub.value.id for sub in ast.walk(node)
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name)
            and isinstance(getattr(module, sub.value.id, None), CodeTable)}


@pytest.mark.parametrize('path', sorted(pathlib.Path(decoders.__path__[0]).rglob('*.py')), ids=lambda p: p.name)
def test_a_lookup_is_guarded_only_where_the_table_can_fail(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    relative = path.relative_to(pathlib.Path(decoders.__path__[0])).with_suffix('')
    module = importlib.import_module(decoders.__name__ + '.' + '.'.join(relative.parts))
    guarded = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and any(isinstance(handler.type, ast.Name) and handler.type.id == 'KeyError'
                                             for handler in node.handlers):
            for statement in node.body:
                guarded |= _tables_of(statement, module)

    for name in _tables_of(tree, module):
        can_fail = getattr(module, name).undefined is None
        assert (name in guarded) is can_fail, name


@pytest.mark.parametrize('name', sorted(TABLES))
def test_table_keys_and_values(name):
    table = TABLES[name]
    for key, value in table.items():
        assert isinstance(key, int if name != 'qzss.dcx.message_type.message_type' else MessageType)
        assert value is None or isinstance(value, str if name != 'qzss.ubx.svid_to_prn' else int)
