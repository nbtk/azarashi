"""The declared types of the report attributes against the values that decoding puts in them.

With py.typed, the type checkers of callers trust these annotations. mypy and pyright check the
decoders and the reports against each other, so they miss an annotation that both get wrong;
decoding real and crafted messages finds it.
"""
import datetime
import inspect
import os
import pathlib
import re
import types
import typing

import pytest

import azarashi
from azarashi.decoders import NmeaQzssDcrDecoder
from azarashi import reports
from qzqsm import jma
from qzqsm import sfrbx
from test_dcx_fields import B4_FIELDS
from test_dcx_fields import ELLIPSE
from test_dcx_fields import JAPAN
from test_dcx_fields import dcx
from test_jma_reports import ASH_FALL
from test_jma_reports import EEW
from test_jma_reports import FLOOD
from test_jma_reports import HYPOCENTER
from test_jma_reports import NORTHWEST_PACIFIC_TSUNAMI
from test_jma_reports import TSUNAMI
from test_jma_reports import TYPHOON
from test_jma_reports import VOLCANO
from test_jma_reports import WEATHER

TESTS = os.path.dirname(os.path.realpath(__file__))
ROOT = pathlib.Path(TESTS).parent
RECEIVED = datetime.datetime(2026, 3, 7, 6, 0, tzinfo=datetime.UTC)


def _messages():
    for log in ('qzqsm_220307.log', 'qzqsm_dcx_240604.log'):
        with open(os.path.join(TESTS, log), encoding='utf-8') as f:
            yield from (line.strip() for line in f if line.startswith('$QZQSM'))
    yield from (jma(1, EEW), jma(1, EEW + [(47, 3, 0), (50, 3, 0)]), jma(2, HYPOCENTER), jma(5, TSUNAMI),
                jma(5, TSUNAMI + [(85, 5, 31)]), jma(6, NORTHWEST_PACIFIC_TSUNAMI), jma(8, VOLCANO),
                jma(8, VOLCANO + [(50, 3, 7)]), jma(9, ASH_FALL), jma(10, WEATHER), jma(11, FLOOD), jma(12, TYPHOON),
                jma(14, [(53, 5, 22), (58, 14, 1030)]), jma(4, [(53, 4, 5), (201, 6, 1), (207, 6, 1)]))
    yield from (dcx(**{**ELLIPSE, 'a9': 0, 'a11': 3, 'a17': a17}) for a17 in range(4))
    yield from (dcx(**ELLIPSE, a4=a4, a17=3) for hazards, _ in B4_FIELDS for a4 in hazards)
    yield dcx(**JAPAN, a3=1, ex1=1100)
    yield dcx(**JAPAN, a3=4, ex1=1100, ex2=1, ex3=1, ex4=2, ex5=3, ex6=4, ex7=5, a9=1, a11=126)
    yield dcx(**JAPAN, a3=2, ex8=0, ex9=1 << 63)
    yield dcx([(147, 16, 1100)], **JAPAN, a3=2, ex8=1)
    yield dcx(**JAPAN, a3=5)
    yield dcx(a2=111)


def _reports():
    nankai = reports.jma.NankaiTroughEarthquake
    assembly = dict(nankai.reports), nankai.completed, nankai.announcement  # reports is updated in place
    decoded = []
    try:
        for message in _messages():
            try:
                decoded.append(NmeaQzssDcrDecoder(message, timestamp=RECEIVED).decode())
            except azarashi.AzarashiInvalidMessageError:
                continue
    finally:  # the pages are assembled in the class: leave it as the other tests expect to find it
        nankai.reports, nankai.completed, nankai.announcement = assembly
    return decoded


REPORTS = _reports()


def _fits(value, annotation):
    """Whether a value is one of the things the annotation allows."""
    if annotation is typing.Any:
        return True
    if annotation is type(None) or annotation is None:
        return value is None
    origin = typing.get_origin(annotation)
    if origin in (typing.Union, types.UnionType):
        return any(_fits(value, arg) for arg in typing.get_args(annotation))
    if typing.is_typeddict(annotation):
        hints = typing.get_type_hints(annotation)
        return isinstance(value, dict) and value.keys() == hints.keys() and \
            all(_fits(value[k], hints[k]) for k in hints)
    if origin is list:
        (inner,) = typing.get_args(annotation)
        return isinstance(value, list) and all(_fits(v, inner) for v in value)
    if origin is dict:
        key, val = typing.get_args(annotation)
        return isinstance(value, dict) and all(_fits(k, key) and _fits(v, val) for k, v in value.items())
    if origin is tuple:
        args = typing.get_args(annotation)
        return isinstance(value, tuple) and len(value) == len(args) and all(map(_fits, value, args))
    if annotation is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if annotation is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, annotation)


def _declared(cls):
    """Attribute name -> annotation, from the class bodies and the __init__ parameters along the MRO."""
    declared = {}
    for klass in reversed(cls.__mro__):
        if klass is object:
            continue
        hints = typing.get_type_hints(klass)
        declared.update({k: v for k, v in hints.items() if typing.get_origin(v) is not typing.ClassVar})
        if '__init__' in vars(klass):
            init = typing.get_type_hints(klass.__init__)
            for name, parameter in inspect.signature(klass.__init__).parameters.items():
                if name in init and parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    declared[name] = init[name]
    return declared


