from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcx_camf_a8_hazard_duration = QzssDcrDefinition(
    {
        0: 'Unknown',
        1: 'Duration < 6H',
        2: '6H <= Duration < 12H',
        3: '12H <= Duration < 24H',
    },
    undefined='Undefined Hazard Duration (Code: %d)'
)
