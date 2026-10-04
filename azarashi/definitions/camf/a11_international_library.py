"""International A11, two five-bit lists: CAMF Issue 1.2, 3.5.3 and Annex C 11.

a11_international_library and a11_international_library_code are List A. List B has
its own tables; its codes 29 and 30 are reserved.
"""
from ..code_table import CodeTable


a11_international_library_code = CodeTable(
    {
        0: "IC-A-01",
        1: "IC-A-02",
        2: "IC-A-03",
        3: "IC-A-04",
        4: "IC-A-05",
        5: "IC-A-06",
        6: "IC-A-07",
        7: "IC-A-08",
        8: "IC-A-09",
        9: "IC-A-10",
        10: "IC-A-11",
        11: "IC-A-12",
        12: "IC-A-13",
        13: "IC-A-14",
        14: "IC-A-15",
        15: "IC-A-16",
        16: "IC-A-17",
        17: "IC-A-18",
        18: "IC-A-19",
        19: "IC-A-20",
        20: "IC-A-21",
        21: "IC-A-22",
        22: "IC-A-23",
        23: "IC-A-24",
        24: "IC-A-25",
        25: "IC-A-26",
        26: "IC-A-27",
        27: "IC-A-28",
        28: "IC-A-29",
        29: "IC-A-30",
        30: "IC-A-31",
        31: "IC-A-32",
    },
    undefined='IC-A-UNDEFINED (Code: %d)'
)


a11_international_library = CodeTable(
    {
        0: "",
        1: "You are in the danger zone, leave the area immediately. Listen to radio or media for directions and information.",
        2: "You are in the danger zone, leave the area immediately and reach the evacuation point indicated by the area plotted in yellow. Listen to radio or media for directions and information.",
        3: "Seek shelter in a building immediately. Stay under cover and stay informed.",
        4: "Seek out a cellar or interior rooms on lower floors.",
        5: "If you are in an alpine terrain, start descending immediately and seek for shelter.",
        6: "Quickly move into interior rooms. If you are in a vehicle: Stop driving immediately on the edge of the road. If a building is nearby, seek shelter in that building.",
        7: "If you are in open terrain and you cannot find shelter, lie face-down on the ground and protect your head and neck with your hands, in a hollow where possible.",
        8: "Prepare for evacuation. Take only the essentials with you, especially ID cards, passport, credit cards and cash. Evacuate only after the instruction of the emergency authorities.",
        9: "Prepare emergency food and relief material: Check and restock your equipment and supplies of water, food, medicine, cash and batteries.",
        10: "Stay away from glass surfaces such as windows and glass doors. There is a risk of injury from glass splinters.",
        11: "Reduce your power consumption to a minimum.",
        12: "Reduce your water consumption to a minimum.",
        13: "Boil water before drinking it or using it in the kitchen.",
        14: "Keep at least one metre away from any conversation partners. Avoid physical contact with other people such as kissing and shaking hands. Wash your hands regularly and thoroughly.",
        15: "Do not drink any tap water. Avoid any skin contact with tap water. Only drink mineral water from a bottle. Turn off the water supply to your house.",
        16: "Watch out for escaping gas. This can be indicated by hissing noises or a typical gas odour. Do not use matches, lighters or the like: naked flames in combination with leaking gas can lead to explosions and fires.",
        17: "Do not go outside and do not use your car.",
        18: "Do not touch any objects that seem suspicious to you. Debris can cause additional hazards such as fires and explosions. Inform the emergency services about damage and debris.",
        19: "Do not enter smoke-filled rooms. Deadly gases can form there.",
        20: "Do not enter cellars or underground car parks.",
        21: "Do not leave pets or livestock outside.",
        22: "Do not touch any dead animals. Report any findings of dead wild animals to the authorities.",
        23: "Avoid driving.",
        24: "Avoid all items with metal parts such as umbrellas and bicycles. Do not bathe or shower during a thunderstorm. Bathing and showering can be life-threatening.",
        25: "Avoid rooms directly underneath the roof truss. Avoid very large rooms, such as halls, in which the ceiling is not supported by pillars.",
        26: "Avoid going outdoors. Keep away from trees, towers and masts. Keep at least 20 m away from power lines. Watch out for flying objects and falling objects.",
        27: "Avoid the danger area.",
        28: "Avoid going out when it is not necessary.",
        29: "This is only a test. You do not have to take any action or to adopt any particular sheltering behaviour.",
        30: "This replaces the warning previously in effect for this area.",
        31: "Conditions have improved and are no longer expected to meet alert criteria.",
    },
    undefined='Undefined instruction in the international library. (Code: %d)'
)


a11_international_library_b_code = CodeTable(
    {code: f'IC-B-{code + 1:02d}' for code in range(32)},
    undefined='IC-B-UNDEFINED (Code: %d)'
)

