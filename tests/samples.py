"""Messages received from QZSS, shared by the tests."""
from qzqsm import hex_message
from qzqsm import sfrbx

# Earthquake Early Warning (training/test message)
EEW = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
EEW_HEX = hex_message(EEW)
FRAME = sfrbx(EEW)  # the same message as a UBX-RXM-SFRBX frame
# DCX message (L-Alert)
L_ALERT = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E'
