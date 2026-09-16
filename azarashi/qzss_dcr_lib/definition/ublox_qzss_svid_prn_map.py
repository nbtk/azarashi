from .qzss_dcr_definition import QzssDcrDefinition

# the L1S PRN numbers of IS-QZSS-L1S-009, which are assigned to the satellite blocks and outlive one satellite
ublox_qzss_svid_prn_map: QzssDcrDefinition[int, int] = QzssDcrDefinition(
    {
        1: 183,
        2: 184,
        3: 185,
        4: 186,
        7: 189,
    },
    undefined=None  # no L1S PRN is assigned to the other svIds
)
