from .qzss_dcr_definition import QzssDcrDefinition

ublox_qzss_svid_prn_map : QzssDcrDefinition = QzssDcrDefinition(
    {
        2: 184,
        3: 185,
        4: 186,
        7: 189,
    },
    undefined = 183 # has already gone silent, but it is still used as the default value
)
