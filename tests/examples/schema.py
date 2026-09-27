"""The JSON v2 schema, built from the tables the conversion itself uses.

azarashi/json/schemas/report-v2.schema.json is this schema as examples.generate writes it, and a
test checks that the two agree: a change to the conversion's tables and a change to the schema
cannot drift apart. The shapes that are not in those tables are written out here.
"""
import json

from azarashi.json.model import B4_NAMES, COMMON, DCR_TYPES, LISTS, PROFILES, RELATIVE_TO, SINGLES, TIMES, TYPE_NAMES

END = '$(?![\\s\\S])'
DECIMAL = '^(0|[1-9][0-9]*)' + END
DATE_TIME = '^\\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d(?:\\.\\d{1,6})?Z' + END
AT = '^\\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d\\.\\d{3}Z' + END


def ref(name):
    return {'$ref': f'#/$defs/{name}'}


def obj(properties, required=None, **extra):
    node = {'type': 'object', 'properties': properties, 'required': list(properties) if required is None else required}
    node.update(extra)
    return node


def nullable(schema):
    return {'anyOf': [schema, {'type': 'null'}]}


def code_in(table):
    return {'allOf': [ref('code'), {'properties': {'table': {'const': table}}}]}


def quantity_in(table):
    scalars, ranges, unit = PROFILES[table]
    parts = {'table': {'const': table}, 'unit': {'const': unit}}
    extra = {'properties': parts}
    if not ranges:
        extra['properties']['range'] = False
    if not scalars:  # a code of this table stands for a range or for no number, never for one number
        extra['properties']['value'] = {'type': 'null'}
    if table in RELATIVE_TO:
        extra['properties']['relative_to'] = {'const': RELATIVE_TO[table]}
    else:
        extra['properties']['relative_to'] = False
    return {'allOf': [ref('quantity'), extra]}


def dcr_field(table):
    name = 'qzss.dcr.' + table
    return quantity_in(name) if name in PROFILES else code_in(name)


def camf_field(table):
    name = 'camf.' + table
    return quantity_in(name) if name in PROFILES else code_in(name)


def time_variant(statuses, basis, source, precisions=('minute',)):
    return {'allOf': [ref('time'), {'properties': {
        'status': {'enum': statuses},
        'basis': {'const': basis},
        'precision': {'enum': list(precisions)},
        'source': ref(source),
    }}]}


defs = {}

defs['envelope'] = obj({
    'schema_version': {'const': 2},
    'type': {'type': 'string', 'pattern': '^[a-z0-9_]+(\\.[a-z0-9_]+)+' + END,
             'description': 'A report type. This version defines those its allOf names; a later release may add types.'},
    'is_test': {'type': 'boolean'},
    'message_id': {'type': 'string', 'pattern': '^[a-z0-9_]+\\.[a-z0-9_]+:(?:[0-9a-f]{2})+' + END,
                   'description': 'The first two parts of type, a colon, and the message without what differs from one '
                                  'satellite or transmission to another, in lower-case hex. Two records with the same '
                                  'message_id carry the same message.'},
    'series': obj({
        'lifecycle': {'enum': ['issue', 'correction', 'cancellation', 'update', 'all_clear', None]},
        'key': {'type': 'string', 'minLength': 1},
    }, required=[], description='How the message stands among others: what it does to its series, and the key that '
                                'names the series. A key applies only to the report types whose specification says '
                                'which messages belong together.'),
    'reception': obj({
        'at': {'type': 'string', 'format': 'date-time', 'pattern': AT},
        'satellite': nullable(obj({
            'system': {'enum': ['qzss']},
            'prn': {'type': 'integer', 'minimum': 1, 'maximum': 255,
                    '$comment': 'the PRN number as transmitted, whose width leaves room for numbers QZSS has not assigned'},
        })),
        'nmea': {'type': 'string', 'pattern': '^\\$QZQSM,[0-9]+,[0-9A-F]{63}\\*[0-9A-F]{2}' + END},
    }, required=['at', 'satellite'],
        description='What differs from one reception of the message to another. nmea is required by the report types '
                    'that have a QZQSM sentence, which is every type of this version.'),
    'texts': {'type': 'object', 'properties': {'ja': {'type': 'string', 'minLength': 1},
                                                'en': {'type': 'string', 'minLength': 1}},
              'required': [], 'minProperties': 1,
              'description': 'The report as text, by language. The language the report is written in is always there.'},
    'data': {'type': 'object'},
}, required=['schema_version', 'type', 'is_test', 'message_id', 'reception', 'texts', 'data'],
    description='What every record carries.')

