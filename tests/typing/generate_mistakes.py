"""Write a file that uses every public function and method wrongly, one use per line.

Each line passes a wrong argument or assigns the return value to a wrong type, and ends with the
error code it should cause; check_all_reported.py checks that the type checker reports every line
with that code. The script fails for a function whose annotations accept anything, since no wrong
use can be written for it. Property return types are checked here; other report attributes are checked in consumer_mistakes.py.

  python tests/typing/generate_mistakes.py out.py
  mypy --strict out.py > mypy.txt
  python tests/typing/check_all_reported.py out.py mypy.txt
"""
import datetime
import inspect
import itertools
import sys
import types
import typing

import azarashi
from azarashi import reports
from azarashi.network.receiver import Receiver
from azarashi.network.transmitter import Transmitter

#: what contradiction() answers -> a literal of that type
ARG_VALUE = {'str': "'not the right type'", 'int': '123', 'bytes': "b'\\x00'"}
#: a value that fits the annotation, for the required arguments
SAMPLE = {int: '0', bool: 'False', float: '0.0', str: "''", bytes: "b''", list: '[]', dict: '{}', tuple: '()',
          datetime.datetime: 'datetime.datetime.now()'}
_numbers = itertools.count()
#: the arguments that are right to accept anything
OPEN = {('AzarashiInvalidMessageError.__init__', 'instance'): 'the object a message came from, whatever it is',
        ('AzarashiNotImplementedError.__init__', 'instance'): 'the object a message came from, whatever it is'}


def base_of(ann):
    o = typing.get_origin(ann)
    return o if o is not None else ann


def contradiction(ann):
    """A type that is incompatible with the annotation in either direction."""
    if ann is inspect.Signature.empty or ann is None:
        return None
    allowed = set()
    stack = [ann]
    while stack:
        a = stack.pop()
        if typing.get_origin(a) in (typing.Union, types.UnionType):
            stack.extend(typing.get_args(a))
            continue
        allowed.add(dict if typing.is_typeddict(a) else base_of(a))
    if typing.Any in allowed or object in allowed:
        return None                    # everything is both of those
    for candidate, name in ((str, 'str'), (int, 'int'), (bytes, 'bytes')):
        if any(isinstance(a, type) and issubclass(a, candidate) for a in allowed):
            continue                   # a subclass of it is allowed
        if candidate is int and allowed & {float, complex}:
            continue                   # int is acceptable where float is
        return name
    return None


def sample(p):
    return SAMPLE.get(base_of(p.annotation), 'None')


def emit(qualname, call, sig, skipped):
    """A wrong argument for each annotated parameter, and the return value taken as the wrong type."""
    lines = []
    for pname, p in sig.parameters.items():
        if pname == 'self':
            continue
        if (qualname, pname) in OPEN:
            continue
        if p.annotation is inspect.Signature.empty:
            skipped.append('%s(%s) has no annotation' % (qualname, pname))
            continue
        wrong = contradiction(p.annotation)
        if wrong is None:
            skipped.append('%s(%s: %s) admits everything' % (qualname, pname, p.annotation))
            continue
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        args = ['%s=%s' % (n, sample(q)) for n, q in sig.parameters.items()
                if n not in ('self', pname) and q.default is inspect.Parameter.empty
                and q.kind not in (q.VAR_POSITIONAL, q.VAR_KEYWORD)]
        args.append('%s=%s' % (pname, ARG_VALUE[wrong]))
        lines.append('%s(%s)  # want: arg-type' % (call, ', '.join(args)))
    ret = sig.return_annotation
    if ret is inspect.Signature.empty or ret is None or qualname.endswith('.__init__'):
        return lines
    wrong = contradiction(ret)
    if wrong is None:
        skipped.append('%s -> %s' % (qualname, ret))
        return lines
    args = ', '.join('%s=%s' % (n, sample(p)) for n, p in sig.parameters.items()
                     if n != 'self' and p.default is inspect.Parameter.empty
                     and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD))
    lines.append('_v%d: %s = %s(%s)  # want: assignment' % (next(_numbers), wrong, call, args))
    return lines


def methods(cls):
    """The public functions defined in the class itself, with the class they are called through."""
    for name in sorted(vars(cls)):
        if name.startswith('_') and name != '__init__':
            continue
        obj = getattr(cls, name)
        if inspect.isfunction(obj):
            yield name, inspect.signature(obj)


def report_classes():
    """The report classes, each under the module a caller names it by: jma.Tsunami, dcx.JAlert, ..."""
    for module in (reports.base, reports.dcx, reports.dcr):
        for name, cls in sorted(vars(module).items()):
            if isinstance(cls, type) and cls.__module__ == module.__name__ and not typing.is_typeddict(cls):
                yield f'{module.__name__.rsplit(".", 1)[-1]}.{name}', cls


out = ['"""Generated: every public function and method used wrongly, one line each."""',
       'import datetime', '', 'import azarashi', 'from azarashi import reports',
       'from azarashi.network.receiver import Receiver', 'from azarashi.network.transmitter import Transmitter', '']
skipped: list[str] = []
body: list[str] = []

for function in (azarashi.decode, azarashi.decode_stream, azarashi.reset_reading_state, azarashi.to_json_dict, azarashi.to_ndjson, azarashi.json_schema):
    body += emit(function.__name__, 'azarashi.%s' % function.__name__, inspect.signature(function), skipped)

params = []
for name, cls in report_classes():
    var = 'r_%s' % name.replace('.', '_')
    params.append('%s: reports.%s' % (var, name))
    for attr, descriptor in vars(cls).items():
        if isinstance(descriptor, property) and descriptor.fget is not None:
            annotation = typing.get_type_hints(descriptor.fget)['return']
            wrong = contradiction(annotation)
            if wrong is not None:
                body.append('_v%d: %s = %s.%s  # want: assignment' % (next(_numbers), wrong, var, attr))
    for method, sig in methods(cls):
        if method == '__init__':
            continue                   # inherited **kwargs are covered by runtime construction tests
        body += emit('%s.%s' % (name, method), '%s.%s' % (var, method), sig, skipped)

for cls, var in ((Transmitter, 'tx'), (Receiver, 'rx')):
    params.append('%s: %s' % (var, cls.__name__))
    for method, sig in methods(cls):
        call = cls.__name__ if method == '__init__' else '%s.%s' % (var, method)
        body += emit('%s.%s' % (cls.__name__, method), call, sig, skipped)

for cls in (azarashi.AzarashiInvalidMessageError, azarashi.AzarashiNotImplementedError):
    body += emit('%s.__init__' % cls.__name__, 'azarashi.%s' % cls.__name__, inspect.signature(cls.__init__), skipped)

out += ['', 'def _uses(%s) -> None:' % ', '.join(params)]
out += ['    ' + line for line in body]
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
print('generated %d wrong uses' % len(body))
if skipped:
    print('NO MISUSE COULD BE WRITTEN FOR:')
    for s_ in skipped:
        print('  ' + s_)
    print('An annotation loose enough that nothing can contradict it constrains'
          ' nothing. Tighten it, or teach contradiction() how to contradict it.')
    sys.exit(1)
