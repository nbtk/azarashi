"""The published schema as the tests check azarashi's own output: no key and no report type it does not define.

The published schema lets a later release add keys and report types within the same version, and
the reader ignores what it does not know. azarashi itself must add nothing it has not defined, so
the tests close every object that lists its properties, and name the report types of this version.
"""
import copy

from azarashi.json.model import TYPE_NAMES


def strict(schema):
    schema = copy.deepcopy(schema)

    def close(node):
        if isinstance(node, dict):
            if node.get('type') == 'object' and 'properties' in node:
                node['additionalProperties'] = False
            for value in node.values():
                close(value)
        elif isinstance(node, list):
            for value in node:
                close(value)

    close(schema)
    schema['$defs']['envelope']['properties']['type'] = {'enum': list(TYPE_NAMES.values())}
    return schema