defs['labels'] = {'type': 'object', 'properties': {'ja': {'type': 'string', 'minLength': 1},
                                                   'en': {'type': 'string', 'minLength': 1}}, 'required': []}

defs['code'] = obj({
    'status': {'enum': ['valid', 'special', 'undefined']},
    'code': {'type': 'string', 'pattern': DECIMAL},
    'table': {'type': 'string', 'pattern': '^[a-z0-9_]+(\\.[a-z0-9_]+)+' + END},
    'labels': ref('labels'),
}, allOf=[{'if': {'properties': {'status': {'const': 'undefined'}}},
           'then': {'properties': {'labels': {'maxProperties': 0}}}},
          {'if': {'properties': {'status': {'const': 'special'}}},
           'then': {'properties': {'labels': {'minProperties': 1}}}}],
    description='A transmitted code, named in the code table the table names. A code that is not in that table is '
                'undefined and has no labels; a special one says what it means in its labels.')

defs['range'] = obj(
    {'lower': nullable({'type': 'number'}), 'upper': nullable({'type': 'number'})},
    **{'not': {'properties': {'lower': {'type': 'null'}, 'upper': {'type': 'null'}}},
       'description': 'A range, null on a side that is open. Whether a range holds its ends is in the labels.'},
)

defs['quantity'] = {
    'type': 'object',
    'properties': {
        'status': {'enum': ['valid', 'assumed', 'special', 'undefined']},
        'value': nullable({'type': 'number'}),
        'range': ref('range'),
        'unit': {'type': 'string', 'minLength': 1, '$comment': 'UCUM; "1" for a number without a unit'},
        'relative_to': {'type': 'string', 'minLength': 1},
        'code': {'type': 'string', 'pattern': DECIMAL},
        'table': {'type': 'string', 'pattern': '^[a-z0-9_]+(\\.[a-z0-9_]+)+' + END},
        'labels': ref('labels'),
    },
    'required': ['status', 'code', 'table', 'labels'],
    'not': {'required': ['value', 'range']},
    'allOf': [
        {'if': {'properties': {'value': {'type': 'number'}}, 'required': ['value']}, 'then': {'required': ['unit']}},
        {'if': {'required': ['range']}, 'then': {'required': ['unit']}},
        {'if': {'properties': {'status': {'const': 'undefined'}}},
         'then': {'properties': {'value': {'type': 'null'}, 'labels': {'maxProperties': 0}}, 'required': ['value']}},
        {'if': {'properties': {'status': {'enum': ['valid', 'assumed']}}},
         'then': {'properties': {'value': {'type': 'number'}}}},
        {'if': {'properties': {'status': {'const': 'special'}}},
         'then': {'properties': {'labels': {'minProperties': 1}}}},
    ],
    'description': 'A code that stands for a number (value) or a range of numbers (range) in unit. A code that says '
                   'the number is unknown has a null value, and one that stands for no number has neither.',
}

