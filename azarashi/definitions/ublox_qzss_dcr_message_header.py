ublox_qzss_dcr_message_header: bytes = b'\xB5\x62\x02\x13'
# \xB5     -> ubx frame preamble sync char1
# \x62     -> ubx frame preamble sync char2
# \x02     -> message class: rbx
# \x13     -> message id: sfrbx
