from typing import Dict

from enum import Enum

Group1 = {"Somalia": 1601, "Mozambique": 1700, "Chad": 2962}

Group2 = {
    "Pakistan": 6287,
    "Nigeria": 6440,
    "Kenya": 6619,
    "Vietnam": 6805,
    "Bangladesh": 9647,
}

Group3 = {"India": 11159, "South Africa": 15457, "Sri Lanka": 15633, "Indonesia": 16448}

Group4 = {"Iran": 18442, "Brazil": 22333, "China": 27105}

Group5 = {
    "Chile": 34637,
    "Oman": 41664,
    "Latvia": 43867,
    "Slovakia": 47181,
    "Russia": 47405,
    "Kuwait": 51636,
    "Japan": 51685,
}

Group6 = {
    "France": 61322,
    "Saudi Arabia": 71243,
    "Germany": 72300,
    "United States": 85810,
    "Swtizerland": 83819,
    "Luxembourg": 150772,
}


def cluster(gno: Dict[str, int]) -> Dict:
    return gno


class GlobalResources(Enum):
    """
    An enumeration of all natural resources, minerals, commodities,
    and energy types mentioned in the comparative analysis report.
    """

    # -- MINERALS, METALS, & ELEMENTS --
    BAUXITE = auto()
    BENTONITE = auto()
    BERYLLIUM = auto()
    BISMUTH = auto()
    BORON = auto()
    BROMINE = auto()
    CADMIUM = auto()
    CEMENT = auto()
    CHROMITE = auto()
    CHROMIUM = auto()
    CLAY = auto()
    CLAYS = auto()
    COBALT = auto()
    COLUMBITE = auto()
    COPPER = auto()
    DIAMONDS = auto()
    DIATOMITE = auto()
    DOLOMITE = auto()
    FELDSPAR = auto()
    FLUORSPAR = auto()
    GALLIUM = auto()
    GARNET = auto()
    GEMSTONES = auto()
    GOLD = auto()
    GRAPHITE = auto()
    GRAVEL = auto()
    GYPSUM = auto()
    ILMENITE = auto()
    INDIUM = auto()
    IODINE = auto()
    IRIDIUM = auto()
    IRON = auto()
    IRON_ORE = auto()
    IRON_OXIDE_PIGMENTS = auto()
    KAOLIN = auto()
    KAOLINITE = auto()
    LEAD = auto()
    LIME = auto()
    LIMESTONE = auto()
    LITHIUM = auto()
    MAGNESIUM = auto()
    MANGANESE = auto()
    MARBLE = auto()
    MERCURY = auto()
    MICA = auto()
    MINERAL_SANDS = auto()
    MOLYBDENUM = auto()
    NATRON = auto()
    NICKEL = auto()
    NIOBIUM = auto()
    NITROGEN = auto()
    PALLADIUM = auto()
    PHOSPHATE_ROCK = auto()
    PHOSPHATES = auto()
    PIG_IRON = auto()
    PLATINUM = auto()
    PLATINUM_GROUP_METALS = auto()
    POTASH = auto()
    PUMICE = auto()
    QUARTZ = auto()
    RARE_EARTH_ELEMENTS = auto()
    REFINED_SELENIUM = auto()
    RHENIUM = auto()
    RHODIUM = auto()
    RUBIES = auto()
    RUTHENIUM = auto()
    RUTILE = auto()
    SALT = auto()
    SAND = auto()
    SELENIUM = auto()
    SILICON = auto()
    SILVER = auto()
    SODA_ASH = auto()
    STONE = auto()
    SULFUR = auto()
    TALC = auto()
    TANTALUM = auto()
    TELLURIUM = auto()
    THORIUM = auto()
    TIN = auto()
    TITANIUM = auto()
    TITANIUM_MINERALS = auto()
    TOURMALINES = auto()
    TUNGSTEN = auto()
    URANIUM = auto()
    VANADIUM = auto()
    VERMICULITE = auto()
    ZEOLITES = auto()
    ZINC = auto()
    ZIRCONIUM = auto()

    # -- ENERGY RESOURCES --
    BIOENERGY = auto()
    BIOMASS = auto()
    BIOMASS_AND_WASTE = auto()
    BROWN_COAL = auto()
    COAL = auto()
    CRUDE_PETROLEUM = auto()
    GEOTHERMAL = auto()
    GREEN_HYDROGEN = auto()
    HYDROPOWER = auto()
    LIGNITE = auto()
    LIQUEFIED_NATURAL_GAS = auto()
    MINERAL_FUELS = auto()
    NATURAL_GAS = auto()
    NUCLEAR = auto()
    OFFSHORE_WIND = auto()
    OIL = auto()
    ONSHORE_WIND = auto()
    PEAT = auto()
    PETROLEUM = auto()
    PETROLEUM_GAS = auto()
    REFINED_PETROLEUM = auto()
    SOLAR = auto()
    SOLAR_PV = auto()
    WIND = auto()
