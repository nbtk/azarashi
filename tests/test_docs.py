"""The examples in the documents: what they say they print has to be what they print.

The type tables in docs/reports.md are held to the annotations by test_declared_types.py; these are
the worked examples, which drift the same way. Each document runs its own examples in order, since
a later one uses what an earlier one defined.

Three things in a documented run cannot be had again, and only those are ignored: a report is stamped
with the time it was decoded and takes the year, and for DCX the week, of its times from it; an object
without a __repr__ prints its address; and pprint wraps a long list where it likes, which is not
something the library promises.
"""
import doctest
import pathlib
import re

import pytest

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
    assert counted == {'README.md': 1, 'docs/api.md': 1, 'docs/dcr.md': 4, 'docs/dcx.md': 2}
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