defs['time'] = {
    'type': 'object',
    'properties': {
        'status': {'enum': ['valid', 'special', 'undefined']},
        'value': nullable({'type': 'string', 'format': 'date-time', 'pattern': DATE_TIME}),
        'precision': {'enum': ['minute', 'hour', 'day']},
        'basis': {'enum': ['received_at', 'report_time']},
        'labels': ref('labels'),
        'source': {'type': 'object'},
    },
    'required': ['status', 'value', 'source'],
    'allOf': [
        {'if': {'properties': {'status': {'const': 'valid'}}},
         'then': {'properties': {'value': {'type': 'string'}}, 'required': ['precision', 'basis']},
         'else': {'properties': {'value': {'type': 'null'}, 'precision': False, 'basis': False}}},
        {'if': {'properties': {'status': {'const': 'special'}}},
         'then': {'required': ['labels'], 'properties': {'labels': {'minProperties': 1}}},
         'else': {'properties': {'labels': False}}},
    ],
    'description': 'A time in UTC. precision says to what it is known, and basis which time gave the year and the '
                   'parts the message leaves out. source holds the fields the message gave.',
}

defs['day_hour_minute'] = obj({'day': {'type': 'integer', 'minimum': 0}, 'hour': {'type': 'integer', 'minimum': 0},
                               'minute': {'type': 'integer', 'minimum': 0}})
defs['month_day_hour_minute'] = obj({k: {'type': 'integer', 'minimum': 0} for k in ('month', 'day', 'hour', 'minute')})
defs['week_minute'] = obj({'week': {'type': 'integer', 'minimum': 0}, 'minute_of_week': {'type': 'integer', 'minimum': 0}})

defs['time_report_time'] = time_variant(['valid'], 'received_at', 'month_day_hour_minute')
defs['time_event'] = time_variant(['valid', 'undefined'], 'report_time', 'day_hour_minute')
defs['time_activity'] = time_variant(['valid', 'special', 'undefined'], 'report_time', 'day_hour_minute',
                                     ('minute', 'hour', 'day'))
defs['time_arrival'] = time_variant(['valid', 'special', 'undefined'], 'report_time', 'day_hour_minute')
defs['dcx_onset'] = time_variant(['valid', 'special', 'undefined'], 'received_at', 'week_minute')

defs['position'] = {
    'type': 'object',
    'properties': {
        'status': {'enum': ['valid', 'undefined']},
        'value': nullable(obj({'latitude': {'type': 'number', 'minimum': -90, 'maximum': 90},
                               'longitude': {'type': 'number', 'minimum': -180, 'maximum': 180}})),
        'unit': {'const': 'deg'},
        'source': obj({k: {'type': 'integer', 'minimum': 0} for k in (
            'latitude_hemisphere', 'latitude_degrees', 'latitude_minutes', 'latitude_seconds',
            'longitude_hemisphere', 'longitude_degrees', 'longitude_minutes', 'longitude_seconds')}),
    },
    'required': ['status', 'value', 'source'],
    'allOf': [{'if': {'properties': {'status': {'const': 'valid'}}},
               'then': {'properties': {'value': {'type': 'object'}}, 'required': ['unit']},
               'else': {'properties': {'value': {'type': 'null'}, 'unit': False}}}],
    'description': 'WGS84 latitude and longitude, north and east positive.',
}


def ellipse(centre_lat, centre_lon, comment):
    return {
        'type': 'object',
        'properties': {
            'status': {'const': 'valid'},
            'value': obj({
                'centre': obj({'latitude_deg': {'type': 'number', 'minimum': centre_lat[0], 'maximum': centre_lat[1]},
                               'longitude_deg': {'type': 'number', 'minimum': centre_lon[0], 'maximum': centre_lon[1]}}),
                'semi_major_axis_km': {'type': 'number', 'exclusiveMinimum': 0},
                'semi_minor_axis_km': {'type': 'number', 'exclusiveMinimum': 0},
                'azimuth_deg': {'type': 'number', 'minimum': -90, 'exclusiveMaximum': 90,
                                '$comment': 'A16 and EX7 count from -90 degrees'},
            }),
            'source': obj({k: {'type': 'integer', 'minimum': 0} for k in (
                'centre_latitude', 'centre_longitude', 'semi_major_axis', 'semi_minor_axis', 'azimuth')}),
        },
        'required': ['status', 'value', 'source'],
        '$comment': comment,
        'description': 'WGS84 centre; azimuth measured from east toward north, not a navigation bearing. source holds '
                       'the transmitted codes of the group the ellipse comes from.',
    }


