ublox_qzss_dcr_message_header = b'\xB5\x62\x02\x13\x2C\x00\x05'
# \xB5     -> ubx frame preamble sync char1
# \x62     -> ubx frame preamble sync char2
# \x02     -> message class: rbx
# \x13     -> message id: sfrbx
# \x2c\x00 -> payload length: 44 (little-endian 16-bit integer)
# \x05     -> gnss id: qzss
