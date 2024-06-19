from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcx_camf_d1_magnitude_on_richter_scale = QzssDcrDefinition(
    {
        0: "1.0-1.9 - Micro",
        1: "2.0-2.9 - Minor",
        2: "3.0-3.9 - Minor",
        3: "4.0-4.9 - Light",
        4: "5.0-5.9 - Moderate",
        5: "6.0-6.9 - Strong",
        6: "7.0-7.9 - Major",
        7: "8.0-8.9 - Great",
        8: "9.0 and greater - Great",
    },
    undefined='Undefined magnitude on richter scale (Code: %d)'
)

qzss_dcx_camf_d2_seismic_coefficient = QzssDcrDefinition(
    {
        0: '2',
        1: '3',
        2: '4',
        3: '5 weak',
        4: '5 strong',
        5: '6 weak',
        6: '6 strong',
        7: '7',
    },
    undefined='Undefined seismic coefficient (Code: %d)'
)

qzss_dcx_camf_d3_azimuth_from_centre_of_main_ellipse_to_epicentre = {
    0: 0.0,
    1: 22.5,
    2: 45.0,
    3: 67.5,
    4: 90.0,
    5: 112.5,
    6: 135.0,
    7: 157.5,
    8: 180.0,
    9: 202.5,
    10: 225.0,
    11: 247.5,
    12: 270.0,
    13: 292.5,
    14: 315.0,
    15: 337.5,
}

qzss_dcx_camf_d4_vector_length_between_centre_of_main_ellipse_and_epicentre = {
    0: 0.25,
    1: 0.5,
    2: 0.75,
    3: 1,
    4: 2,
    5: 3,
    6: 5,
    7: 10,
    8: 20,
    9: 30,
    10: 40,
    11: 50,
    12: 70,
    13: 100,
    14: 150,
    15: 200,
}

qzss_dcx_camf_d5_wave_height = QzssDcrDefinition(
    {
        0: 'H ≤ 0.5m',
        1: '0.5m < H ≤ 1.0m',
        2: '1.0m < H ≤ 1.5m',
        3: '1.5m < H ≤ 2.0m',
        4: '2.0m < H ≤ 3.0m',
        5: '3.0m < H ≤ 5.0m',
        6: '5.0m < H ≤ 10.0m',
        7: 'H > 10.0m',
    },
    undefined='Undefined wave height (Code: %d)'
)

qzss_dcx_camf_d6_temperature_range = QzssDcrDefinition(
    {
        0: 'T ≤ -30°C',
        1: '-30°C < T ≤ -25°C',
        2: '-25°C < T ≤ -20°C',
        3: '-20°C < T ≤ -15°C',
        4: '-15°C < T ≤ -10°C',
        5: '-10°C < T ≤ -5°C',
        6: '-5°C < T ≤ 0°C',
        7: '0°C < T ≤ 5°C',
        8: '5°C < T ≤ 10°C',
        9: '10°C < T ≤ 15°C',
        10: '15°C < T ≤ 20°C',
        11: '20°C < T ≤ 25°C',
        12: '25°C < T ≤ 30°C',
        13: '30°C < T ≤ 35°C',
        14: '35°C < T ≤ 45°C',
        15: 'T > 45°C',
    },
    undefined='Undefined temperature (Code: %d)'
)

qzss_dcx_camf_d7_hurricane_category = QzssDcrDefinition(
    {
        0: 'Category 1/5 hurricane: Very dangerous winds will produce some damage. Winds range from 120 to 150 km/h. Falling debris could strike people, livestock and pets, and older mobile homes could be destroyed. Protected glass windows will generally make it through the hurricane without major damage. Frame homes, apartments and shopping centres may experience some damage, and snapped power lines could result in short-term power outages.',
        1: 'Category 2/5 hurricane: Extremely dangerous winds will cause extensive damage. Winds range between 150 and 180 km/h. There is a bigger risk of injury or death to people, livestock and pets from flying debris. Older mobile homes will likely be destroyed, and debris can ruin newer mobile homes, too. Frame homes, apartment buildings and shopping centres may see major roof and siding damage, and many trees will be uprooted. Residents should expect near total power loss after a Category 2 hurricane, with outages lasting anywhere from a few days to a few weeks.',
        2: 'Category 3/5 hurricane: Devastating damage will occur. In a Category 3 hurricane, winds range from 180 to 210 km/h. There is a high risk of injury or death to people, livestock and pets from flying and falling debris. Nearly all older mobile homes will be destroyed, and most new ones will experience significant damage. Even well-built frame homes, apartments and industrial buildings will likely experience major damage, and the storm will uproot many trees that may block roads. Electricity and water will likely be unavailable for several days to a few weeks after the storm.',
        3: 'Category 4/5 hurricane: Catastrophic damage will occur. During a Category 4 hurricane, winds range from 210 to 250 km/h. At these speeds, falling and flying debris poses a very high risk of injury or death to people, pets and livestock. Again, most mobile homes will be destroyed, even newer ones. Some frame homes may totally collapse, while well-built homes will likely see severe damage to their roofs, and apartment buildings can experience damage to upper floors. A Category 4 hurricane will blow out most windows on high-rise buildings, uproot most trees and will likely down many power lines.',
        4: 'Category 5/5 hurricane: Catastrophic damage will occur. In a Category 5 hurricane, the highest category hurricane, winds are 250 km/h or higher. People, livestock and pets can be in danger from flying debris, even indoors. Most mobile homes will be completely destroyed, and a high percentage of frame homes will be destroyed. Commercial buildings with wood roofs will experience severe damage, metal buildings may collapse and high-rise windows will nearly all be blown out. A Category 5 hurricane is likely to uproot most trees and ruin most power poles. People should expect long-term water shortages and power outages.',
    },
    undefined='Undefined hurricane category (Code: %d)'
)

