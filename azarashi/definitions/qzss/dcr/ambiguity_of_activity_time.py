"""Du, the ambiguity of the activity time of a volcano report, in the words of IS-QZSS-DCR-017.

Every 3-bit value is defined. The Japanese text shows the ambiguity through the time it writes, so
there is no Japanese table.
"""
from ...code_table import CodeTable

ambiguity_of_activity_time_en = CodeTable(
    {
        0: "No ambiguity",
        1: "Approximate time (equivalent to Approximate time (minute))",
        2: "Approximate time (second)",
        3: "Approximate time (minute)",
        4: "Approximate time (hour)",
        5: "Approximate time (day)",
        6: "Approximate time (month)",
        7: "Approximate time (year)",
    },
    undefined="Undefined Ambiguity of Activity Time (Code: %d)"
)
