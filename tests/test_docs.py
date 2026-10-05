"""The examples in the documents: what they say they print has to be what they print.

The type tables in docs/reports.md are held to the annotations by test_declared_types.py; these are
the worked examples, which drift the same way. Each document runs its own examples in order, since
a later one uses what an earlier one defined. An example without output runs with what it takes
as given, and the help of a command is held to what the command prints.

Three things in a documented run cannot be had again, and only those are ignored: a report is stamped
with the time it was decoded and takes the year, and for DCX the week, of its times from it; an object
without a __repr__ prints its address; and pprint wraps a long list where it likes, which is not
something the library promises.
"""
import doctest
import gzip
import inspect
import io
import pathlib
import re
import sys
import types

import pytest

import azarashi
from samples import EEW

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCUMENTS = ['README.md', 'docs/api.md', 'docs/dcr.md', 'docs/dcx.md']
UNREPEATABLE = [(re.compile(r'datetime\.datetime\([^)]*\)'), 'a decoded time'),  # and the times taken from it
                (re.compile(r'object at 0x[0-9a-f]+'), 'an object address'),
                (re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'), 'a decoded time')]  # written out by a report
#: examples that open a device, which a test has nothing to open
NEEDS_A_DEVICE = 'serial.Serial'


class _IgnoringWhatCannotBeRepeated(doctest.OutputChecker):
    def check_output(self, want: str, got: str, optionflags: int) -> bool:
        for pattern, instead in UNREPEATABLE:
            want, got = pattern.sub(instead, want), pattern.sub(instead, got)
        return super().check_output(want, got, optionflags)


def _blocks(document):
    return re.findall(r'```(\w*)\n(.*?)```', (ROOT / document).read_text(encoding='utf-8'), re.S)


def _examples(document):
    """Every >>> block, with the fenced block that follows it when that holds the output."""
    blocks = _blocks(document)
    for i, (language, body) in enumerate(blocks):
        if language != 'python' or '>>>' not in body or NEEDS_A_DEVICE in body:
            continue
        if all(line.startswith(('>>>', '...')) or not line.strip() for line in body.splitlines()):
            output = blocks[i + 1][1] if i + 1 < len(blocks) else ''
            output = '\n'.join(line or '<BLANKLINE>' for line in output.splitlines())  # doctest stops at a blank line
            body = body.rstrip('\n') + '\n' + output + '\n'
        yield i, body


@pytest.mark.parametrize('document', DOCUMENTS)
def test_the_examples_print_what_they_say(document):
    parser = doctest.DocTestParser()
    globs: dict[str, object] = {}
    failures: list[str] = []
    for number, body in _examples(document):
        # pprint decides for itself where to wrap a long list, so only there is the layout not checked
        flags = doctest.NORMALIZE_WHITESPACE if 'pprint(' in body else 0
        runner = doctest.DocTestRunner(checker=_IgnoringWhatCannotBeRepeated(), optionflags=flags)
        test = parser.get_doctest(body, globs, f'{document} block {number}', document, 0)
        assert test.examples, f'{document} block {number} has nothing to run'
        runner.run(test, out=failures.append, clear_globs=False)
        globs = test.globs
    assert failures == []


def test_every_example_is_covered_or_known_not_to_be():
    counted = {document: len(list(_examples(document))) for document in DOCUMENTS}
    assert counted == {'README.md': 1, 'docs/api.md': 1, 'docs/dcr.md': 3, 'docs/dcx.md': 3}
    skipped = [(document, i) for document in DOCUMENTS
               for i, (language, body) in enumerate(_blocks(document))
               if language == 'python' and '>>>' in body and NEEDS_A_DEVICE in body]
    assert skipped == [('docs/api.md', 4)]  # the pySerial example, which needs a device to open


def test_a_changed_example_is_noticed(tmp_path, monkeypatch):
    document = tmp_path / 'drifted.md'
    document.write_text('```python\n>>> 1 + 1\n3\n```\n', encoding='utf-8')
    monkeypatch.setattr('test_docs.ROOT', tmp_path)
    monkeypatch.setattr('test_docs.DOCUMENTS', ['drifted.md'])
    with pytest.raises(AssertionError):
        test_the_examples_print_what_they_say('drifted.md')


EVERY_DOCUMENT = ['README.md', *sorted(str(path.relative_to(ROOT)) for path in (ROOT / 'docs').glob('*.md'))]
#: the blocks that show how a function is called; test_the_signatures_shown_are_the_functions_own holds them
SIGNATURES = {('docs/api.md', 'azarashi.decode(msg,'): azarashi.decode,
              ('docs/api.md', 'azarashi.decode_stream(stream,'): azarashi.decode_stream,
              ('docs/api.md', 'azarashi.reset_reading_state(stream,'): azarashi.reset_reading_state}
#: how decode_stream() calls the callback, which is a description rather than something to run
CALLBACK = ('docs/api.md', 'callback(report, *callback_args, **callback_kwargs)')
#: the examples without output, each run by a test below
RUN = [('docs/api.md', 'def handler(report: azarashi.Report)'),
       ('docs/api.md', "open('qzss.ubx', mode='rb')"),
       ('docs/api.md', "serial.serial_for_url('socket://"),
       ('docs/reports.md', 'report.get_texts()'),
       ('docs/json.md', 'report.to_json_dict()'),
       ('docs/dcr.md', 'for forecast in report.forecasts:'),
       ('docs/development.md', 'from qzqsm import jma, sfrbx')]


def _block(document, marker):
    """The one Python block of a document that holds marker."""
    found = [body for language, body in _blocks(document) if language == 'python' and marker in body]
    assert len(found) == 1, f'{document}: {len(found)} Python blocks hold {marker!r}'
    return found[0]


def _run(document, marker, given=None):
    """Run an example with the names it takes as given, and return the names it defined."""
    names = {'__name__': '__example__', **(given or {})}
    exec(compile(_block(document, marker), f'{document}: {marker}', 'exec'), names)
    return names


def test_every_python_example_is_run_or_known_not_to_be():
    # a new example is noticed here until a test runs it
    accounted = set()
    for document in EVERY_DOCUMENT:
        blocks = _blocks(document)
        for i, (language, body) in enumerate(blocks):
            if language == 'python' and '>>>' in body:
                accounted |= {(document, i), (document, i + 1)}  # a doctest, and the output that follows it
            elif language == 'python' and 'serial.Serial' in body and 'while ' in body:
                accounted.add((document, i))  # run by test_disconnect.py against a device that is pulled out
    for document, marker in [*SIGNATURES, CALLBACK, *RUN]:
        body = _block(document, marker)
        accounted.add((document, [b for _, b in _blocks(document)].index(body)))
    missing = [f'{document} block {i}: {body.splitlines()[0]}' for document in EVERY_DOCUMENT
               for i, (language, body) in enumerate(_blocks(document))
               if language == 'python' and (document, i) not in accounted]
    assert missing == []


def _shown(function):
    """A signature the way the documents show it: the names and defaults, without the annotations."""
    parameters = [name if p.default is inspect.Parameter.empty else f'{name}={p.default!r}'
                  for name, p in inspect.signature(function).parameters.items()]
    return f'azarashi.{function.__name__}({", ".join(parameters)})'


@pytest.mark.parametrize('document,marker', list(SIGNATURES))
def test_the_signatures_shown_are_the_functions_own(document, marker):
    assert _block(document, marker).strip() == _shown(SIGNATURES[document, marker])


def _reports():
    from test_declared_types import REPORTS
    return REPORTS


def test_the_type_hints_example_handles_every_report(capsys):
    handler = _run('docs/api.md', 'def handler(report: azarashi.Report)')['handler']
    for report in _reports():
        handler(report)
    assert capsys.readouterr().out  # it printed arrival and onset times, so its branches were taken


def test_the_io_stream_example_reads_a_recording_to_the_end(tmp_path, monkeypatch, capsys):
    frames = gzip.decompress((ROOT / 'tests/ublox_260924.ubx.gz').read_bytes())[:200_000]
    (tmp_path / 'qzss.ubx').write_bytes(frames)
    monkeypatch.chdir(tmp_path)
    exits = []
    _run('docs/api.md', "open('qzss.ubx', mode='rb')", {'exit': exits.append})
    assert exits == [0]
    assert '防災気象情報' in capsys.readouterr().out


class _Socket(io.BytesIO):
    """What serial_for_url('socket://...', timeout=1) gives: bytes, until the read times out."""
    timeout = 1


def test_the_socket_example_reads_until_the_read_times_out(capsys):
    opened = []
    fake = types.ModuleType('serial')
    fake.serial_for_url = lambda url, timeout: opened.append((url, timeout)) or _Socket(sfrbx(EEW))
    with pytest.raises(azarashi.AzarashiTimeoutError):
        _run('docs/api.md', "serial.serial_for_url('socket://", {'azarashi': azarashi, 'serial': fake})
    assert opened == [('socket://192.168.1.10:2000', 1)]
    assert '緊急地震速報' in capsys.readouterr().out


def test_the_text_example_calls_what_reports_have():
    _run('docs/reports.md', 'report.get_texts()', {'report': azarashi.decode(EEW)})


def test_the_json_example_gives_a_record_the_schema_and_the_tables(capsys):
    names = _run('docs/json.md', 'report.to_json_dict()', {'sentence': EEW})
    assert names['record']['type'] == 'qzss.dcr.earthquake_early_warning'
    assert capsys.readouterr().out == names['report'].to_ndjson()
    assert names['schema']['$id'] == 'urn:azarashi:report:2' and names['tables']['tables']


def test_the_forecast_example_prints_a_line_a_region(capsys):
    report = next(r for r in _reports() if isinstance(r, azarashi.reports.dcr.Tsunami) and r.forecasts)
    _run('docs/dcr.md', 'for forecast in report.forecasts:', {'azarashi': azarashi, 'report': report})
    assert len(capsys.readouterr().out.splitlines()) == len(report.forecasts)


def test_the_message_builder_example_builds_what_its_comment_says():
    names = _run('docs/development.md', 'from qzqsm import jma, sfrbx')
    report = azarashi.decode(names['sentence'])
    assert isinstance(report, azarashi.reports.dcr.Flood)
    assert '鬼怒川' in str(report) and '氾濫警戒情報' in str(report)
    assert azarashi.decode(names['frame'], 'ublox') == report


def sfrbx(sentence):
    from qzqsm import sfrbx as frame
    return frame(sentence)


#: the commands whose help a document shows, by the name the document shows them under
COMMANDS = {'docs/cli.md': ('azarashi', 'azarashi.__main__'),
            'docs/network.md': ('transmitter.py', 'azarashi.network.transmitter'),
            'docs/network.md#2': ('receiver.py', 'azarashi.network.receiver')}


def _help_shown(document, prog):
    found = [body for _, body in _blocks(document) if body.startswith(f'usage: {prog} ')]
    assert len(found) == 1, f'{document} shows the help of {prog} {len(found)} times'
    return found[0]


def _layout_free(text):
    """Help without what the Python version decides: the wrapping, and whether a short option repeats its metavar."""
    text = re.sub(r'(-\w) (\S+), (--[\w-]+) \2(?=\s)', r'\1, \3 \2', text)  # the layout before Python 3.13
    return ' '.join(text.split())


@pytest.mark.parametrize('where', list(COMMANDS))
def test_the_help_shown_is_what_the_command_prints(where, monkeypatch, capsys):
    prog, module = COMMANDS[where]
    monkeypatch.setattr(sys, 'argv', [prog, '--help'])
    monkeypatch.setenv('NO_COLOR', '1')
    with pytest.raises(SystemExit):
        __import__(module, fromlist=['main']).main()
    printed = capsys.readouterr().out
    assert _layout_free(_help_shown(where.split('#')[0], prog)) == _layout_free(printed)