qzss_dcx_camf_d8_wind_speed = QzssDcrDefinition(
    {
        0: 'Beaufort 0 - 0km/h < v < 1km/h - Calm',
        1: 'Beaufort 1 - 1km/h < v < 5km/h - Light Air',
        2: 'Beaufort 2 - 6km/h < v < 11km/h - Light Breeze',
        3: 'Beaufort 3 - 12km/h < v < 19km/h - Gentle Breeze',
        4: 'Beaufort 4 - 20km/h < v < 30km/h - Moderate Breeze',
        5: 'Beaufort 5 - 31km/h < v < 39km/h - Fresh Breeze',
        6: 'Beaufort 6 - 40km/h < v < 50km/h - Strong Breeze',
        7: 'Beaufort 7 - 51km/h < v < 61km/h - Near Gale',
        8: 'Beaufort 8 - 62km/h < v < 74km/h - Gale',
        9: 'Beaufort 9 - 75km/h < v < 88km/h - Strong Gale',
        10: 'Beaufort 10 - 89km/h < v < 102km/h - Storm',
        11: 'Beaufort 11 - 103km/h < v < 117km/h - Violent Storm',
        12: 'Beaufort 12 - v > 118km/h - Hurricane',
    },
    undefined='Undefined wind speed (Code: %d)'
)

qzss_dcx_camf_d9_rainfall_amounts = QzssDcrDefinition(
    {
        0: 'p ≤ 2.5mm/h',
        1: '2.5mm/h < p ≤ 7.5mm/h',
        2: '7.5mm/h < p ≤ 10mm/h',
        3: '10mm/h < p ≤ 20mm/h',
        4: '20mm/h < p ≤ 30mm/h',
        5: '30mm/h < p ≤ 50mm/h',
        6: '50mm/h < p ≤ 80mm/h',
        7: '80mm/h < p',
    },
    undefined='Undefined rainfall amounts (Code: %d)'
)

qzss_dcx_camf_d10_damage_category = QzssDcrDefinition(
    {
        0: 'Category 1 - Very dangerous winds will produce some damage. Scale 1 and Intensity 1',
        1: 'Category 2 - Extremely dangerous winds will cause extensive damage. Scale 1 and Intensity 2',
        2: 'Category 3 - Devastating damage will occur. Scale 1 and Intensity 3',
        3: 'Category 4 - Catastrophic damage will occur. Scale 2 and Intensity 1',
        4: 'Category 5 - Catastrophic damage will occur. Scale 2 and Intensity 2',
        5: 'Category 5 - Catastrophic damage will occur. Scale 3 and Intensity 3',
    },
    undefined='Undefined damage category (Code: %d)'
)

qzss_dcx_camf_d11_tornado_probability = QzssDcrDefinition(
    {
        0: 'Non-Threatening - Threat: No discernible threat to life and property. Minimum Action: Listen for forecast changes; review tornado safety rules. Potential Impact: None expected; strong wind gusts may still occur.',
        1: 'Very Low - Threat: A very low threat to life and property. Minimum Action: Preparations should be made for a very low likelihood (or a 2 to 4% probability) of tornadoes; isolated tornadoes of F0 to F1 intensity possible. Potential Impact: The potential for isolated locations to experience minor to moderate tornado damage.',
        2: 'Low - Threat: A low threat to life and property. Minimum Action: Preparations should be made for a low likelihood (or a 5 to 14% probability) of tornadoes; scattered tornadoes of F0 to F1 intensity possible. Potential Impact: The potential for scattered locations to experience minor to moderate tornado damage.',
        3: 'Moderate - Threat: A moderate threat to life and property. Minimum Action: Preparations should be made for a moderate likelihood (or a 15 to 29% probability) of tornadoes; many tornadoes (even families) of F0 to F1 intensity possible. Potential Impact: The potential for many locations to experience minor to moderate tornado damage (see below). Some tornadoes may have longer damage tracks.',
        4: 'High - Threat: A high threat to life and property. Minimum Action: Preparations should be made for a high likelihood (or a 30 to 44% probability) of tornadoes; scattered tornadoes possible with isolated tornadoes of F2 to F5 intensity also possible. Potential Impact: The potential for isolated locations to experience major tornado damage (see below), among scattered locations of minor to moderate tornado damage. Some tornadoes may have longer damage tracks.',
        5: 'Extreme - Threat: An extreme threat to life and property. Minimum Action: Preparations should be made for a very high likelihood (or a 45% probability or greater) of tornadoes; many tornadoes (even families) possible with scattered tornadoes of F2 to F5 intensity also possible. Potential Impact: The potential for scattered locations to experience major tornado damage (see below), among many locations of minor to moderate tornado damage. Some tornadoes may have longer damage tracks',
    },
    undefined='Undefined tornado probability (Code: %d)'
)