defs['main_ellipse'] = ellipse((-90, 90), (-180, 180), 'A12 spans the poles and A13 the meridians')
defs['refined_ellipse'] = ellipse((-90, 90.01), (-180, 180.01),
                                  'C1 to C4 add up to seven eighths of an A12 or A13 step, which can pass the pole or the meridian')
defs['additional_ellipse'] = ellipse((-90, 90), (45, 225), 'EX4 counts from 45 degrees east, so it passes 180')


def version(expected):
    """The version field: valid only as expected gives it, an integer or 'any', or never with None."""
    node = obj({'status': {'enum': ['valid', 'undefined']}, 'value': {'type': 'integer', 'minimum': 0}})
    if expected == 'any':
        node['properties']['status'] = {'const': 'valid'}
    elif expected is None:
        node['properties']['status'] = {'const': 'undefined'}
    else:
        node['allOf'] = [{'if': {'properties': {'value': {'const': expected}}},
                          'then': {'properties': {'status': {'const': 'valid'}}},
                          'else': {'properties': {'status': {'const': 'undefined'}}}}]
    return node


defs['dcr_version'] = version(1)
defs['dcx_version_japan'] = version(1)
defs['dcx_version_outside_japan'] = version('any')
defs['dcx_version_unknown'] = version(None)

# DCR types
FORECAST_EXTRA = {'Tsunami': 'time_arrival', 'NorthwestPacificTsunami': 'time_arrival'}
for name in DCR_TYPES:
    props = {'version': ref('dcr_version'), 'report_time': ref('time_report_time')}
    for out, _, table in COMMON + SINGLES.get(name, []):
        props[out] = dcr_field(table)
    if name in TIMES:
        props[TIMES[name][0]] = ref('time_activity' if name == 'Volcano' else 'time_event')
    if name in ('EarthquakeEarlyWarning', 'Hypocenter', 'Tsunami'):
        props['notifications'] = {'type': 'array', 'items': dcr_field('notification_on_disaster_prevention')}
    if name in LISTS:
        out, columns = LISTS[name]
        item = {key: dcr_field(table) for key, _, table in columns}
        if name in FORECAST_EXTRA:
            item['arrival'] = ref(FORECAST_EXTRA[name])
        props[out] = {'type': 'array', 'items': obj(item)}
    if name == 'EarthquakeEarlyWarning':
        props['target_regions'] = {'type': 'array', 'items': dcr_field('eew_forecast_region')}
    if name == 'Volcano':
        props['target_regions'] = {'type': 'array', 'items': dcr_field('local_government')}
    if name in ('Hypocenter', 'Typhoon'):
        props['position'] = ref('position')
    if name == 'Volcano':
        props['activity_time_ambiguity'] = dcr_field('ambiguity_of_activity_time')
    if name == 'NankaiTroughEarthquake':
        props['page'] = obj({
            'number': {'type': 'integer', 'minimum': 0, 'maximum': 63},
            'total': {'type': 'integer', 'minimum': 0, 'maximum': 63},
            'content_hex': {'type': 'string', 'pattern': '^(?:[0-9a-f]{2})*' + END},
        }, **{'$comment': 'both are six-bit fields as transmitted; a page number of zero is one the specification '
                          'leaves undefined'})
    defs[name] = obj(props)

