from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....reports.base import Coordinates

latitude_degrees = range(0, 90)
longitude_degrees = range(0, 180)
latitude_and_longitude_minutes = range(0, 60)
latitude_and_longitude_seconds = range(0, 60)

# names the whole LatLon field (41 bits) as one number when a part of it is outside its range
latitude_and_longitude_undefined = "緯度・経度(コード番号：%d)"
latitude_and_longitude_undefined_en = "Undefined Latitude and Longitude (Code: %d)"


def is_position(coordinates: 'Coordinates') -> bool:
    """Whether every part is inside its range: with one outside, the others cannot be trusted either."""
    return (coordinates['lat_d'] in latitude_degrees
            and coordinates['lat_m'] in latitude_and_longitude_minutes
            and coordinates['lat_s'] in latitude_and_longitude_seconds
            and coordinates['lon_d'] in longitude_degrees
            and coordinates['lon_m'] in latitude_and_longitude_minutes
            and coordinates['lon_s'] in latitude_and_longitude_seconds)


def latitude_and_longitude_code(coordinates: 'Coordinates') -> int:
    """The LatLon field as one number, as it was sent."""
    code = 0
    for bits, value in ((1, coordinates['lat_ns']), (7, coordinates['lat_d']), (6, coordinates['lat_m']),
                        (6, coordinates['lat_s']), (1, coordinates['lon_ew']), (8, coordinates['lon_d']),
                        (6, coordinates['lon_m']), (6, coordinates['lon_s'])):  # in the order they are sent
        code = code << bits | value
    return code