qzss_dcx_camf_d12_hail_scale = QzssDcrDefinition(
    {
        0: 'H0 Hard hail. Typical hail diameter of 5 mm, No damage',
        1: 'H1 Potentially damaging. Typical hail diameter of 5-15 mm. Slight general damage to plants, crops',
        2: 'H2 Significant. Typical hail diameter of 10-20 mm. Slight general damage to fruit, crops, vegetation',
        3: 'H3 Severe. Typical hail diameter of 20-30 mm (size of a walnut). Severe damage to fruit and crops, damage to glass and plastic structures, paint and wood scored',
        4: 'H4 Severe. Typical hail diameter of 25-40 mm (size of a squash ball). Widespread glass damage, vehicle bodywork damage',
        5: 'H5 Destructive. Typical hail diameter of 30-50 mm (size of a golf ball). Wholesale destruction of glass, damage to tiled roofs, significant risk of injuries',
        6: 'H6 Destructive. Typical hail diameter of 40-60 mm. Bodywork of grounded aircraft dented, brick walls pitted',
        7: 'H7 Destructive. Typical hail diameter of 50-75 mm (size of a tennis ball). Severe roof damage, risk of serious injuries',
        8: 'H8 Destructive. Typical hail diameter of 60-90 mm (size of a large orange). Severe damage to aircraft bodywork',
        9: 'H9 Super Hailstorms. Typical hail diameter of 75-100 mm (size of a grapefruit). Extensive structural damage. Risk of severe or even fatal injuries to persons caught in the open',
        10: 'H10 Super Hailstorms. Typical hail diameter > 100 mm (size of a melon). Extensive structural damage. Risk of severe or even fatal injuries to persons caught in the open',
    },
    undefined='Undefined tornado probability (Code: %d)'
)

qzss_dcx_camf_d13_visibility = QzssDcrDefinition(
    {
        0: 'Dense fog: visibility < 20m',
        1: 'Thick fog: 20m < visibility < 200m',
        2: 'Moderate fog: 200m < visibility < 500m',
        3: 'Light fog: 500m < visibility < 1000m',
        4: 'Thin fog: 1km < visibility < 2km',
        5: 'Haze: 2km < visibility < 4km',
        6: 'Light haze: 4km < visibility < 10km',
        7: 'Clear: 10km < visibility < 20km',
        8: 'Very clear: 20km < visibility < 50km',
        9: 'Exceptionally clear: visibility > 50km',
    },
    undefined='Undefined visibility (Code: %d)'
)

qzss_dcx_camf_d14_snow_depth = QzssDcrDefinition(
    {
        0: '0cm < daily snow depth ≤ 20cm',
        1: '20cm < daily snow depth ≤ 40cm',
        2: '40cm < daily snow depth ≤ 60cm',
        3: '60cm < daily snow depth ≤ 80cm',
        4: '80cm < daily snow depth ≤ 100cm',
        5: '100cm < daily snow depth ≤ 120cm',
        6: '120cm < daily snow depth ≤ 140cm',
        7: '140cm < daily snow depth ≤ 160cm',
        8: '160cm < daily snow depth ≤ 180cm',
        9: '180cm < daily snow depth ≤ 200cm',
        10: '200cm < daily snow depth ≤ 220cm',
        11: '220cm < daily snow depth ≤ 240cm',
        12: '240cm < daily snow depth ≤ 260cm',
        13: '260cm < daily snow depth ≤ 280cm',
        14: '280cm < daily snow depth ≤ 300cm',
        15: '300cm < daily snow depth ≤ 320cm',
        16: '320cm < daily snow depth ≤ 340cm',
        17: '340cm < daily snow depth ≤ 360cm',
        18: '360cm < daily snow depth ≤ 380cm',
        19: '380cm < daily snow depth ≤ 400cm',
        20: '400cm < daily snow depth ≤ 420cm',
        21: '420cm < daily snow depth ≤ 440cm',
        22: '440cm < daily snow depth ≤ 460cm',
        23: '460cm < daily snow depth ≤ 480cm',
        24: '480cm < daily snow depth ≤ 500cm',
        25: '500cm < daily snow depth ≤ 520cm',
        26: '520cm < daily snow depth ≤ 540cm',
        27: '540cm < daily snow depth ≤ 560cm',
        28: '560cm < daily snow depth ≤ 580cm',
        29: '580cm < daily snow depth ≤ 600cm',
        30: 'daily snow depth > 600cm',
    },
    undefined='Undefined snow depth (Code: %d)'
)

qzss_dcx_camf_d15_flood_severity = QzssDcrDefinition(
    {
        0: 'Minor Flooding - Minimal or no property damage, but possibly some public threat.',
        1: 'Moderate Flooding - Some inundation of structures and roads near stream. Some evacuations of people and/or transfer of property to higher elevations.',
        2: 'Major Flooding - Extensive inundation of structures and roads. Significant evacuations of people and/or transfer of property to higher elevations.',
        3: 'Record Flooding',
    },
    undefined='Undefined flood severity (Code: %d)'
)

