from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_satellite_prn = QzssDcrDefinition(
    {
        55: "PRN183",
        56: "PRN184",
        57: "PRN185",
        58: "PRN186",
        61: "PRN189",
    },
    undefined="Undefined PRN (Code: %d)"
)
