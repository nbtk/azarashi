"""Who sent the alert, by the country A2 names. Each country assigns its own identifiers.

Keyed by the A2 code, not by country name: the code is what the message carries, and country
names change while their codes do not. A service specification that publishes another country's
identifiers adds it here.
"""
from ..code_table import CodeTable

a3_provider_identifier_map: dict[int, CodeTable[int, str]] = {
    10: CodeTable(  # Australia
        {
            1: 'National Emergency Management Agency',
            2: 'Bureau of Meteorology',
            3: 'Australian Climate Service',
            4: 'Geoscience Australia',
            5: 'Commonwealth Scientific and Industrial Research Organisation',
            6: 'Australian Bureau of Statistics',
            7: 'Resilience New South Wales',
            8: 'State Emergency Service New South Wales',
            9: 'New South Wales Rural Fire Service',
            10: 'Joint Australian Tsunami Warning Centre',
            11: 'Flood Knowledge Centre',
            12: 'Australian Broadcasting Corporation',
        },
        undefined="Undefined Provider Identifier of Australia (Code: %d)"
    ),
    71: CodeTable(  # Fiji
        {
            1: 'National Disaster Management Office',
            2: 'Fiji Meteorological Service',
            3: 'Hydrology Section, Fiji Water Authority',
            4: 'Mineral Resources Department',
            5: 'Fiji Broadcasting Corporation',
        },
        undefined="Undefined Provider Identifier of Fiji (Code: %d)"
    ),
    111: CodeTable(  # Japan
        {
            1: 'Foundation for MultiMedia Communications',
            2: 'Fire and Disaster Management Agency',
            3: 'Related Ministries',
            4: 'Local Government',
        },
        undefined="Undefined Provider Identifier of Japan (Code: %d)"
    ),
    219: CodeTable(  # Thailand
        {
            1: 'Department of Disaster Prevention and Mitigation',
            2: 'Thai Meteorological Department',
            3: 'National Disaster Warning Center',
            4: 'Department of Mineral Resources',
            5: 'Navy Hydrographic Department, Royal Thai Navy',
            6: 'Department of Water Resources',
            7: 'Royal Irrigation Department',
            8: 'Department of Pollution Control',
            9: 'Geo-Informatics and Space Technology Development Agency',
            10: 'Electricity Generating Authority of Thailand',
            11: 'Royal Forest Department',
            12: 'Department of Parks, Wildlife and Plant Conservation',
            13: 'Water Crisis Prevention Center',
        },
        undefined="Undefined Provider Identifier of Thailand (Code: %d)"
    ),
}

a3_provider_identifier_undefined: CodeTable[int, str] = CodeTable(
    {},
    undefined="Undefined Provider Identifier (Code: %d)"
)
