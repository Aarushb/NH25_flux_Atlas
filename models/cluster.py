
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

from country import Country



@dataclass
class ClusterInfo:
    """Represents a K-means cluster with metadata."""
    name: str
    countries: List[Country]
    min_ppp: int
    max_ppp: int
    budget: float = 0.0
    auction_quantity: Optional[float] = None
    
    def __post_init__(self):
        """After initialization, calculate and assign budgets to all countries."""
        self.assign_country_budgets()
    
    @property
    def avg_ppp(self) -> float:
        """Calculate average PPP from countries in cluster."""
        if not self.countries:
            return 0
        return sum(c.ppp for c in self.countries) / len(self.countries)
    
    @property
    def total_ppp(self) -> float:
        """Calculate total PPP for all countries in cluster."""
        return sum(c.ppp for c in self.countries)

    @property
    def country_count(self) -> int:
        """Get number of countries in this cluster."""
        return len(self.countries)

    def assign_country_budgets(self) -> None:
        """Calculate and assign budget to each country in this cluster."""
        cluster_total_ppp = self.total_ppp
        
        if cluster_total_ppp == 0:
            return
        
        for country in self.countries:
            country.budget = (country.ppp / cluster_total_ppp) * self.budget
    
    def calculate_country_budgets(self) -> Dict[str, float]:
        """
        Calculate budget allocation for each country in this cluster.
        Formula: country_budget = (country_ppp / cluster_total_ppp) * cluster_budget
        """
        if self.total_ppp == 0:
            return {country.name: 0.0 for country in self.countries}
        
        country_budgets = {}
        for country in self.countries:
            country_budget = (country.ppp / self.total_ppp) * self.budget
            country_budgets[country.name] = country_budget
        
        return country_budgets
    
    def assign_auction_quantity(self, total_quantity: float, total_clusters: int = 6) -> None:
        """
        Calculate and assign the auction quantity for this cluster.
        Called when an auction starts.
        
        
        Args:
            total_quantity: Total resource quantity to distribute
            total_clusters: Total number of clusters (default: 6)
        """
        self.auction_quantity = (total_quantity / total_clusters) * self.country_count
        

    

