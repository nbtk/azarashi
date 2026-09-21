from ..code_table import CodeTable

a17_type_of_specific_settings = CodeTable(
    {
        0: 'B1 - Improved Resolution of Main Ellipse',
        1: 'B2 - Position of the Centre of the Hazard',
        2: 'B3 - Secondary Ellipse Definition',
        3: 'B4 - Quantitative and detailed information about the Hazard',
    },
    undefined='Undefined Type of Specific Settings (Code: %d)'
)
