"""Frame decoder tests: NMEA, hex, net and u-blox framing, and the checks shared by every message."""
import random
from datetime import UTC, datetime

import pytest

import azarashi
from azarashi.decoders.qzss import base
from azarashi.decoders.qzss.context import Frame
from qzqsm import nmea_checksum
from qzqsm import sentence
from qzqsm import sfrbx
from qzqsm import ubx
from qzqsm import with_fields
from samples import EEW
from samples import EEW_HEX


def _nmea(body):
    """A sentence with a valid checksum around any body, so that the checks after the checksum are reached."""
    return f'${body}*{nmea_checksum(body)}'


def _error(msg, msg_format='nmea'):
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(msg, msg_format)
    return excinfo.value.message


# NMEA

@pytest.mark.parametrize('msg, message', [
    (' \r\n', 'Too Short Sentence: expected 76 characters, but got 0'),  # a blank line
    (EEW[:-1], 'Too Short Sentence: expected 76 characters, but got 75'),
    (EEW + '0', 'Too Long Sentence: expected 76 characters, but got 77'),
    (EEW.replace('*', ','), 'Checksum Not Found'),
    (EEW[:-4] + '**05', 'Checksum Not Found'),
    (EEW[:-4] + '*005', 'Invalid Checksum Length: expected 2 characters, but got 3'),
    (EEW[:-2] + 'ZZ', 'Invalid Checksum'),
    (EEW[:-2] + '00', 'Checksum Mismatch: expected 05, but got 00'),
    (_nmea('QZQSM;55,' + EEW_HEX), 'Invalid Sentence'),
    (_nmea('GPQSM,55,' + EEW_HEX), 'Unknown Message Header: $GPQSM'),
    (_nmea('QZQSM,5,0' + EEW_HEX), 'Invalid Satellite ID: 5'),
    (_nmea('QZQSM,AB,' + EEW_HEX), 'Invalid Satellite ID: AB'),
    (_nmea('QZQSM,-5,' + EEW_HEX), 'Invalid Satellite ID: -5'),
    (_nmea('QZQSM,55,' + EEW_HEX[:-1] + 'G'), 'Invalid Message'),
])
def test_nmea_rejects(msg, message):
    assert _error(msg) == message


def test_nmea_ignores_what_follows_the_sentence():
    assert azarashi.decode(EEW + ' 12:34:56\r\n') == azarashi.decode(EEW)


@pytest.mark.parametrize('satellite_id', [55, 56, 57, 58, 61])
def test_nmea_satellite(satellite_id):
    report = azarashi.decode(with_fields(EEW.replace(',55,', f',{satellite_id},'), []))
    assert (report.satellite_id, report.satellite_prn) == (satellite_id, satellite_id | 0x80)
    assert report.nmea.startswith(f'$QZQSM,{satellite_id},')


def test_spresense_is_nmea():
    assert azarashi.decode(EEW, 'spresense') == azarashi.decode(EEW, 'nmea')


@pytest.mark.parametrize('msg, msg_format', [(EEW.encode() + b'\r\n', 'nmea'), (EEW_HEX.encode() + b'\n', 'hex')])
def test_text_formats_take_a_line_of_bytes(msg, msg_format):  # as pySerial's readline() gives it
    report = azarashi.decode(msg, msg_format)
    assert report == azarashi.decode(EEW)
    assert isinstance(report.sentence, str)


@pytest.mark.parametrize('msg, msg_format, message', [
    (b'\xff' * 76, 'nmea', 'Checksum Not Found'),
    (b'\xff' * 63, 'hex', 'Invalid Message'),
    ('7' + '0' * 32, 'net', 'Invalid Sentence'),  # a datagram is bytes
])
def test_wrong_kind_of_input_is_a_decoder_error(msg, msg_format, message):
    assert _error(msg, msg_format) == message


# hex

@pytest.mark.parametrize('msg, message', [
    (' \n', 'Too Short Sentence: expected 63 characters, but got 0'),
    (EEW_HEX[:-1], 'Too Short Sentence: expected 63 characters, but got 62'),
    (EEW_HEX + '0', 'Too Long Sentence: expected 63 characters, but got 64'),
    (EEW_HEX[:-1] + 'G', 'Invalid Message'),
    (EEW_HEX[:30] + '  ' + EEW_HEX[32:], 'Invalid Message'),  # bytes.fromhex() would skip the spaces
])
def test_hex_rejects(msg, message):
    assert _error(msg, 'hex') == message


