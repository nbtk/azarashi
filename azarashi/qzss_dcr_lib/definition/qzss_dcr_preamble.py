from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_preamble = QzssDcrDefinition(
    {
        0x53: "A",  # 01010011
        0x9A: "B",  # 10011010
        0xC6: "C",  # 11000110
    },
    undefined=None
)
