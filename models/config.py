from typing import Dict
from pydantic import BaseModel, Field, ValidationError
from pydantic import field_validator
from enum import Enum, auto

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


from dataclasses import dataclass


@dataclass
class Resource:
    """Represents a natural resource with its quantity and unit of measurement."""

    amount: float
    unit: str
