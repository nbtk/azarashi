"""C9, the bearing angle of second ellipse: CAMF Issue 1.2, 18.3.3, in degrees, turned from the azimuth of the main ellipse."""
from ..code_table import CodeTable

c9_bearing_angle_of_second_ellipse_value = {code: round(code * 360 / 32, 5) for code in range(32)}

c9_bearing_angle_of_second_ellipse = CodeTable(
    {code: f'{deg:g}°' for code, deg in c9_bearing_angle_of_second_ellipse_value.items()},
    undefined='Undefined bearing angle of second ellipse (Code: %d)'
)
