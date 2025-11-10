try:
    from .resourcess import Resource
# Fall back to direct imports for when running this file as a script
except ImportError:
    # This block runs when `country.py` is executed as a script
    from resourcess import Resource

country_resources: dict[str, dict[str, Resource]] = {
    "Russia": {
        "PETROLEUM": Resource(80.0, "billion barrels"),
        "NATURAL_GAS": Resource(47.8, "trillion cubic meters"),
        "COAL": Resource(160.0, "billion tonnes"),
        "URANIUM": Resource(0.61, "million tonnes"),
        "GOLD": Resource(13.0, "thousand tonnes"),
        "NICKEL": Resource(8.8, "million tonnes"),
        "IRON_ORE": Resource(47.0, "billion tonnes"),
        "DIAMONDS": Resource(2.0, "million carats annually"),
        "COPPER": Resource(1.4, "million tonnes"),
        "TIN": Resource(0.15, "million tonnes"),
        "BAUXITE": Resource(0.5, "million tonnes"),
        "COBALT": Resource(0.03, "million tonnes"),
        "PALLADIUM": Resource(0.08, "million tonnes"),
        "PLATINUM": Resource(0.02, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.01, "million tonnes"),
        "TUNGSTEN": Resource(0.03, "million tonnes"),
        "NIOBIUM": Resource(0.05, "million tonnes"),
    },
    "Kuwait": {
        "PETROLEUM": Resource(104.0, "billion barrels"),
        "NATURAL_GAS": Resource(1.8, "trillion cubic meters"),
    },
    "Nigeria": {
        "PETROLEUM": Resource(37.0, "billion barrels"),
        "NATURAL_GAS": Resource(5.3, "trillion cubic meters"),
        "COAL": Resource(0.5, "billion tonnes"),
        "TIN": Resource(0.25, "million tonnes"),
    },
    "Chad": {
        "PETROLEUM": Resource(1.5, "billion barrels"),
        "URANIUM": Resource(0.05, "million tonnes"),
        "GOLD": Resource(0.15, "thousand tonnes"),
    },
    "Iran": {
        "PETROLEUM": Resource(155.6, "billion barrels"),
        "NATURAL_GAS": Resource(33.8, "trillion cubic meters"),
        "URANIUM": Resource(0.25, "million tonnes"),
        "IRON_ORE": Resource(3.5, "billion tonnes"),
        "COPPER": Resource(0.8, "million tonnes"),
    },
    "Brazil": {
        "PETROLEUM": Resource(13.0, "billion barrels"),
        "URANIUM": Resource(0.28, "million tonnes"),
        "GOLD": Resource(2.9, "thousand tonnes"),
        "NICKEL": Resource(5.0, "million tonnes"),
        "IRON_ORE": Resource(98.0, "billion tonnes"),
        "PLATINUM": Resource(0.01, "million tonnes"),
        "BAUXITE": Resource(14.0, "million tonnes"),
        "TIN": Resource(0.08, "million tonnes"),
        "LITHIUM": Resource(0.26, "million tonnes"),
        "GRAPHITE": Resource(0.15, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.02, "million tonnes"),
        "NIOBIUM": Resource(0.1, "million tonnes"),
        "HYDROPOWER": Resource(150.0, "GW capacity"),
    },
    "Oman": {
        "PETROLEUM": Resource(5.0, "billion barrels"),
        "NATURAL_GAS": Resource(0.9, "trillion cubic meters"),
        "GOLD": Resource(0.3, "thousand tonnes"),
    },
    "United States": {
        "PETROLEUM": Resource(35.0, "billion barrels"),
        "NATURAL_GAS": Resource(12.0, "trillion cubic meters"),
        "COBALT": Resource(0.01, "million tonnes"),
        "LITHIUM": Resource(0.98, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.01, "million tonnes"),
        "GRAPHITE": Resource(0.05, "million tonnes"),
    },
    "Saudi Arabia": {
        "PETROLEUM": Resource(267.0, "billion barrels"),
        "GOLD": Resource(3.5, "thousand tonnes"),
    },
    "Somalia": {
        "PETROLEUM": Resource(0.5, "billion barrels"),  # ADDED: Small supply
        "NATURAL_GAS": Resource(0.6, "trillion cubic meters"),
        "URANIUM": Resource(0.02, "million tonnes"),
        "IRON_ORE": Resource(0.5, "billion tonnes"),
        "COPPER": Resource(0.1, "million tonnes"),
        "TIN": Resource(0.05, "million tonnes"),
        "BAUXITE": Resource(1.2, "million tonnes"),
    },
    "Bangladesh": {
        "PETROLEUM": Resource(1.0, "billion barrels"),  # ADDED: Small supply
        "NATURAL_GAS": Resource(0.2, "trillion cubic meters"),
        "COAL": Resource(3.3, "billion tonnes"),
    },
    "Germany": {
        "PETROLEUM": Resource(2.0, "billion barrels"),  # ADDED: Small supply
        "COAL": Resource(46.0, "billion tonnes"),
        "URANIUM": Resource(0.01, "million tonnes"),
        "NICKEL": Resource(0.2, "million tonnes"),
        "IRON_ORE": Resource(1.0, "billion tonnes"),
        "COPPER": Resource(0.55, "million tonnes"),
        "GRAPHITE": Resource(0.08, "million tonnes"),
    },
    "France": {
        "PETROLEUM": Resource(1.5, "billion barrels"),  # ADDED: Small supply
        "COAL": Resource(0.1, "billion tonnes"),
        "URANIUM": Resource(0.4, "million tonnes"),
        "GOLD": Resource(0.8, "thousand tonnes"),
        "IRON_ORE": Resource(2.0, "billion tonnes"),
        "BAUXITE": Resource(0.5, "million tonnes"),
        "NIOBIUM": Resource(0.02, "million tonnes"),
    },
    "Indonesia": {
        "PETROLEUM": Resource(8.0, "billion barrels"),  # ADDED: Moderate supply
        "COAL": Resource(104.0, "billion tonnes"),
        "NICKEL": Resource(13.0, "million tonnes"),
        "COPPER": Resource(0.9, "million tonnes"),
        "TIN": Resource(1.1, "million tonnes"),
        "BAUXITE": Resource(1.5, "million tonnes"),
        "COBALT": Resource(0.1, "million tonnes"),
    },
    "South Africa": {
        "PETROLEUM": Resource(3.0, "billion barrels"),  # ADDED: Small supply
        "COAL": Resource(128.0, "billion tonnes"),
        "GOLD": Resource(4.2, "thousand tonnes"),
        "NICKEL": Resource(3.5, "million tonnes"),
        "IRON_ORE": Resource(29.0, "billion tonnes"),
        "DIAMONDS": Resource(9.0, "million carats annually"),
        "COPPER": Resource(0.7, "million tonnes"),
        "COBALT": Resource(0.05, "million tonnes"),
        "PALLADIUM": Resource(0.08, "million tonnes"),
        "PLATINUM": Resource(0.06, "million tonnes"),
    },
    "Pakistan": {
        "PETROLEUM": Resource(0.8, "billion barrels"),  # ADDED: Small supply
        "COAL": Resource(3.8, "billion tonnes"),
        "GOLD": Resource(0.5, "thousand tonnes"),
        "IRON_ORE": Resource(0.4, "billion tonnes"),
        "COPPER": Resource(0.3, "million tonnes"),
    },
    "Slovakia": {
        "PETROLEUM": Resource(2.0, "billion barrels"),  # ADDED: Small supply
        "NICKEL": Resource(0.15, "million tonnes"),
        "IRON_ORE": Resource(0.8, "billion tonnes"),
        "COBALT": Resource(0.02, "million tonnes"),
    },
    "Chile": {
        "PETROLEUM": Resource(1.2, "billion barrels"),  # ADDED: Small supply
        "COPPER": Resource(18.0, "million tonnes"),
        "LITHIUM": Resource(9.0, "million tonnes"),
    },
    "Vietnam": {
        "PETROLEUM": Resource(2.5, "billion barrels"),  # ADDED: Small supply
        "TIN": Resource(0.4, "million tonnes"),
        "TUNGSTEN": Resource(0.08, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.01, "million tonnes"),
    },
    "India": {
        "PETROLEUM": Resource(5.0, "billion barrels"),  # ADDED: Moderate supply
        "BAUXITE": Resource(4.0, "million tonnes"),
        "IRON_ORE": Resource(8.0, "billion tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.01, "million tonnes"),
        "LITHIUM": Resource(0.10, "million tonnes"),
    },
    "Mozambique": {
        "PETROLEUM": Resource(1.0, "billion barrels"),  # ADDED: Small supply
        "NATURAL_GAS": Resource(3.5, "trillion cubic meters"),
        "IRON_ORE": Resource(1.2, "billion tonnes"),
        "BAUXITE": Resource(0.8, "million tonnes"),
        "NIOBIUM": Resource(0.08, "million tonnes"),
    },
    "Switzerland": {
        "PETROLEUM": Resource(0.3, "billion barrels"),  # ADDED: Tiny supply
        "HYDROPOWER": Resource(18.0, "GW capacity"),
    },
    "Sri Lanka": {
        "PETROLEUM": Resource(0.5, "billion barrels"),  # ADDED: Small supply
        "GRAPHITE": Resource(0.02, "million tonnes"),
    },
    "Kenya": {
        "PETROLEUM": Resource(0.8, "billion barrels"),  # ADDED: Small supply
        "HYDROPOWER": Resource(2.0, "GW capacity"),
    },
    "Haiti": {
        "PETROLEUM": Resource(0.2, "billion barrels"),  # ADDED: Tiny supply
    },
    "Azerbaijan": {
        "PETROLEUM": Resource(7.0, "billion barrels"),  # ADDED: Moderate supply
    },
    "Latvia": {
        "PETROLEUM": Resource(0.4, "billion barrels"),  # ADDED: Small supply
    },
    "Australia": {
        "PETROLEUM": Resource(4.0, "billion barrels"),  # ADDED: Moderate supply
    },
    "Japan": {
        "PETROLEUM": Resource(0.5, "billion barrels"),  # ADDED: Tiny supply (net importer)
    },
}


# IMPROVED: More varied petroleum demands
country_demands: dict[str, dict[str, Resource]] = {
    "Russia": {
        "LITHIUM": Resource(0.5, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.02, "million tonnes"),
        "COPPER": Resource(2.0, "million tonnes"),
    },
    "Kuwait": {
        "COAL": Resource(5.0, "billion tonnes"),
        "IRON_ORE": Resource(10.0, "billion tonnes"),
        "COPPER": Resource(1.0, "million tonnes"),
        "NICKEL": Resource(0.5, "million tonnes"),
        "LITHIUM": Resource(0.3, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.01, "million tonnes"),
    },
    "Nigeria": {
        "IRON_ORE": Resource(8.0, "billion tonnes"),
        "COPPER": Resource(1.5, "million tonnes"),
        "NICKEL": Resource(0.8, "million tonnes"),
        "LITHIUM": Resource(0.2, "million tonnes"),
        "COAL": Resource(10.0, "billion tonnes"),
    },
    "Chad": {
        "PETROLEUM": Resource(2.0, "billion barrels"),  # CHANGED: Reduced
        "IRON_ORE": Resource(2.0, "billion tonnes"),
        "COPPER": Resource(0.3, "million tonnes"),
        "COAL": Resource(3.0, "billion tonnes"),
        "NICKEL": Resource(0.1, "million tonnes"),
    },
    "Iran": {
        "NICKEL": Resource(1.0, "million tonnes"),
        "LITHIUM": Resource(0.4, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.015, "million tonnes"),
        "COAL": Resource(20.0, "billion tonnes"),
    },
    "Brazil": {
        "PETROLEUM": Resource(25.0, "billion barrels"),  # CHANGED: Reduced from 50
        "NATURAL_GAS": Resource(15.0, "trillion cubic meters"),
        "COPPER": Resource(2.0, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.05, "million tonnes"),
    },
    "Oman": {
        "PETROLEUM": Resource(3.0, "billion barrels"),  # CHANGED: Reduced
        "IRON_ORE": Resource(5.0, "billion tonnes"),
        "COPPER": Resource(0.8, "million tonnes"),
        "COAL": Resource(8.0, "billion tonnes"),
        "NICKEL": Resource(0.4, "million tonnes"),
        "LITHIUM": Resource(0.2, "million tonnes"),
    },
    "United States": {
        "PETROLEUM": Resource(60.0, "billion barrels"),  # CHANGED: Reduced from 100
        "NATURAL_GAS": Resource(20.0, "trillion cubic meters"),
        "IRON_ORE": Resource(50.0, "billion tonnes"),
        "COPPER": Resource(5.0, "million tonnes"),
        "NICKEL": Resource(2.0, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.1, "million tonnes"),
        "LITHIUM": Resource(3.0, "million tonnes"),
        "COAL": Resource(100.0, "billion tonnes"),
    },
    "Saudi Arabia": {
        "IRON_ORE": Resource(15.0, "billion tonnes"),
        "COPPER": Resource(2.0, "million tonnes"),
        "NICKEL": Resource(1.0, "million tonnes"),
        "COAL": Resource(20.0, "billion tonnes"),
        "LITHIUM": Resource(0.5, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.02, "million tonnes"),
    },
    "Somalia": {
        "PETROLEUM": Resource(3.0, "billion barrels"),  # CHANGED: Reduced from 5
        "COAL": Resource(2.0, "billion tonnes"),
        "IRON_ORE": Resource(1.0, "billion tonnes"),
    },
    "Bangladesh": {
        "PETROLEUM": Resource(6.0, "billion barrels"),  # CHANGED: Reduced from 10
        "IRON_ORE": Resource(5.0, "billion tonnes"),
        "COPPER": Resource(0.5, "million tonnes"),
        "NICKEL": Resource(0.3, "million tonnes"),
    },
    "Germany": {
        "PETROLEUM": Resource(45.0, "billion barrels"),  # CHANGED: Reduced from 80
        "NATURAL_GAS": Resource(25.0, "trillion cubic meters"),
        "IRON_ORE": Resource(40.0, "billion tonnes"),
        "COPPER": Resource(3.0, "million tonnes"),
        "LITHIUM": Resource(1.5, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.05, "million tonnes"),
        "NICKEL": Resource(1.5, "million tonnes"),
    },
    "France": {
        "PETROLEUM": Resource(35.0, "billion barrels"),  # CHANGED: Reduced from 60
        "NATURAL_GAS": Resource(20.0, "trillion cubic meters"),
        "IRON_ORE": Resource(30.0, "billion tonnes"),
        "COPPER": Resource(2.0, "million tonnes"),
        "NICKEL": Resource(1.0, "million tonnes"),
        "LITHIUM": Resource(1.0, "million tonnes"),
    },
    "Indonesia": {
        "PETROLEUM": Resource(18.0, "billion barrels"),  # CHANGED: Reduced from 30
        "IRON_ORE": Resource(20.0, "billion tonnes"),
        "COPPER": Resource(1.5, "million tonnes"),
        "LITHIUM": Resource(0.4, "million tonnes"),
    },
    "South Africa": {
        "PETROLEUM": Resource(22.0, "billion barrels"),  # CHANGED: Reduced from 40
        "NATURAL_GAS": Resource(10.0, "trillion cubic meters"),
        "COPPER": Resource(2.0, "million tonnes"),
        "LITHIUM": Resource(0.8, "million tonnes"),
    },
    "Pakistan": {
        "PETROLEUM": Resource(15.0, "billion barrels"),  # CHANGED: Reduced from 25
        "NATURAL_GAS": Resource(8.0, "trillion cubic meters"),
        "IRON_ORE": Resource(10.0, "billion tonnes"),
        "NICKEL": Resource(0.5, "million tonnes"),
    },
    "Slovakia": {
        "PETROLEUM": Resource(8.0, "billion barrels"),  # CHANGED: Reduced from 15
        "NATURAL_GAS": Resource(5.0, "trillion cubic meters"),
        "COPPER": Resource(1.0, "million tonnes"),
        "LITHIUM": Resource(0.3, "million tonnes"),
    },
    "Chile": {
        "PETROLEUM": Resource(12.0, "billion barrels"),  # CHANGED: Reduced from 20
        "NATURAL_GAS": Resource(8.0, "trillion cubic meters"),
        "COAL": Resource(15.0, "billion tonnes"),
        "IRON_ORE": Resource(10.0, "billion tonnes"),
    },
    "Vietnam": {
        "PETROLEUM": Resource(10.0, "billion barrels"),  # CHANGED: Reduced from 18
        "IRON_ORE": Resource(12.0, "billion tonnes"),
        "COPPER": Resource(1.0, "million tonnes"),
        "NICKEL": Resource(0.6, "million tonnes"),
        "LITHIUM": Resource(0.3, "million tonnes"),
    },
    "India": {
        "PETROLEUM": Resource(80.0, "billion barrels"),  # CHANGED: Reduced from 150
        "NATURAL_GAS": Resource(40.0, "trillion cubic meters"),
        "COAL": Resource(200.0, "billion tonnes"),
        "IRON_ORE": Resource(50.0, "billion tonnes"),
        "COPPER": Resource(4.0, "million tonnes"),
        "NICKEL": Resource(2.0, "million tonnes"),
        "LITHIUM": Resource(2.0, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.05, "million tonnes"),
    },
    "Mozambique": {
        "PETROLEUM": Resource(5.0, "billion barrels"),  # CHANGED: Reduced from 8
        "COAL": Resource(10.0, "billion tonnes"),
        "IRON_ORE": Resource(5.0, "billion tonnes"),
        "COPPER": Resource(0.4, "million tonnes"),
    },
    "Switzerland": {
        "PETROLEUM": Resource(6.0, "billion barrels"),  # CHANGED: Reduced from 10
        "NATURAL_GAS": Resource(5.0, "trillion cubic meters"),
        "IRON_ORE": Resource(8.0, "billion tonnes"),
        "COPPER": Resource(0.5, "million tonnes"),
        "LITHIUM": Resource(0.2, "million tonnes"),
    },
    "Sri Lanka": {
        "PETROLEUM": Resource(7.0, "billion barrels"),  # CHANGED: Reduced from 12
        "COAL": Resource(8.0, "billion tonnes"),
        "IRON_ORE": Resource(4.0, "billion tonnes"),
        "COPPER": Resource(0.3, "million tonnes"),
    },
    "Kenya": {
        "PETROLEUM": Resource(9.0, "billion barrels"),  # CHANGED: Reduced from 15
        "COAL": Resource(12.0, "billion tonnes"),
        "IRON_ORE": Resource(6.0, "billion tonnes"),
        "COPPER": Resource(0.5, "million tonnes"),
    },
    "Haiti": {
        "PETROLEUM": Resource(3.0, "billion barrels"),  # CHANGED: Reduced from 5
        "COAL": Resource(3.0, "billion tonnes"),
        "IRON_ORE": Resource(2.0, "billion tonnes"),
    },
    "Azerbaijan": {
        "PETROLEUM": Resource(5.0, "billion barrels"),  # CHANGED: Reduced (was no demand)
        "IRON_ORE": Resource(10.0, "billion tonnes"),
        "COPPER": Resource(1.0, "million tonnes"),
        "NICKEL": Resource(0.5, "million tonnes"),
        "LITHIUM": Resource(0.2, "million tonnes"),
    },
    "Latvia": {
        "PETROLEUM": Resource(5.0, "billion barrels"),  # CHANGED: Reduced from 8
        "NATURAL_GAS": Resource(3.0, "trillion cubic meters"),
        "IRON_ORE": Resource(5.0, "billion tonnes"),
        "COPPER": Resource(0.3, "million tonnes"),
    },
    "Australia": {
        "PETROLEUM": Resource(18.0, "billion barrels"),  # CHANGED: Reduced from 30
        "LITHIUM": Resource(5.0, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.03, "million tonnes"),
    },
    "Japan": {
        "PETROLEUM": Resource(55.0, "billion barrels"),  # CHANGED: Reduced from 100
        "NATURAL_GAS": Resource(30.0, "trillion cubic meters"),
        "COAL": Resource(80.0, "billion tonnes"),
        "IRON_ORE": Resource(60.0, "billion tonnes"),
        "COPPER": Resource(3.0, "million tonnes"),
        "NICKEL": Resource(2.0, "million tonnes"),
        "LITHIUM": Resource(2.0, "million tonnes"),
        "RARE_EARTH_ELEMENTS": Resource(0.08, "million tonnes"),
        "URANIUM": Resource(0.3, "million tonnes"),
    },
}
