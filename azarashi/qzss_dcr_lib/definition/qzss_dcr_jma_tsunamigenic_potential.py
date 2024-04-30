from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_tsunamigenic_potential_en = QzssDcrDefinition(
    {
        0: "There is No Possibility of a Tsunami",
        1: "There is a Possibility of a Destructive Ocean-Wide Tsunami",
        2: "There is a Possibility of a Destructive Regional Tsunami",
        3: "There is a Possibility of a Destructive Local Tsunami Near the Epicenter",
        4: "There is a Very Small Possibility of a destructive Local Tsunami",
        7: "There is Possibility of a Tsunami",  # "その他の津波発生の可能性有無",
        # "N*": "Tsunamigenic Potential (Code: N)",
    },
    undefined="Tsunamigenic Potential (Code: %d)"
)
