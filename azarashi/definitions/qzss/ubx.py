from ..code_table import CodeTable

GNSS_ID = 5  # the gnssId of QZSS in UBX
L1S_SIGNAL_ID = 1  # the sigId of the L1S signal of QZSS in UBX

# the L1S PRN numbers of IS-QZSS-L1S-009, which are assigned to the satellite blocks and outlive one satellite
svid_to_prn: CodeTable[int, int] = CodeTable(
    {
        1: 183,
        2: 184,
        3: 185,
        4: 186,
        7: 189,
    },
    undefined=None  # no L1S PRN is assigned to the other svIds
)
