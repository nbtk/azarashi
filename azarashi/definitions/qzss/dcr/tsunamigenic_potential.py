"""Tsunamigenic potentials of the JMA-DC Report (Northwest Pacific Tsunami), IS-QZSS-DCR-017 Table 4.1.2-27.

The English of 0 to 4 is the specification's, which writes them in capitals. 7 is その他の津波発生の可能性有無,
the code JMA sends for a potential the table has no code for; its English is azarashi's, in the words
of the table's name. The table has no Japanese but that one. JMA's specification of the bulletin
itself (配信資料に関する仕様 No.40401, 2020-03-31) gives the five sentences of 0 to 4 and no other.
"""
from ...code_table import CodeTable

tsunamigenic_potential_en = CodeTable(
    {
        0: "There is No Possibility of a Tsunami",
        1: "There is a Possibility of a Destructive Ocean-Wide Tsunami",
        2: "There is a Possibility of a Destructive Regional Tsunami",
        3: "There is a Possibility of a Destructive Local Tsunami Near the Epicenter",
        4: "There is a Very Small Possibility of a Destructive Local Tsunami",
        7: "Other Tsunamigenic Potential",
        # "N*": "Tsunamigenic Potential (Code: N)",
    },
    undefined="Undefined Tsunamigenic Potential (Code: %d)"
)