def test_hex_has_no_satellite():
    report = azarashi.decode(EEW_HEX + '\n', 'hex')
    assert (report.satellite_id, report.satellite_prn, report.satellite_svid) == (None, None, None)
    assert report.nmea == EEW  # written as from PRN183
    assert report == azarashi.decode(EEW)


# net

@pytest.mark.parametrize('msg, message', [
    (bytes((55,)) + bytes(31), 'Too Short Sentence: expected 33 bytes, but got 32'),
    (bytes((55,)) + bytes(33), 'Too Long Sentence: expected 33 bytes, but got 34'),
])
def test_net_rejects(msg, message):
    assert _error(msg, 'net') == message


def test_net_carries_the_satellite():
    report = azarashi.decode(bytes((58,)) + azarashi.decode(EEW).message, 'net')
    assert (report.satellite_id, report.satellite_prn, report.satellite_svid) == (58, 186, None)
    assert report.nmea == with_fields(EEW.replace(',55,', ',58,'), [])  # with the checksum recomputed


# u-blox

def _sfrbx_payload(frame):
    return frame[6:-2]


@pytest.mark.parametrize('frame, message', [
    (b'\xB5\x62\x02\x14' + sfrbx(EEW)[4:], "Unknown Message Header: b'\\xb5b\\x02\\x14'"),
    (ubx(b'\x02\x13', bytes((5, 0, 1, 0, 8, 0))), 'Too Short Sentence: expected at least 16 bytes, but got 14'),
    (sfrbx(EEW)[:-1] + b'\x00', 'Checksum Mismatch: expected '),
    (sfrbx(EEW, gnss=0), 'This Sentence is not from QZSS: expected GNSS ID 5, but got 0'),
    (sfrbx(EEW, sig=0), 'The Sentence is not an L1S Signal: expected Signal ID 1, but got 0'),
    (sfrbx(EEW, num_words=9), 'Invalid Message Length: expected 44 bytes for 9 data words, but got 40'),
    (ubx(b'\x02\x13', _sfrbx_payload(sfrbx(EEW, num_words=7))[:-4]),
     'Invalid Message Length: expected at least 8 data words, but got 7'),
])
def test_ublox_rejects(frame, message):
    assert _error(frame, 'ublox').startswith(message)


def test_ublox_checksum_mismatch_names_both_checksums():
    frame = sfrbx(EEW)
    broken = frame[:-2] + bytes((frame[-2] ^ 1, frame[-1]))
    assert _error(broken, 'ublox') == f'Checksum Mismatch: expected {frame[-2]:02X}{frame[-1]:02X}, ' \
                                      f'but got {broken[-2]:02X}{broken[-1]:02X}'


@pytest.mark.parametrize('declared_length', [8, 39, 44, 296])
def test_ublox_rejects_inconsistent_declared_length(declared_length):
    frame = bytearray(sfrbx(EEW))
    frame[4:6] = declared_length.to_bytes(2, 'little')
    # Keep the checksum valid so that only the inconsistent length makes this invalid.
    ck_a = ck_b = 0
    for value in frame[2:-2]:
        ck_a = (ck_a + value) & 0xff
        ck_b = (ck_b + ck_a) & 0xff
    frame[-2:] = bytes((ck_a, ck_b))
    assert _error(bytes(frame), 'ublox') == \
        f'Payload Length Mismatch: declared {declared_length} bytes, but got 40'


@pytest.mark.parametrize('sv, satellite_prn', [
    (1, 183), (2, 184), (3, 185), (4, 186), (7, 189),  # the PRN numbers of IS-QZSS-L1S-009
    (0, None), (5, None), (6, None), (8, None), (255, None),  # no PRN is assigned to these svIds
])
def test_ublox_satellite(sv, satellite_prn):
    report = azarashi.decode(sfrbx(EEW, sv=sv), 'ublox')
    satellite_id = None if satellite_prn is None else satellite_prn & 0x3f
    assert (report.satellite_prn, report.satellite_id) == (satellite_prn, satellite_id)
    assert report.satellite_svid == sv  # what the receiver said, whether or not it has a PRN number
    assert report.nmea.startswith(f'$QZQSM,{satellite_id or 55},')  # 55 stands in for an unknown satellite


