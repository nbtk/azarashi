from ..code_table import CodeTable

a8_hazard_duration = CodeTable(
    {
        0: 'Unknown',
        1: 'Duration < 6H',
        2: '6H <= Duration < 12H',
        3: '12H <= Duration < 24H',
    },
    undefined='Undefined Hazard Duration (Code: %d)'
)
