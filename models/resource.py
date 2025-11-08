from dataclasses import dataclass


@dataclass
class Resource:
    amount: float
    unit: str

    def __repr__(self) -> str:
        return f"{self.amount} {self.unit}"


class GlobalResources(str):
    """
    String-based class for all natural resources, minerals, commodities,
    and energy types mentioned in the comparative analysis report.
    """

    PETROLEUM = "PETROLEUM"
    NATURAL_GAS = "NATURAL_GAS"
    COAL = "COAL"
    URANIUM = "URANIUM"
    GOLD = "GOLD"
    NICKEL = "NICKEL"
    IRON_ORE = "IRON_ORE"
    DIAMONDS = "DIAMONDS"
    COPPER = "COPPER"
    TIN = "TIN"
    BAUXITE = "BAUXITE"
    COBALT = "COBALT"
    LITHIUM = "LITHIUM"
    GRAPHITE = "GRAPHITE"
    PALLADIUM = "PALLADIUM"
    PLATINUM = "PLATINUM"
    TUNGSTEN = "TUNGSTEN"
    NIOBIUM = "NIOBIUM"
    HYDROPOWER = "HYDROPOWER"
    RARE_EARTH_ELEMENTS = "RARE_EARTH_ELEMENTS"