# DCX
defs['dcx_instruction'] = {
    'type': 'object',
    'properties': {
        'library': camf_field('a9_type_of_library'),
        'library_version': camf_field('a10_library_version'),
        'content': {'allOf': [ref('code'), {'properties': {'table': {
            'pattern': '^camf\\.a11_instruction_library\\.(international|country_(0|[1-9][0-9]*))\\.version_(0|[1-9][0-9]*)' + END}}}]},
        'identifier': nullable({'type': 'string', 'minLength': 1}),
    },
    'required': ['library', 'library_version', 'content'],
    'allOf': [{'if': {'properties': {'library': {'properties': {'code': {'const': '0'}}}}},
               'then': {'required': ['identifier']}, 'else': {'properties': {'identifier': False}}}],
    'description': "The guidance of A11, from the library A9 chooses in the version A10 gives. identifier is CAMF's "
                   'name for an instruction of its own library.',
}
defs['dcx_hazard'] = obj({part: camf_field('a4_hazard_' + part) for part in ('type', 'category', 'definition')})
defs['dcx_target_regions'] = {'type': 'array', 'items': {'allOf': [ref('code'), {'properties': {'table': {
    'enum': ['qzss.dcx.ex1_target_area_code', 'qzss.dcx.ex9_target_area_code_list']}}}]}}
defs['dcx_evacuation'] = obj({'direction': code_in('qzss.dcx.ex2_evacuate_direction_type'),
                          'ellipse': ref('additional_ellipse')})
defs['hazard_details'] = obj({name.split('_', 1)[1]: camf_field(name) for name in B4_NAMES}, required=[])
SETTINGS = ['refined_ellipse', 'hazard_centre', 'second_ellipse', 'hazard_details']
defs['specific_settings'] = {
    'type': 'object',
    'properties': {
        'type': code_in('camf.a17_type_of_specific_settings'),
        'refined_ellipse': ref('refined_ellipse'),
        'hazard_centre': {
            'type': 'object',
            'properties': {
                'status': {'const': 'valid'},
                'value': obj({'latitude_deg': {'type': 'number', 'minimum': -100, 'maximum': 100},
                              'longitude_deg': {'type': 'number', 'minimum': -190, 'maximum': 190}}),
                'source': obj({'latitude': {'type': 'integer', 'minimum': 0},
                               'longitude': {'type': 'integer', 'minimum': 0}}),
            },
            'required': ['status', 'value', 'source'],
            '$comment': 'C5 and C6 offset the main centre by up to ten degrees either way',
        },
        'second_ellipse': obj({
            'shift': camf_field('c7_shift_of_second_ellipse_centre'),
            'scale_factor': camf_field('c8_homothetic_factor_of_second_ellipse'),
            'bearing': camf_field('c9_bearing_angle_of_second_ellipse'),
            'instruction': camf_field('c10_instruction_library_for_second_ellipse'),
        }, description='CAMF B3: the second ellipse, made from the main one by C7 to C9, and its C10 instruction.'),
        'hazard_details': ref('hazard_details'),
    },
    'required': ['type'],
    'oneOf': [
        {'properties': {'type': {'properties': {'code': {'const': str(i)}}}}, 'required': [kind],
         'not': {'anyOf': [{'required': [other]} for other in SETTINGS if other != kind]}}
        for i, kind in enumerate(SETTINGS)
    ],
}

defs['dcx_message_type'] = camf_field('a1_message_type')
defs['dcx_country'] = camf_field('a2_country_region_name')
defs['dcx_severity'] = camf_field('a5_severity')
defs['dcx_duration'] = camf_field('a8_hazard_duration')
defs['dcx_provider'] = {'allOf': [ref('code'), {'properties': {'table': {
    'pattern': '^camf\\.a3_provider_identifier\\.country_(0|[1-9][0-9]*)' + END}}}]}
DCX_COMMON = {field: ref('dcx_' + field) for field in (
    'message_type', 'country', 'severity', 'duration', 'provider', 'hazard', 'onset', 'instruction')}
REQUIRED = ['version'] + list(DCX_COMMON)


def dcx_type(version_def, extra, required):
    props = {'version': ref(version_def), **DCX_COMMON, **extra}
    return obj(props, required=REQUIRED + required)


defs['OutsideJapan'] = dcx_type('dcx_version_outside_japan', {'main_ellipse': ref('main_ellipse'),
                                                      'specific_settings': ref('specific_settings')}, ['main_ellipse'])
defs['LAlert'] = dcx_type('dcx_version_japan', {'main_ellipse': ref('main_ellipse'),
                                                'specific_settings': ref('specific_settings'),
                                                'target_regions': ref('dcx_target_regions')}, [])
