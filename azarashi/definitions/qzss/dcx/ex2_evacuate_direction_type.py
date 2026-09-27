"""EX2, which way to go from the additional ellipse, IS-QZSS-DCX-004 Table 4.2-22. EX2 is one bit."""
from ...code_table import CodeTable

ex2_evacuate_direction_type = CodeTable(
    {
        0: "Leave the additional target area range.",
        1: "Head to the additional target area range.",
    },
    undefined="Undefined Evacuate Direction Type (Code: %d)"
)
