"""CAMF A12–A15 coordinates and semi-axis lengths (kilometres)."""
import math


def semi_axis(factor: int) -> float:
    return pow(10, math.log10(216.2) + factor * (math.log10(2500000) - math.log10(216.2)) / 31) / 1000


def centre_latitude(code: int) -> float:
    return -90 + 180 / 0xFFFF * code


def centre_longitude(code: int) -> float:
    return -180 + 360 / 0x1FFFF * code