qzss_dcx_camf_d16_lightning_intensity = QzssDcrDefinition(
    {
        0: 'LAL 1 - No thunderstorms',
        1: 'LAL 2 - Isolated thunderstorms. Light rain will occasionally reach the ground. Lightning is very infrequent, 1 to 5 cloud to ground strikes in a 5-minute period.',
        2: 'LAL 3 - Widely scattered thunderstorms. Light to moderate rain will reach the ground. Lightning is infrequent, 6 to 10 cloud to ground strikes in a 5-minute period.',
        3: 'LAL 4 - Scattered thunderstorms. Moderate rain is commonly produced Lightning is frequent, 11 to 15 cloud to ground strikes in a 5-minute period.',
        4: 'LAL 5 - Numerous thunderstorms. Rainfall is moderate to heavy. Lightning is frequent and intense, greater than 15 cloud to ground strikes in a 5-minute period.',
        5: 'LAL 6 - Dry lightning (same as LAL 3 but without rain). This type of lightning has the potential for extreme fire activity and is normally.',
    },
    undefined='Undefined lightning intensity (Code: %d)'
)

qzss_dcx_camf_d17_fog_level = QzssDcrDefinition(
    {
        0: 'Level 1 of 5: Slight fog or Mist. On land, object appear hazy or blurry. Road and rail traffic are unhindered. On sea, horizon cannot be seen. Lights and landmarks can be seen at working distances.',
        1: 'Level 2 of 5: Slight fog. On land, railroad traffic takes additional caution. On sea, Lights on passing vessel are generally not distinct at distances under 1 mile. Fog signals are sounded.',
        2: 'Level 3 of 5: Moderate fog. On land, rail and road traffic is obstructed. On sea, Lights on passing vessels are generally not distinct at distances under 1 mile. Fog signals are sounded. On river, navigation is unhindered but extra caution is required.',
        3: 'Level 4 of 5: Moderate fog. On land, rail and road traffic impeded. On sea, lights on ships and other vessels cannot be seen at distances of 4 miles or less. On river, navigation is suspended.',
        4: 'Level 5 of 5: Thick fog. On land, all traffic is impeded and totally disorganised. On sea, lights on ships and other vessels cannot be seen at distances of 4 miles or less. On river, navigation is suspended.',
    },
    undefined='Undefined fog level (Code: %d)'
)

qzss_dcx_camf_d18_drought_level = QzssDcrDefinition(
    {
        0: 'D1 – Moderate Drought – PDSI = -2.0 to -2.9. Some damage to crops, pastures. Streams, reservoirs, or wells low, some water shortages developing or imminent. Voluntary water-use restrictions requested.',
        1: 'D2 – Severe Drought – PDSI = -3.0 to -3.9. Crop or pasture losses likely. Water shortages common. Water restrictions imposed.',
        2: 'D3 – Extreme Drought – PDSI = -4.0 to -4.9. Major crop/pasture losses. Widespread water shortages or restrictions.',
        3: 'D4 – Exceptional Drought – PDSI = -5.0 or less. Exceptional and widespread crop/pasture losses. Shortages of water in reservoirs, streams, and wells creating water emergencies.',
    },
    undefined='Undefined drought level (Code: %d)'
)

qzss_dcx_camf_d19_avalanche_warning_level = QzssDcrDefinition(
    {
        0: '1 – Low. Generally stable conditions. Triggering is generally possible only from high additional loads in isolated areas of very steep, extreme terrain. Only small and medium natural avalanches are possible.',
        1: '2 – Moderate. Heightened avalanche conditions on specific terrain features. Triggering is possible, primarily from high additional loads, particularly on the indicated steep slopes. Very large natural avalanches are unlikely.',
        2: '3 – Considerable. Dangerous avalanche conditions Triggering is possible, even from low additional loads, particularly on the indicated steep slopes. In certain situations, some large, and in isolated cases very large natural avalanches are possible.',
        3: '4 – High. Very dangerous avalanche conditions. Triggering is likely, even from low additional loads, on many steep slopes. In some cases, numerous large and often very large natural avalanches can be expected.',
        4: '5 – Very high. Extraordinary avalanche conditions. Numerous very large and often extremely large natural avalanches can be expected, even in moderately steep terrain.',
    },
    undefined='Undefined avalanche warning level (Code: %d)'
)

qzss_dcx_camf_d20_ash_fall_amount_and_impact = QzssDcrDefinition(
    {
        0: 'Less than 1 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Possible minor damage to vehicles, houses and equipment caused by fine abrasive ash. Possible contamination of water supplies, particularly roof-fed tank supplies. Dust may affect road visibility and traction for an extended period.',
        1: '1-5 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Minor damage to vehicles, houses and equipment caused by fine abrasive ash. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Dust may affect road visibility and traction for an extended period. Roads may need to be cleared to reduce the dust nuisance and prevent storm-water systems from becoming blocked. Possible crop damage. Some livestock may be affected.',
        2: '5-100 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Most buildings will support the ash load but weaker roof structures may collapse at 100 mm ash thickness, particularly if the ash is wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road transport may be halted due to the build-up of ash on roads. Cars still working may soon stop due to clogging of air-filters. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Likely crop damage. Most pastures will be killed by over 50 mm of ash. Some livestock may be affected.',
        3: '100-300 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Buildings that are not cleared of ash will run the risk of roof collapse, especially large flat roofed structures and if ash becomes wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road transport may be halted due to the build-up of ash on roads. Cars still working may soon stop due to clogging of air-filters. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Likely crop damage. Most pastures will be killed by over 50 mm of ash. Some livestock may be affected.',
        4: '> 300 mm ash thickness. Possible impact: Will act as an irritant to lungs and eyes. Damage to vehicles, houses and equipment caused by fine abrasive ash. Buildings that are not cleared of ash will run the risk of roof collapse, especially large flat roofed structures and if ash becomes wet. Possible contamination of water supplies, particularly roof-fed tank supplies. Electricity and water supplies may be cut or limited. Road unusable until cleared. Rail transport may be forced to stop due to signal failure bought on by short circuiting if ash becomes wet. Heavy kill of vegetation. Livestock and other animals killed or heavily distressed.',
    },
    undefined='Undefined ash fall amount and impact (Code: %d)'
)

