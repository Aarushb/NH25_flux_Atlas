from enum import Enum
from models.cluster import ClusterInfo
from models.country import Country


class CountryClusters(Enum):
    """K-means clustering results based on PPP values."""
    
    GROUP1 = ClusterInfo(
        name="Emerging Markets - Low PPP",
        countries=[
            Country("Somalia", 1601),
            Country("Mozambique", 1700),
            Country("Chad", 2962),
            Country("Haiti",3183),
        ],
        min_ppp=1601,
        max_ppp=3183
    )
    
    GROUP2 = ClusterInfo(
        name="Developing Nations",
        countries=[
            Country("Pakistan", 6287),
            Country("Nigeria", 6440),
            Country("Kenya", 6619),
            Country("Bangladesh", 9647),
        ],
        min_ppp=6287,
        max_ppp=9647
    )
    
    GROUP3 = ClusterInfo(
        name="Lower-Middle Income",
        countries=[
            Country("India", 11159),
            Country("South Africa", 15457),
            Country("Sri Lanka", 15633),
            Country("Indonesia", 16448),
            Country("Vietnam", 16386),

        ],
        min_ppp=11159,
        max_ppp=16386
    )
    
    GROUP4 = ClusterInfo(
        name="Upper-Middle Income",
        countries=[
            Country("Iran", 18442),
            Country("Brazil", 22333),
            Country("China", 27105),
             Country("Azerbaijan", 25089),

        ],
        min_ppp=18442,
        max_ppp=27105
    )
    
    GROUP5 = ClusterInfo(
        name="High-Income Nations",
        countries=[
            Country("Chile", 34637),
            Country("Oman", 41664),
            Country("Latvia", 43867),
            Country("Slovakia", 47181),
            Country("Russia", 47405),
            Country("Kuwait", 51636),
            Country("Japan", 51685),
        ],
        min_ppp=34637,
        max_ppp=51685
    )
    
    GROUP6 = ClusterInfo(
        name="Developed Economies - High PPP",
        countries=[
            Country("France", 61322),
            Country("Saudi Arabia", 71243),
            Country("Germany", 72300),
            Country("United States", 85810),
            Country("Switzerland", 83819),
            Country("Australia", 71193),
        ],
        min_ppp=61322,
        max_ppp=85810
    )
