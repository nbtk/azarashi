"""Frame decoder tests: NMEA, hex, net and u-blox framing, and the checks shared by every message."""
import random

import pytest

import azarashi
from azarashi.qzss_dcr_lib.decoder import QzssDcrDecoderBase
from azarashi.qzss_dcr_lib.report import QzssDcReportBase
from qzqsm import hex_message
from qzqsm import nmea_checksum
from qzqsm import sentence
from qzqsm import sfrbx
from qzqsm import ubx
from qzqsm import with_fields

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
EEW_HEX = hex_message(EEW)


def _nmea(body):
    """A sentence with a valid checksum around any body, so that the checks after the checksum are reached."""
    return f'${body}*{nmea_checksum(body)}'


def _error(msg, msg_type='nmea'):
    with pytest.raises(azarashi.QzssDcrDecoderException) as excinfo:
        azarashi.decode(msg, msg_type)
    return excinfo.value.message


# NMEA

@pytest.mark.parametrize('msg, message', [
    (' \r\n', 'Too Short Sentence'),  # a blank line
    (EEW[:-1], 'Too Short Sentence'),
    (EEW + '0', 'Too Long Sentence'),
    (EEW.replace('*', ','), 'Checksum Not Found'),
    (EEW[:-4] + '**05', 'Checksum Not Found'),
    (EEW[:-4] + '*005', 'Invalid Checksum Length'),
    (EEW[:-2] + 'ZZ', 'Invalid Checksum'),
    (EEW[:-2] + '00', 'Checksum Mismatch, should be 05'),
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


# hex

@pytest.mark.parametrize('msg, message', [
    (' \n', 'Too Short Sentence'),
    (EEW_HEX[:-1], 'Too Short Sentence'),
    (EEW_HEX + '0', 'Too Long Sentence'),
    (EEW_HEX[:-1] + 'G', 'Invalid Message'),
    (EEW_HEX[:30] + '  ' + EEW_HEX[32:], 'Invalid Message'),  # bytes.fromhex() would skip the spaces
])
def test_hex_rejects(msg, message):
    assert _error(msg, 'hex') == message


def test_hex_has_no_satellite():
    report = azarashi.decode(EEW_HEX + '\n', 'hex')
    assert (report.satellite_id, report.satellite_prn) == (None, None)
    assert report.nmea == EEW  # written as from PRN183
    assert report == azarashi.decode(EEW)


# net

@pytest.mark.parametrize('msg, message', [
    (bytes((55,)) + bytes(31), 'Too Short Sentence'),
    (bytes((55,)) + bytes(33), 'Too Long Sentence'),
])
def test_net_rejects(msg, message):
    assert _error(msg, 'net') == message


def test_net_carries_the_satellite():
    report = azarashi.decode(bytes((58,)) + azarashi.decode(EEW).message, 'net')
    assert (report.satellite_id, report.satellite_prn) == (58, 186)
    assert report.nmea == with_fields(EEW.replace(',55,', ',58,'), [])  # with the checksum recomputed


# u-blox

def _sfrbx_payload(frame):
    return frame[6:-2]


@pytest.mark.parametrize('frame, message', [
    (b'\xB5\x62\x02\x14' + sfrbx(EEW)[4:], "Unknown Message Header: b'\\xb5b\\x02\\x14'"),
    (ubx(b'\x02\x13', bytes((5, 0, 1, 0, 8, 0))), 'Too Short Sentence'),
    (sfrbx(EEW)[:-1] + b'\x00', 'Checksum Mismatch: expected '),
    (sfrbx(EEW, gnss=0), 'This Sentence is not from QZSS: 0'),
    (sfrbx(EEW, sig=0), 'The Sentence is not an L1S Signal: 0'),
    (sfrbx(EEW, num_words=9), 'Invalid Message Length: 9'),
    (ubx(b'\x02\x13', _sfrbx_payload(sfrbx(EEW, num_words=7))[:-4]), 'Invalid Message Length: 7'),
])
def test_ublox_rejects(frame, message):
    assert _error(frame, 'ublox').startswith(message)


def test_ublox_checksum_mismatch_names_both_checksums():
    frame = sfrbx(EEW)
    broken = frame[:-2] + bytes((frame[-2] ^ 1, frame[-1]))
    assert _error(broken, 'ublox') == f'Checksum Mismatch: expected {frame[-2]:02X}{frame[-1]:02X}, ' \
                                      f'but got {broken[-2]:02X}{broken[-1]:02X}'


@pytest.mark.parametrize('sv, satellite_prn', [(2, 184), (3, 185), (4, 186), (7, 189), (1, 183), (0, 183)])
def test_ublox_satellite(sv, satellite_prn):
    report = azarashi.decode(sfrbx(EEW, sv=sv), 'ublox')
    assert (report.satellite_prn, report.satellite_id) == (satellite_prn, satellite_prn & 0x3f)


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
     'CRC Mismatch'),
    (sentence([(0, 8, 0x53), (8, 6, 42)]), 'Undefined Message Type: 42'),
    (sentence([(0, 8, 0x53), (8, 6, 0)]), 'Undefined Message Type: 0'),
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
    class Decoder(QzssDcrDecoderBase):
        schema = QzssDcReportBase

    with pytest.raises(azarashi.QzssDcrDecoderNotImplementedError) as excinfo:
        Decoder(EEW).decode()
    assert str(excinfo.value) == 'Decoder Not Implemented'


def test_extract_field_matches_the_bit_string():
    rng = random.Random(250)

    class Decoder(QzssDcrDecoderBase):
        schema = QzssDcReportBase

    for _ in range(20):
        bits = rng.getrandbits(250)
        decoder = Decoder('')
        decoder.message = (bits << 6).to_bytes(32, 'big')
        for pos in range(250):
            for size in range(1, min(64, 250 - pos) + 1):
                assert decoder.extract_field(pos, size) == bits >> (250 - pos - size) & (1 << size) - 1, (pos, size)
