from .qzss_dcr_definition import QzssDcrDefinition

ublox_qzss_svn_prn_map = QzssDcrDefinition(
    {
        1: 183,
        2: 184,
        3: 189,
        4: 185,
        5: 186,
    },
    undefined = 183 # has already gone silent, but it is still used as the default value
)
