"""Code tables: QzssDcrDefinition lookups, and conventions that every table follows."""
import importlib
import pkgutil
import unicodedata
import warnings

import pytest

from azarashi.qzss_dcr_lib import definition
from azarashi.qzss_dcr_lib.definition.qzss_dcr_definition import QzssDcrDefinition
from azarashi.qzss_dcr_lib.definition.qzss_dcx_message_type import DcxMessageType


def _prefecture(code):
    return code // 100


def test_defined_codes():
    table = QzssDcrDefinition({1: 'one'}, undefined='code %d')
    assert (table[1], table.get(1), 1 in table, 2 in table) == ('one', 'one', True, False)


def test_undefined_string_is_formatted_with_the_code():
    assert QzssDcrDefinition({1: 'one'}, undefined='code %d')[2] == 'code 2'


def test_undefined_value_that_is_not_a_string_is_returned_as_is():
    assert QzssDcrDefinition({1: 184}, undefined=183)[2] == 183


def test_without_undefined_a_missing_code_is_a_key_error():
    table = QzssDcrDefinition({1: 'one'})
    with pytest.raises(KeyError):
        table[2]
    assert table.get(2) is None


def test_prefix_names_a_missing_code_after_its_group():
    table = QzssDcrDefinition({101: 'one'}, prefix={1: 'group one (%d)'}, prefix_extractor=_prefecture,
                              undefined='code %d')
    assert (table[101], table[102], table[202]) == ('one', 'group one (102)', 'code 202')


def test_prefix_without_undefined():
    table = QzssDcrDefinition({101: 'one'}, prefix={1: 'group one (%d)'}, prefix_extractor=_prefecture)
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
        QzssDcrDefinition({}, **kwargs)


def test_consistent_settings_do_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        QzssDcrDefinition({}, prefix={1: '%d'}, prefix_extractor=_prefecture, undefined='%d')
        QzssDcrDefinition({}, undefined=0)


def _tables():
    for module_info in pkgutil.iter_modules(definition.__path__):
        module = importlib.import_module(f'{definition.__name__}.{module_info.name}')
        for name, value in vars(module).items():
            if isinstance(value, QzssDcrDefinition):
                yield f'{module_info.name}.{name}', value
            elif isinstance(value, dict) and value and all(isinstance(v, QzssDcrDefinition) for v in value.values()):
                for key, table in value.items():
                    yield f'{module_info.name}.{name}[{key}]', table


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
        assert name in {'qzss_dcr_jma_disaster_category.qzss_dcr_jma_disaster_category',
                        'qzss_dcr_jma_disaster_category.qzss_dcr_jma_disaster_category_en',
                        'qzss_dcr_message_type.qzss_dcr_message_type'}
    elif isinstance(table.undefined, str):
        key = next((k for k in range(1 << 16) if k not in table), None) if not name.startswith('qzss_dcx_message_type') \
            else None
        if key is not None:
            assert f'{key}' in table[key]
    for text in (table.prefix or {}).values():
        assert text.count('%d') == 1


@pytest.mark.parametrize('name', sorted(TABLES))
def test_table_keys_and_values(name):
    table = TABLES[name]
    for key, value in table.items():
        assert isinstance(key, int if name != 'qzss_dcx_message_type.qzss_dcx_message_type' else DcxMessageType)
        assert value is None or isinstance(value, str if name != 'ublox_qzss_svid_prn_map.ublox_qzss_svid_prn_map' else int)