qzss_dcx_camf_d21_geomagnetic_scale = QzssDcrDefinition(
    {
        0: 'G1 - Minor. Power systems: Weak power grid fluctuations can occur. Spacecraft operations: Minor impact on satellite operations possible. Other systems: Migratory animals are affected at this and higher levels; aurora is commonly visible at high latitudes.',
        1: 'G2 - Moderate. Power systems: High-latitude power systems may experience voltage alarms, long-duration storms may cause transformer damage. Spacecraft operations: Corrective actions to orientation may be required by ground control; possible changes in drag affect orbit predictions. Other systems: HF radio propagation can fade at higher latitudes, and aurora has been seen as low as 55° geomagnetic lat.',
        2: 'G3 - Strong. Power systems: Voltage corrections may be required, false alarms triggered on some protection devices. Spacecraft operations: Surface charging may occur on satellite components, drag may increase on low-Earth-orbit satellites, and corrections may be needed for orientation problems. Other systems: Intermittent satellite navigation and low-frequency radio navigation problems may occur, HF radio may be intermittent, and aurora has been seen as low as 50° geomagnetic lat.',
        3: 'G4 - Severe. Power systems: Possible widespread voltage control problems and some protective systems will mistakenly trip out key assets from the grid. Spacecraft operations: May experience surface charging and tracking problems, corrections may be needed for orientation problems. Other systems: Induced pipeline currents affect preventive measures, HF radio propagation sporadic, satellite navigation degraded for hours, low-frequency radio navigation disrupted, and aurora has been seen as low as 45° geomagnetic lat.',
        4: 'G5 - Extreme. Power systems: Widespread voltage control problems and protective system problems can occur; some grid systems may experience complete collapse or blackouts. Transformers may experience damage. Spacecraft operations: May experience extensive surface charging, problems with orientation, uplink/downlink and tracking satellites. Other systems: Pipeline currents can reach hundreds of amps, HF (high frequency) radio propagation may be impossible in many areas for one to two days, satellite navigation may be degraded for days, low-frequency radio navigation can be out for hours, and aurora has been seen as low 40° geomagnetic lat.',
    },
    undefined='Undefined geomagnetic scale (Code: %d)'
)

qzss_dcx_camf_d22_terrorism_threat_level = QzssDcrDefinition(
    {
        0: 'Very low threat level. A violent act of terrorism is highly unlikely. Measures are in place to keep the population safe.',
        1: 'Low threat level. A violent act of terrorism is possible but unlikely. Measures are in place to keep the population safe.',
        2: 'Medium threat level. A violent act of terrorism could occur. Additional measures are in place to keep the population safe.',
        3: 'High threat level. A violent act of terrorism is likely. Heightened measures are in place to keep the population safe.',
        4: 'Critical threat level. A violent act of terrorism is highly likely and could occur imminently. Exceptional measures are in place to keep the population safe.',
    },
    undefined='Undefined geomagnetic scale (Code: %d)'
)

qzss_dcx_camf_d23_fire_risk_level = QzssDcrDefinition(
    {
        0: 'Danger level 1/5 (low or none danger). Small fires cannot be entirely ruled out, but require a high energy input. Lightning hardly ever causes a fire. Rate of spread: Generally slow. Characteristics: Surface or crawling fires, crowns of trees are not affected, topsoil does not burn. Fire-fighting: Forest fire is easy to extinguish. Behaviour: Do not carelessly discard cigarettes, tobacco products or lighters.',
        1: 'Danger level 2/5 (moderate danger). Local fires can start spontaneously. Lightning only rarely causes a conflagration. Rate of spread: Slow to medium. Characteristics: Surface or crawling fires, crowns of trees are rarely affected, topsoil is burnt a little or not at all. Fire-fighting: Forest fire is ordinarily easy to extinguish. Behaviour: Do not carelessly discard cigarettes, tobacco products or lighters. Always watch barbecue fires and immediately extinguish stray sparks.',
        2: 'Danger level 3/5 (considerable danger): Burning matches and flying sparks from barbecue fires can ignite a fire. Lightning can also trigger widespread fires. Rate of spread: High in open terrain, medium in the forest. Characteristics. Topsoil is partly burnt; individual crown fires are possible. Fire-fighting: Forest fire can be extinguished only by experts using modern equipment. Behaviour: Light barbecue fires only in existing fire places. Always watch the fire and immediately extinguish stray sparks.',
        3: 'Danger level 4/5 (high danger). Burning matches, flying sparks from barbecue fires and lightning will very probably ignite a fire. Rate of spread: High, including in forests. Characteristics: Intense surface fires can ignite the crowns of individual trees, spotting is possible, burning topsoil. Fire-fighting: Forest fire is difficult to extinguish and commands extensive resources. Behaviour: As a general rule, do not make any fires outdoors. Permanent fire places (concreted base) in locations designated by the authorities can be used with the utmost caution. Do not make fires in strong winds.',
        4: 'Danger level 5/5 (very high danger). Fires can start at any time. Rate of spread: Very high over a long period. Characteristics: Very intense burning, extensive crown fires, long-distance spotting. Fire-fighting: Forest fire is virtually impossible to extinguish. Behaviour: Do not make any fires outdoors. Follow the instructions and observe the fire bans imposed by the local authorities.',
    },
    undefined='Undefined fire risk level (Code: %d)',
)

