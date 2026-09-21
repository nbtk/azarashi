"""Stage boundaries preserve report output without constructing temporary reports."""
from datetime import UTC, datetime

import pytest

import azarashi
from azarashi.decoders import base as decoder_base
from azarashi.reports import base as report_base
from qzqsm import hex_message, jma, sentence, sfrbx
from samples import EEW, L_ALERT


MESSAGES = [jma(dc, []) for dc in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14)] + [
    sentence([(8, 6, 44)]), L_ALERT,
]


@pytest.mark.parametrize('message', MESSAGES)
@pytest.mark.parametrize('fmt', ['nmea', 'hex', 'ublox', 'net'])
def test_only_the_final_report_is_constructed(message, fmt, monkeypatch):
    constructed = []
    original = report_base.Base.__init__

    def record(self, *args, **kwargs):
        constructed.append(type(self))
        original(self, *args, **kwargs)

    monkeypatch.setattr(report_base.Base, '__init__', record)
    payload = bytes.fromhex(hex_message(message) + '0')
    inputs = {'nmea': message, 'hex': hex_message(message), 'ublox': sfrbx(message),
              'net': bytes((55,)) + payload}
    stamp = datetime(2026, 9, 21, tzinfo=UTC)
    report = azarashi.decode(inputs[fmt], fmt, timestamp=stamp)
    assert constructed == [type(report)]
    assert report.timestamp == stamp
    assert 'context' not in report.get_params()


def test_reception_clock_is_read_once(monkeypatch):
    calls = []
    stamp = datetime(2026, 9, 21, tzinfo=UTC)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            calls.append(tz)
            return stamp

    monkeypatch.setattr(decoder_base, 'datetime', Clock)
    monkeypatch.setattr(report_base, 'datetime', Clock)
    assert azarashi.decode(EEW).timestamp == stamp
    assert calls == [UTC]


def test_decode_error_keeps_frame_diagnostics():
    from qzqsm import with_fields

    message = with_fields(EEW, [(214, 6, 0)])
    stamp = datetime(2026, 9, 21, tzinfo=UTC)
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as error:
        azarashi.decode(message, timestamp=stamp)
    decoder = error.value.instance
    assert decoder.sentence == message
    assert decoder.nmea == message
    assert decoder.timestamp == stamp
    assert decoder.message_type == 'DCR'
    assert decoder.version == 0
    assert decoder.raw == azarashi.reports.base.MessagePartial(
        message=decoder.message, nmea=message).raw
    assert str(error.value) == f'Unsupported JMA-DC Report Version: 0 -> {message}'