a11_international_library_b = CodeTable(
    {
        0: "",
        1: "Check with the weather services and local authorities for additional information",
        2: "Find out the location of the information points set up by the authorities on official channels (radio, internet, TV, social networks…)",
        3: "Sensitive or vulnerable people should not go out unless they must.",
        4: "Rescue operation under process by security forces and emergency services. Avoid moving to facilitate security and emergency actions.",
        5: "Protect the most vulnerable and hear from your loved ones. Be aware of their special needs and support, as required. If you notice distressed or vulnerable persons, call the emergency services. Provide first aid if necessary but do not put yourself in any danger.",
        6: "Pay attention to announcements made by the police, fire brigade and by officials.",
        7: "Stay aware, keep listening to official instructions broadcast on the radio, television, websites and social networks pages",
        8: "If you need help leaving your home, call the emergency services.",
        9: "Only make phone calls in serious emergencies to avoid overloading the mobile network.",
        10: "Extreme intensity weather phenomena expected. The weather is very dangerous and implies high level of threat to health, even the life hazard. BE AWARE and keep up to date with the latest weather forecast.",
        11: "Severe weather expected. BE PREPARED. Take precautions and keep up to date with the latest weather forecast. Severe damages to people and properties may occur, especially to those vulnerable or in exposed areas.",
        12: "Moderate intensity weather phenomena expected. BE AWARE, keep up to date with the latest weather forecast. Moderate damages to people and properties may occur, especially to those vulnerable or in exposed areas",
        13: "BE PREPARED to protect yourself and your property. Flooding of properties and transport networks is expected. Disruption to power, communications and water supplies are possible. Evacuation may be required. Dangerous driving conditions due to reduced visibility and aquaplaning",
        14: "Do not go near or in flooded waters. Do not walk or drive on a submerged road. Flood waves may surprise you, the river bank may collapse or you could be sucked in a manhole or hit by a floating debris. Keep drains and shafts clear so that the water can drain away. Secure and/or move assets away from vulnerable area (car along the river, basements).",
        15: "Take shelter in the most resistant part of a permanent building, a municipal shelter if possible, and keep away from windows. BE AWARE of the “eye of the storm”, the calm area in its centre. It will be followed by an inversion and the strengthening of winds. Do not go outside and do not use your car. Wait until the alert is over.",
        16: "TAKE PRECAUTIONS, High temperatures are expected. Protect yourself from the heat and avoid physical and sports activities. Wet your body several times a day. Drink plenty of water and eat light food.",
        17: "Forest fire danger. Under these conditions fires may develop and spread rapidly resulting in damage to property and possible loss of human and/or animal life. Do not throw away any burning cigarettes or matches to the environment. Do not make a fire outdoors. Do not light any fireworks. Do not barbeque in open places. Vegetation is easily ignited and large areas may be affected. Follow the instructions from the local authorities.",
        18: "Risks of fire. Use permanent fireplaces when barbecuing. Make sure your fire is completely extinguished before you leave. Only light fireworks with the permission of the municipality, keep a safe distance from the forest and have water to hand.",
        19: "Keep as far away as possible from coastal areas, beaches and rivers. Get immediately to the highest ground possible and wait until the alert is over. If you are in danger of being overtaken by waves, climb onto a roof or up a solid tree, or cling on to a floating object carried along by the water.",
        20: "Do not go to sea and keep as far away as possible from the coast and wait until the alert is over. If you are at sea, don’t return to port. Keep away from the coast. Waves are much less dangerous out at sea.",
        21: "Leave the affected area immediately and seek higher ground or move to higher parts of the building. Listen to radio or media for directions and information",
        22: "Indoors: during the quake, take shelter near a wall or a solid piece of furniture. Outside: during the quake, keep away from anything that might collapse. In a car: during the quake, stop as far away from buildings as you can. After, be prepared for aftershocks. If you are indoor, leave by the stairs.",
        23: "Leave the impact site immediately and cover your mouth and nose with improvised respiratory protection (cloth, garment, surgical mask). This protects you from dust, but not from gaseous hazardous substances. Seek out a building. Move wherever possible at a right angle to the wind direction as this is the quickest way to leave the danger zone with a possible cloud of hazardous substances.",
        24: "Switch off the ventilation and air conditioning systems. Close all windows, doors and shutters. Cover your mouth and nose and breathe through a facemask or an improvised respiratory protection (cloth, garment, surgical mask) if the air is filled with smoke and ashes",
        25: "Have iodine tablets ready. DO NOT take the iodine tablets now. If this becomes necessary, we will inform you in good time.",
        26: "Take the iodine tablets NOW according to the package insert.",
        27: "Avoid watering your plants during the hottest hours, avoid using water for secondary uses such as washing your car.",
        28: "Seek shelter if you cannot leave the area immediately.",
        31: "This replaces the warning previously in effect for this area.",
    },
    undefined='Undefined instruction in the international library List B. (Code: %d)'
)