def test_there_are_reports_of_every_kind():
    kinds = {type(report) for report in REPORTS}
    concrete = {cls for module in (reports.dcx, reports.jma) for cls in vars(module).values()
                if isinstance(cls, type) and cls.__module__.startswith(reports.__name__)
                and cls.__name__.startswith(('QzssDcReportJma', 'QzssDcx')) and not cls.__name__.endswith('Base')
                and cls is not reports.dcx.Camf}
    assert concrete - kinds == set()
    assert len(REPORTS) > 400


@pytest.mark.parametrize('report', REPORTS, ids=lambda r: f'{type(r).__name__}-{r.nmea[10:26]}')
def test_every_attribute_is_declared_and_fits(report):
    declared = _declared(type(report))
    for name, value in vars(report).items():
        assert name in declared, f'{type(report).__name__}.{name} is not declared'
        assert _fits(value, declared[name]), f'{type(report).__name__}.{name} = {value!r} is not {declared[name]}'


def test_every_declared_attribute_can_be_read():
    # a declared attribute that does not exist is a hint that lies: the checker passes and the read raises
    missing = [f'{type(report).__name__}.{name}'
               for report in REPORTS for name in _declared(type(report))
               if not hasattr(report, name)]
    assert missing == []


def test_a_null_message_declares_no_alert_field():
    null = next(r for r in REPORTS if type(r) is reports.dcx.NullMsg)
    alert = _declared(reports.dcx.AlertBase).keys() - _declared(type(null)).keys()
    assert {'a1_message_type', 'a4_hazard_category', 'a12_ellipse_centre_latitude'} <= alert
    assert not any(hasattr(null, name) for name in alert)


def test_camf_fields_are_declared_ints():
    declared = typing.get_type_hints(reports.dcx.Camf)
    seen = set()
    for report in REPORTS:
        camf = getattr(report, 'camf', None)
        for name, value in (vars(camf) if camf is not None else {}).items():
            assert _fits(value, declared[name]) and type(value) is int, name
            seen.add(name)
    assert {'a1', 'c1', 'c5', 'c7', 'd1', 'd36', 'ex9', 'vn'} <= seen


def test_only_the_camf_c_and_d_fields_are_optional():
    # the message carries the rest whatever it says, so only these are read under a condition
    declared = typing.get_type_hints(reports.dcx.Camf)
    optional = {name for name, ann in declared.items() if type(None) in typing.get_args(ann)}
    assert optional == {f'c{i}' for i in range(1, 11)} | {f'd{i}' for i in range(1, 37)}


def test_every_declared_camf_field_can_be_read():
    camfs = [report.camf for report in REPORTS if hasattr(report, 'camf')]
    declared = typing.get_type_hints(reports.dcx.Camf)
    assert camfs and [f'{name}' for camf in camfs for name in declared if not hasattr(camf, name)] == []


def test_the_nankai_assembly_state_is_declared():
    hints = typing.get_type_hints(reports.jma.NankaiTroughEarthquake)
    cls = reports.jma.NankaiTroughEarthquake
    for name in ('completed', 'reports', 'announcement'):
        assert typing.get_origin(hints[name]) is typing.ClassVar
        (inner,) = typing.get_args(hints[name])
        assert _fits(getattr(cls, name), inner), name


def test_what_decode_returns_is_a_report():
    alias = typing.get_args(reports.Report)
    assert all(isinstance(report, alias) for report in REPORTS)
    assert isinstance(azarashi.decode(sfrbx(jma(12, TYPHOON)), 'ublox'), reports.Report)


def _rendered(annotation):
    """An annotation the way docs/reports.md spells it."""
    text = str(annotation).replace('typing.', '').replace("<class '", '').replace("'>", '')
    return re.sub(r'azarashi[\w.]*\.', '', text.replace('datetime.datetime', 'datetime'))


def test_the_documented_types_are_the_declared_ones():
    # the DCX tables list a hundred fields by hand, and an annotation that changes has to reach them
    declared = {}
    for module in (reports.base, reports.dcx, reports.jma):
        for cls in vars(module).values():
            if isinstance(cls, type) and cls.__module__.startswith(reports.__name__):
                hints = typing.get_type_hints(cls)
                for field in getattr(cls, '__annotations__', {}):
                    declared.setdefault(field, _rendered(hints[field]))
    rows = re.findall(r'^\| `(\w+)` \| `([^`]+)` \|', (ROOT / 'docs' / 'reports.md').read_text(encoding='utf-8'), re.M)
    checked = [(field, shown.replace('\\|', '|')) for field, shown in rows if field in declared]
    assert len(checked) > 80  # a parser that matches nothing would agree with anything
    assert [f'{field}: {shown} is not {declared[field]}' for field, shown in checked
            if shown != declared[field]] == []


def test_the_check_would_notice_a_wrong_one():
    assert not _fits(256, dict[str, int])
    assert not _fits([1, None], list[int])
    assert not _fits({'day': 1, 'hour': 2}, reports.base.DayHourMinute)
    assert not _fits(True, int)
    assert not _fits('7.2', float)
    assert _fits(7, float)
    assert _fits({'day': 1, 'hour': 2, 'minute': 3}, reports.base.DayHourMinute)
