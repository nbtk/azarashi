from ..code_table import CodeTable

a5_severity = CodeTable(
    {
        0: 'Unknown',
        1: 'Moderate - Possible threat to life or property',
        2: 'Severe - Significant threat to life or property',
        3: 'Extreme - Extraordinary threat to life or property',
    },
    undefined='Undefined Severity (Code: %d)'
)
