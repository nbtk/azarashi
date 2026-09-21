from ..code_table import CodeTable

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