qzss_dcx_camf_d24_water_quality = QzssDcrDefinition(
    {
        0: 'Excellent water quality',
        1: 'Good water quality',
        2: 'Poor water quality',
        3: 'Very poor water quality',
        4: 'Suitable for drinking purposes',
        5: 'Unsuitable for drinking purpose',
    },
    undefined='Undefined water quality (Code: %d)'
)

qzss_dcx_camf_d25_uv_index = QzssDcrDefinition(
    {
        0: 'Index 0 - 2 Low. No protection needed. You can safely stay outside using minimal sun protection.',
        1: 'Index 3/11 Moderate. Protection needed. Seek shade during late morning through mid-afternoon. When outside, generously apply broad-spectrum SPF-15 or higher sunscreen on exposed skin, and wear protective clothing, a wide-brimmed hat, and sunglasses.',
        2: 'Index 4/11 Moderate. Protection needed. Seek shade during late morning through mid-afternoon. When outside, generously apply broad-spectrum SPF-15 or higher sunscreen on exposed skin, and wear protective clothing, a wide-brimmed hat, and sunglasses.',
        3: 'Index 5/11 High. Protection needed. Seek shade during late morning through mid-afternoon. When outside, generously apply broad-spectrum SPF-15 or higher sunscreen on exposed skin, and wear protective clothing, a wide-brimmed hat, and sunglasses.',
        4: 'Index 6/11 High. Protection needed. Seek shade during late morning through mid-afternoon. When outside, generously apply broad-spectrum SPF-15 or higher sunscreen on exposed skin, and wear protective clothing, a wide-brimmed hat, and sunglasses.',
        5: 'Index 7/11 High. Protection needed. Seek shade during late morning through mid-afternoon. When outside, generously apply broad-spectrum SPF-15 or higher sunscreen on exposed skin, and wear protective clothing, a wide-brimmed hat, and sunglasses.',
        6: 'Index 8/11 Very high. Extra protection needed. Be careful outside, especially during late morning through mid-afternoon. If your shadow is shorter than you, seek shade and wear protective clothing, a wide-brimmed hat, and sunglasses, and generously apply a minimum of SPF-15, broad-spectrum sunscreen on exposed skin.',
        7: 'Index 9/11 Very high. Extra protection needed. Be careful outside, especially during late morning through mid-afternoon. If your shadow is shorter than you, seek shade and wear protective clothing, a wide-brimmed hat, and sunglasses, and generously apply a minimum of SPF-15, broad-spectrum sunscreen on exposed skin.',
        8: 'Index 10/11 Extreme. Extra protection needed. Be careful outside, especially during late morning through mid-afternoon. If your shadow is shorter than you, seek shade and wear protective clothing, a wide-brimmed hat, and sunglasses, and generously apply a minimum of SPF-15, broad-spectrum sunscreen on exposed skin.',
        9: 'Index 11/11 Extreme. Extra protection needed. Be careful outside, especially during late morning through mid-afternoon. If your shadow is shorter than you, seek shade and wear protective clothing, a wide-brimmed hat, and sunglasses, and generously apply a minimum of SPF-15, broad-spectrum sunscreen on exposed skin.',
    },
    undefined='Undefined UV index (Code: %d)'
)

qzss_dcx_camf_d26_number_of_cases_per_100000_inhabitants = QzssDcrDefinition(
    {
        0: '0 - 9',
        1: '10 - 20',
        2: '21 - 50',
        3: '51 - 70',
        4: '71 - 100',
        5: '101- 125',
        6: '126 - 150',
        7: '151 - 175',
        8: '176 - 200',
        9: '201 - 250',
        10: '251 - 300',
        11: '301 - 350',
        12: '351 - 400',
        13: '401 - 450',
        14: '451 - 500',
        15: '501 - 750',
        16: '751 - 1000',
        17: '> 1000',
        18: '> 2000',
        19: '> 3000',
        20: '> 5000',
    },
    undefined='Undefined number of cases per 100000 inhabitants (Code: %d)'
)

qzss_dcx_camf_d27_noise_range = QzssDcrDefinition(
    {
        0: '40 < dB ≤ 45',
        1: '45 < dB ≤ 50',
        2: '50 < dB ≤ 60',
        3: '60 < dB ≤ 70',
        4: '70 < dB ≤ 80 (loud)',
        5: '80 < dB ≤ 90 (very loud)',
        6: '90 < dB ≤ 100 (very loud)',
        7: '100 <dB ≤ 110 (very loud)',
        8: '110 < dB ≤ 120 (extremely loud)',
        9: '120 < dB ≤ 130 (extremely loud)',
        10: '130 < dB ≤ 140 (threshold of pain)',
        11: 'dB > 140 (pain)',
    },
    undefined='Undefined noise range (Code: %d)'
)

