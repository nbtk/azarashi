RXM_SFRBX_HEADER: bytes = b'\xB5\x62\x02\x13'
# \xB5     -> ubx frame preamble sync char1
# \x62     -> ubx frame preamble sync char2
# \x02     -> message class: rxm
# \x13     -> message id: sfrbx
