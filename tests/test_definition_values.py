"""Code table contents and fallbacks match the reference snapshot."""
import hashlib
import importlib
import json
import pathlib
from enum import Enum

import pytest


VALUES = json.loads(pathlib.Path(__file__).with_name('definition_values.json').read_text())


def _normalize(value):
    if isinstance(value, Enum):
        return ['enum', value.name, value.value]
    if isinstance(value, dict):
        return ['dict', [[_normalize(k), _normalize(v)] for k, v in value.items()],
                _normalize(getattr(value, 'undefined', None)), _normalize(getattr(value, 'prefix', None))]
    if isinstance(value, range):
        return ['range', value.start, value.stop, value.step]
    if isinstance(value, bytes):
        return ['bytes', value.hex()]
    return value


@pytest.mark.parametrize('module_name,name,digest', VALUES, ids=[row[0] + '.' + row[1] for row in VALUES])
def test_definition_values(module_name, name, digest):
    module = importlib.import_module(f'azarashi.definitions.{module_name}')
    value = getattr(module, name)
    actual = hashlib.sha256(json.dumps(_normalize(value), ensure_ascii=False).encode()).hexdigest()
    assert actual == digest
