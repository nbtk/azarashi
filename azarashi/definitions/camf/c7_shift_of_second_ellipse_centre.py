"""C7, the shift of second ellipse centre: CAMF Issue 1.2, 18.3.1, in lengths of the semi-major axis of the main ellipse, along that axis."""
from ..code_table import CodeTable

c7_shift_of_second_ellipse_centre_value = {code: code for code in range(4)}

c7_shift_of_second_ellipse_centre = CodeTable(
    {code: f'{shift:g}' for code, shift in c7_shift_of_second_ellipse_centre_value.items()},
    undefined='Undefined shift of second ellipse centre (Code: %d)'
)