qzss_dcx_camf_d28_air_quality_index = QzssDcrDefinition(
    {
        0: 'Index value 0 - 50. Good. Green. Advisory: None.',
        1: 'Index value 51 - 100. Moderate. Yellow. Unusually sensitive individuals should consider limiting prolonged outdoor exertion.',
        2: 'Index 101 - 150. Unhealthy for sensitive groups. Orange. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion',
        3: 'Index 151 - 200. Unhealthy. Red. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion. Everyone else should limit prolonged outdoor exertion.',
        4: 'Index 201 - 300. Very unhealthy. Purple. Children, active adults and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion. Everyone else should limit outdoor exertion.',
        5: 'Index 301 - 500. Hazardous.Brown.Everyone should avoid all physical activity outdoor.',
    },
    undefined='Undefined air quality index (Code: %d)'
)

qzss_dcx_camf_d29_outage_estimated_duration = QzssDcrDefinition(
    {
        0: '0 < duration < 30 min',
        1: '30 min ≤ duration < 45 min',
        2: '45 min ≤ duration < 1 h',
        3: '1 h ≤ duration < 1h 30min',
        4: '1h 30min ≤ duration < 2 h',
        5: '2 h ≤ duration < 3 h',
        6: '3 h ≤ duration < 4 h',
        7: '4 h ≤ duration < 5 h',
        8: '5 h ≤ duration < 10 h',
        9: '10 h ≤ duration < 24 h',
        10: '24 h ≤ duration < 2 days',
        11: '2 days ≤ duration < 7 days',
        12: '7 days ≤ duration',
    },
    undefined='Undefined outage estimated duration (Code: %d)'
)

qzss_dcx_camf_d30_nuclear_event_scale = QzssDcrDefinition(
    {
        0: 'Unknown',
        1: 'Level 0/7. Deviation. No safety significance',
        2: 'Level 1/7. Anomaly. Overexposure in excess of statutory annual limits. Minor problems with safety components with significant defence-in-depth remaining. Low activity lost or stolen radioactive source, device, or transport package.',
        3: 'Level 2/7. Incident. Impact on people and environment: Exposure of the public in excess of 10 mSv. Exposure of workers in excess of the statutory annual limits. Impact on radiological barriers and control: Radiation levels in an operating area of more than 50 mSv/h. Significant contamination within the facility into an area not expected by design. Possible cause: Significant failures in safety provisions but with no actual consequences. Found highly radioactive sealed orphan source, device or transport package with safety provisions intact. Inadequate packaging of a highly radioactive sealed source.',
        4: 'Level 3/7. Serious incident. Impact on people and environment: Exposure in excess of ten times the statutory annual limit for workers. Non-lethal deterministic health effect (e.g., burns) from radiation. Impact on radiological barriers and control: Exposure rates of more than 1 Sv/h in an operating area. Severe contamination in an area not expected by design, with a low probability of significant public exposure. Possible cause: Near-accident at a nuclear power plant with no safety provisions remaining. Lost or stolen highly radioactive sealed source. Misdelivered highly radioactive sealed source without adequate procedures in place to handle it.',
        5: 'Level 4/7. Accident with local consequences. Impact on people and environment: Minor release of radioactive material unlikely to result in implementation of planned countermeasures other than local food controls. Impact on radiological barriers and control: Release of significant quantities of radioactive material within an installation with a high probability of significant public exposure.',
        6: 'Level 5/7. Accident with wider consequences. Impact on people and environment: Limited release of radioactive material likely to require implementation of some planned countermeasures. Major health impact from radiation is likely. Impact on radiological barriers and control: Severe damage to reactor core. Release of large quantities of radioactive material within an installation with a high probability of significant public exposure. This could arise from a major criticality accident or fire.',
        7: 'Level 6/7. Serious accident. Impact on people and environment: Significant release of radioactive material likely to require implementation of planned countermeasures.',
        8: 'Level 7/7. Major accident. Impact on people and environment: Major release of radioactive material with widespread health and environmental effects requiring implementation of planned and extended countermeasures.',
    },
    undefined='Undefined nuclear event scale (Code: %d)'
)

qzss_dcx_camf_d31_chemical_hazard_type = QzssDcrDefinition(
    {
        0: 'Explosives',
        1: 'Flammable gases',
        2: 'Flammable aerosols and aerosols',
        3: 'Oxidizing gases',
        4: 'Gases under pressure',
        5: 'Flammable liquids',
        6: 'Flammable solids',
        7: 'Self-reactive substance/mixture',
        8: 'Pyrophoric liquids. Pyrophoric materials are often water-reactive as well and will ignite when they contact water or humid air.',
        9: 'Pyrophoric solids. Pyrophoric materials are often water-reactive as well and will ignite when they contact water or humid air.',
        10: 'Self-heating substance/mixture',
        11: 'Water-reactive - emits flammable gases',
        12: 'Oxidising liquids',
        13: 'Oxidising solids',
        14: 'Organic peroxides',
        15: 'Corrosive to metals',
    },
    undefined='Undefined chemical hazard type (Code: %d)'
)

