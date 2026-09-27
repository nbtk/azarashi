"""C8, the homothetic factor of second ellipse: CAMF Issue 1.2, 18.3.2, applied to both semi-axes of the main ellipse."""
from ..code_table import CodeTable

c8_homothetic_factor_of_second_ellipse_value = {code: 0.25 * (code + 1) for code in range(8)}

c8_homothetic_factor_of_second_ellipse = CodeTable(
    {code: f'{factor:g}' for code, factor in c8_homothetic_factor_of_second_ellipse_value.items()},
    undefined='Undefined homothetic factor of second ellipse (Code: %d)'
)
