from ..code_table import CodeTable

satellite_prn = CodeTable(
    {
        55: "PRN183",
        56: "PRN184",
        57: "PRN185",
        58: "PRN186",
        61: "PRN189",
    },
    undefined="Undefined PRN (Code: %d)"
)

preambles = CodeTable(
    {
        0x53: "A",  # 01010011
        0x9A: "B",  # 10011010
        0xC6: "C",  # 11000110
    },
    undefined="Undefined Preamble (Code: %d)"  # not an error: a later edition may add patterns
)

message_types = CodeTable(
    {
        43: "DCR",
        44: "DCX",
    },
    undefined=None
)