qzss_dcx_camf_d32_biohazard_level = QzssDcrDefinition(
    {
        0: 'Biohazard Level 1/4: Often pertains to agents that include viruses and bacteria, this biosafety level requires minimal precaution, such as wearing face masks and maintaining no close contact. The biological hazard examples in the first level include E. coli and other non-infectious bacteria.',
        1: 'Biohazard Level 2/4: Usually causing severe diseases to humans, the second level classifies agents that can be transmitted through direct contact with infected materials. HIV and hepatitis B are some biological hazard examples that pose moderate risks to humans.',
        2: 'Biohazard Level 3/4: Mainly through respiratory transmission, pathogens that are highly likely to become airborne can cause serious or lethal diseases to humans. Mycobacterium tuberculosis, the bacteria that causes tuberculosis, is an example of a level-3 biohazard.',
        3: 'Biohazard Level 4/4: Extremely dangerous pathogens that expose humans to life-threatening diseases, the fourth and last level requires workers to utilise maximum protection and containment. Some biological hazard examples are the Ebola virus and the Lassa virus.',
    },
    undefined='Undefined biohazard level (Code: %d)'
)

qzss_dcx_camf_d33_biohazard_type = QzssDcrDefinition(
    {
        0: "Biological agents. These include bacteria, viruses, parasites, and fungi (such as yeasts and molds).",
        1: "Biotoxins. These refer to a group of substances with a biological origin that are toxic and poisonous to humans. Often, biotoxins are produced by plants, bacteria, insects, or certain animals, among others.Continuous exposure to these may cause, at the very least, a series of inflammatory reactions throughout the body.",
        2: "Blood and blood products. While blood isn't considered a biological hazard, it can still bring potential risks if it's contaminated or its source is in any way infected. Also, blood products such as red blood cells, white blood cells, plasma, tissues, and platelets are also hazardous if not properly handled.",
        3: "Environmental specimens. Generally, these refer to plants, soil, or water that potentially contain biological agents(include bacteria, viruses, parasites, and fungi) and biotoxins.",
    },
    undefined='Undefined biohazard type (Code: %d)'
)

qzss_dcx_camf_d34_explosive_hazard_type = QzssDcrDefinition(
    {
        0: 'PE1 - Mass explosion hazard in which the entire body of explosives explodes as one.',
        1: 'PE2 - Serious projectile hazard but does not have a mass explosion hazard.',
        2: 'PE3 - Fire hazard and either a minor blast hazard or a minor projection hazard, or both, but does not have a mass explosion hazard. Explosives which give rise to considerable radiant heat or which burn to produce a minor blast or projection hazard.',
        3: 'PE4 - Fire or slight explosion hazard, or both, with only local effect. Explosives which present only a low hazard in the event of ignition or initiation, where no significant blast or projection of fragments of appreciable size or range is expected.',
    },
    undefined='Undefined explosive hazard type (Code: %d)'
)

qzss_dcx_camf_d35_infection_type = QzssDcrDefinition(
    {
        0: "Anthrax",
        1: "Avian influenza in humans",
        2: "Botulism",
        3: "Brucellosis",
        4: "Campylobacteriosis",
        5: "Chikungunya virus disease",
        6: "Chlamydia infections",
        7: "Cholera",
        8: "COVID - 19",
        9: "Creutzfeldt - Jakob Disease - variant(vCJD)",
        10: "Cryptosporidiosis",
        11: "Dengue",
        12: "Diphtheria",
        13: "Echinococcosis",
        14: "Giardiasis",
        15: "Gonorrhoea",
        16: "Hepatitis A",
        17: "Hepatitis B",
        18: "Hepatitis C",
        19: "HIV infection and AIDS",
        20: "Infections with haemophilus influenza group B",
        21: "Influenza including Influenza A(H1N1)",
        22: "Invasive meningococcal disease",
        23: "Invasive pneumococcal disease",
        24: "Legionnaries' disease",
        25: "Leptospirosis",
        26: "Listeriosis",
        27: "Lyme neuroborreliosis",
        28: "Malaria",
        29: "Measles",
        30: "Meningoccocal disease, invasive",
        31: "Mumps",
        32: "Pertussis",
        33: "Plague",
        34: "Pneumoccocal invasive diseases",
        35: "Poliomyelitis",
        36: "Q fever",
        37: "Rabies",
        38: "Rubella",
        39: "Rubella, congenital",
        40: "Salmonellosis",
        41: "Severe Acute Respiratory Syndrome (SARS)",
        42: "Shiga toxin /verocytotoxin -producing Escherichia coli (STEC/VTEC)",
        43: "Shigellosis",
        44: "Smallpox",
        45: "Syphilis",
        46: "Syphilis, congenital",
        47: "Tetanus",
        48: "Tick-borne encephalitis",
        49: "Toxoplasmosis, congenital",
        50: "Trichinellosis",
        51: "Tuberculosis",
        52: "Tularaemia",
        53: "Typhoid and paratyphoid fevers",
        54: "Viral haemorrhagic fevers",
        55: "West Nile virus infection",
        56: "Yellow fever",
        57: "Yersinosis",
        58: "Zika virus disease",
        59: "Zika virus disease, congenital",
        60: "Nosocomial infections",
        61: "Antimicrobial resistance",
        62: "unidentified infection",
    },
    undefined='Undefined infection type (Code: %d)'
)

qzss_dcx_camf_d36_typhoon_category = QzssDcrDefinition(
    {
        0: 'Scale 1 and Intensity 1',
        1: 'Scale 1 and Intensity 2',
        2: 'Scale 1 and Intensity 3',
        3: 'Scale 2 and Intensity 1',
        4: 'Scale 2 and Intensity 2',
    },
    undefined='Undefined typhoon category (Code: %d)'
)