defs['LAlert']['oneOf'] = [{'required': ['main_ellipse'], 'not': {'required': ['target_regions']}},
                           {'required': ['target_regions'], 'not': {'required': ['main_ellipse']}}]
defs['JAlert'] = dcx_type('dcx_version_japan', {'target_regions': ref('dcx_target_regions')}, ['target_regions'])
defs['MTInfo'] = dcx_type('dcx_version_japan', {'main_ellipse': ref('main_ellipse'),
                                                'specific_settings': ref('specific_settings'),
                                                'target_regions': ref('dcx_target_regions'),
                                                'evacuation': ref('dcx_evacuation')}, ['main_ellipse', 'target_regions'])
defs['Unknown'] = dcx_type('dcx_version_unknown', {'main_ellipse': ref('main_ellipse'),
                                                 'specific_settings': ref('specific_settings')}, ['main_ellipse'])
defs['NullMsg'] = obj({}, required=[])

# series by type
DCR_SERIES = {'properties': {'lifecycle': {'enum': ['issue', 'correction', 'cancellation', None]}}, 'required': ['lifecycle']}
KEYED = {
    'NankaiTroughEarthquake': '^\\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\dZ\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)' + END,
    'LAlert': '^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*)){3}' + END,
    'MTInfo': '^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*)){3}' + END,
    'JAlert': '^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*)){2}' + END,
}

branches = []
for name, type_name in TYPE_NAMES.items():
    then = {'properties': {'data': ref(name)}}
    if name == 'NullMsg':
        then['properties']['is_test'] = {'const': False}
        then['properties']['series'] = False
    elif type_name.startswith('qzss.dcr.'):
        series = {'allOf': [DCR_SERIES]}
        if name in KEYED:
            series['allOf'].append({'properties': {'key': {'pattern': KEYED[name]}}, 'required': ['key']})
        else:
            series['allOf'].append({'properties': {'key': False}})
        then['properties']['series'] = series
        then['required'] = ['series']
    else:
        key = {'properties': {'key': {'pattern': KEYED[name]}}, 'required': ['key']} if name in KEYED else \
            {'properties': {'key': False}}
        lifecycle = {'properties': {'lifecycle': {'enum': ['issue', 'update', 'all_clear']}}}
        then['properties']['series'] = {'allOf': [key, lifecycle]}
        then['allOf'] = [{'if': {'properties': {'is_test': {'const': False}}},
                          'then': {'properties': {'series': {'required': ['lifecycle']}}, 'required': ['series']},
                          'else': {'properties': {'series': {'properties': {'lifecycle': False}}}}}]
        if name in KEYED:
            then['required'] = ['series']
    texts_required = ['en'] if name == 'NorthwestPacificTsunami' or type_name.startswith('qzss.dcx.') else ['ja']
    then['properties']['texts'] = {'required': texts_required}
    branches.append({'if': {'properties': {'type': {'const': type_name}}, 'required': ['type']}, 'then': then})

schema = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'urn:azarashi:report:2',
    'title': 'Azarashi report JSON v2',
    'description': 'One decoded report. The contract is specified in docs/json.md; serialization API is separate.',
    '$comment': 'Patterns end with $(?![\\s\\S]) rather than $, because in some regular expression engines, '
                "Python's among them, $ also matches before a trailing newline. Constraints a schema cannot express, "
                'a lower bound below its upper one, a semi-minor axis below its semi-major, a page number within its '
                'total, a message_id that begins with the type, a code and its labels as the code tables give them, '
                'are checked by the conversion tests instead.',
    '$ref': '#/$defs/envelope',
    'allOf': [{'if': {'properties': {'type': {'pattern': '^qzss\\.'}}, 'required': ['type']},
               'then': {'properties': {'reception': {'required': ['nmea']}}}}] + branches,
    '$defs': defs,
}



def schema_text():
    """The schema as the package gives it."""
    return json.dumps(schema, ensure_ascii=False, indent=2) + '\n'
