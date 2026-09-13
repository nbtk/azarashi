"""Build QZQSM sentences field by field for tests, with a valid CRC-24Q and checksum.

Positions and sizes are in bits from the start of the 250-bit message, as in
IS-QZSS-DCR and IS-QZSS-DCX.
"""
import struct

Field = tuple[int, int, int]  # (position, size, value)


def set_fields(bits: int, fields: list[Field] | tuple[Field, ...]) -> int:
    for pos, size, value in fields:
        assert 0 <= value < 1 << size, (pos, size, value)
        shift = 250 - pos - size
        bits = bits & ~(((1 << size) - 1) << shift) | value << shift
    return bits


def with_crc(bits: int) -> int:
    crc = 0
    for i in range(226):  # CRC-24Q over everything but the CRC field
        crc ^= (bits >> (249 - i) & 1) << 23
        crc = (crc << 1) ^ 0x1864cfb if crc & 0x800000 else crc << 1
    return bits & ~0xffffff | crc & 0xffffff


def nmea_checksum(body: str) -> str:
    checksum = 0
    for c in body:
        checksum ^= ord(c)
    return f'{checksum:02X}'


def sentence(fields: list[Field] | tuple[Field, ...], satellite_id: int = 55) -> str:
    bits = with_crc(set_fields(0, fields))
    body = f'QZQSM,{satellite_id:02d},{bits << 2:063X}'
    return f'${body}*{nmea_checksum(body)}'


def with_fields(nmea: str, fields: list[Field] | tuple[Field, ...]) -> str:
    satellite_id = int(nmea.split(',')[1])
    bits = int(nmea.split(',')[2].split('*')[0], 16) >> 2
    bits = with_crc(set_fields(bits, fields))
    body = f'QZQSM,{satellite_id:02d},{bits << 2:063X}'
    return f'${body}*{nmea_checksum(body)}'


def jma(category: int, fields: list[Field] | tuple[Field, ...] = (), *, classification: int = 7,
        month: int = 3, day: int = 7, hour: int = 5, minute: int = 10, information_type: int = 0,
        preamble: int = 0x53, version: int = 1) -> str:
    """A JMA-DC Report (MT43) with the common header filled in."""
    return sentence([(0, 8, preamble), (8, 6, 43), (14, 3, classification), (17, 4, category),
                     (21, 4, month), (25, 5, day), (30, 5, hour), (35, 6, minute),
                     (41, 2, information_type), (214, 6, version), *fields])


def hex_message(nmea: str) -> str:
    return nmea.split(',')[2].split('*')[0]


def ubx(msg_class_id: bytes, payload: bytes) -> bytes:
    body = msg_class_id + struct.pack('<H', len(payload)) + payload
    ck_a = ck_b = 0
    for b in body:
        ck_a = (ck_a + b) & 0xff
        ck_b = (ck_b + ck_a) & 0xff
    return b'\xB5\x62' + body + bytes((ck_a, ck_b))


def sfrbx(nmea: str, *, gnss: int = 5, sv: int = 0, sig: int = 1, num_words: int = 8) -> bytes:
    """A UBX-RXM-SFRBX frame carrying the message of a QZQSM sentence."""
    message = bytes.fromhex(hex_message(nmea) + '0')  # 250 bits padded to 32 bytes
    words = b''.join(message[i:i + 4][::-1] for i in range(0, 32, 4))  # data words are little-endian
    return ubx(b'\x02\x13', bytes((gnss, sv, sig, 0, num_words, 0, 2, 0)) + words)
