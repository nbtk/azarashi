from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcx_camf_a5_severity = QzssDcrDefinition(
    {
        0: 'Unknown',
        1: 'Moderate - Possible threat to life or property',
        2: 'Severe - Significant threat to life or property',
        3: 'Extreme - Extraordinary threat to life or property',
    },
    undefined='Undefined Severity (Code: %d)'
)