def test_ublox_ignores_extra_data_words():
    frame = ubx(b'\x02\x13', _sfrbx_payload(sfrbx(EEW, num_words=9)) + bytes(4))
    assert azarashi.decode(frame, 'ublox') == azarashi.decode(EEW)


def test_ublox_clears_the_bits_after_the_message():
    frame = bytearray(sfrbx(EEW))
    frame[14 + 28] |= 0x3f  # the least significant byte of the last word: 2 message bits and 6 padding bits
    report = azarashi.decode(ubx(b'\x02\x13', _sfrbx_payload(bytes(frame))), 'ublox')
    assert report.message == azarashi.decode(EEW).message


# the checks after the framing

@pytest.mark.parametrize('msg, message', [
    (EEW[:-4] + ('0' if EEW[-4] != '0' else '1') + '*' + nmea_checksum(EEW[1:-4] + ('0' if EEW[-4] != '0' else '1')),
     'CRC Mismatch: expected 1510FF, but got 1510FC'),
    (sentence([(0, 8, 0x53), (8, 6, 42)]), 'The Message is not DCR or DCX: expected Message Type 43 or 44, but got 42'),
    (sentence([(0, 8, 0x53), (8, 6, 0)]), 'The Message is not DCR or DCX: expected Message Type 43 or 44, but got 0'),
])
def test_message_rejects(msg, message):
    assert _error(msg) == message


@pytest.mark.parametrize('preamble, name', [
    (0x53, 'A'), (0x9A, 'B'), (0xC6, 'C'),
    (0x00, 'Undefined Preamble (Code: 0)'),  # not an error, since a later edition may add patterns; the CRC still applies
])
def test_preamble(preamble, name):
    assert azarashi.decode(with_fields(EEW, [(0, 8, preamble)])).preamble == name


def test_decoder_base_is_abstract():
    context = Frame(sentence=EEW, message=b'', timestamp=datetime.now(UTC))
    with pytest.raises(azarashi.AzarashiNotImplementedError) as excinfo:
        base.ContextDecoder(context).decode()
    assert str(excinfo.value) == 'Decoder Not Implemented'


def test_extract_field_matches_the_bit_string():
    rng = random.Random(250)

    for _ in range(20):
        bits = rng.getrandbits(250)
        decoder = base.ContextDecoder(Frame(
            sentence='', message=(bits << 6).to_bytes(32, 'big'), timestamp=datetime.now(UTC)))
        for pos in range(250):
            for size in range(1, min(64, 250 - pos) + 1):
                assert decoder.extract_field(pos, size) == bits >> (250 - pos - size) & (1 << size) - 1, (pos, size)


# The specifications are revised, and a revision adds codes. These guards catch a table that
# gained a code the decoders were not taught, which is the shape such an update takes here. They
# cannot fire while the tables and the decoders agree, so the tables are moved to make them.

def test_a_message_type_the_table_knows_but_no_decoder_takes(monkeypatch):
    from azarashi.definitions.qzss.l1s import message_types
    monkeypatch.setitem(message_types, 45, 'DCZ')  # a message type of some later edition
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(with_fields(EEW, [(8, 6, 45)]))
    assert excinfo.value.message == 'Unsupported Message Type: 45'


def test_a_disaster_category_the_table_knows_but_no_decoder_takes(monkeypatch):
    from azarashi.definitions.qzss.dcr.disaster_category import disaster_category
    from azarashi.definitions.qzss.dcr.disaster_category import disaster_category_en
    monkeypatch.setitem(disaster_category, 7, '高潮')  # category 7 is not assigned yet
    monkeypatch.setitem(disaster_category_en, 7, 'Storm Surge')
    with pytest.raises(azarashi.AzarashiInvalidMessageError) as excinfo:
        azarashi.decode(with_fields(EEW, [(17, 4, 7)]))
    assert excinfo.value.message == 'Unsupported Disaster Category: 高潮'
