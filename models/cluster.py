from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .country import Country


@dataclass
class ClusterInfo:
    """Represents a K-means cluster with metadata."""
    name: str
    countries: List[Country]
    min_ppp: int
    max_ppp: int
    budget: float = 0.0
    auction_quantity: Optional[float] = None
    auction_batches: Dict[int, float] = field(default_factory=dict)  # Store batches here
    
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
        Also automatically calculates and stores batch quantities.
        Called when an auction starts.
        
        Args:
            total_quantity: Total resource quantity to distribute
            total_clusters: Total number of clusters (default: 6)
        """
        self.auction_quantity = (total_quantity / total_clusters) * self.country_count
        
        # Automatically calculate and store batches
        self._calculate_and_store_batches()
    
    def _calculate_and_store_batches(self) -> None:
        """
        Internal method to calculate and store batch quantities.
        Divides auction_quantity into n-1 batches where n = number of countries.
        
        Formula:
        - Batch 1: quantity / 2
        - Batch 2: remaining / 2
        - Batch 3: remaining / 2
        - ...
        - Batch n-1: all remaining
        """
        if self.auction_quantity is None:
            return
        
        num_batches = self.country_count - 1
        
        if num_batches <= 0:
            # Edge case: only 1 country, all quantity in batch 1
            self.auction_batches = {1: self.auction_quantity}
            return
        
        self.auction_batches = {}
        remaining_quantity = self.auction_quantity
        
        for batch_num in range(1, num_batches + 1):
            if batch_num == num_batches:
                # Last batch gets all remaining quantity
                self.auction_batches[batch_num] = remaining_quantity
            else:
                # Current batch gets half of remaining
                batch_quantity = remaining_quantity / 2
                self.auction_batches[batch_num] = batch_quantity
                remaining_quantity -= batch_quantity
    
    def get_batch_quantity(self, batch_num: int) -> Optional[float]:
        """
        Get the quantity for a specific batch number.
        
        Args:
            batch_num: Batch number (1-indexed)
            
        Returns:
            Batch quantity or None if batch doesn't exist
        """
        return self.auction_batches.get(batch_num)
    
    def get_num_batches(self) -> int:
        """Get the total number of batches."""
        return len(self.auction_batches)
    
    def get_batch_summary(self) -> Dict:
        """
        Get a summary of all batch allocations.
        
        Returns:
            Dictionary with batch allocation details
        """
        if not self.auction_batches:
            return {
                "cluster_name": self.name,
                "error": "No batches calculated. Call assign_auction_quantity() first."
            }
        
        return {
            "cluster_name": self.name,
            "total_quantity": self.auction_quantity,
            "num_countries": self.country_count,
            "num_batches": len(self.auction_batches),
            "batches": self.auction_batches.copy(),
            "batch_percentages": {
                batch_num: (qty / self.auction_quantity) * 100
                for batch_num, qty in self.auction_batches.items()
            }
        }
