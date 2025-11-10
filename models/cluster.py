import requests
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
@classmethod
def from_group_id(cls, group_id: str, api_base_url: str = "http://localhost:8000") -> 'ClusterInfo':
    """
    Create ClusterInfo from a group ID by fetching data from API.
    
    Args:
        group_id: UUID of the group
        api_base_url: Base URL of the API
    
    Returns:
        ClusterInfo instance with data from API
    """
    try:
        # Get group details
        group_response = requests.get(f"{api_base_url}/groups/{group_id}")
        group_response.raise_for_status()
        group_data = group_response.json()
        
        # Get all countries in this group
        all_countries_response = requests.get(f"{api_base_url}/countries")
        all_countries_response.raise_for_status()
        all_countries = all_countries_response.json()
        
        # Filter countries by group_id
        group_countries = [c for c in all_countries if c.get('group_id') == group_id]
        
        # Create Country objects
        from .country import Country
        country_objects = []
        for c_data in group_countries:
            country = Country(
                name=c_data['cname'],
                ppp=c_data.get('ppp', 0),
                budget=c_data.get('carbon_budget', 0.0) or 0.0,
                id=c_data['id']
            )
            country_objects.append(country)
        
        # Create ClusterInfo
        return cls(
            name=group_data['name'],
            countries=country_objects,
            min_ppp=group_data.get('low_ppp', 0),
            max_ppp=group_data.get('high_ppp', 0),
            budget=0.0  # Will be calculated
        )
        
    except requests.RequestException as e:
        print(f"Error creating cluster from group {group_id}: {e}", file=sys.stderr)
        return None
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
    
    def assign_auction_quantity(self, total_auction_quantity: float, total_countries_in_world: int, seller: Country = None) -> None:
        """
        Calculate and assign the auction quantity for this cluster based on its
        proportional share of the total world countries.
        
        Args:
            total_auction_quantity: Total resource quantity to distribute (e.g., 50.0)
            total_countries_in_world: The sum of countries in all clusters (e.g., 30)
            seller (Optional): The country selling. This is used to calculate n-1 batches.
        """
        if total_countries_in_world == 0:
            self.auction_quantity = 0.0
        else:
            # --- THIS IS THE FIXED FORMULA (WEIGHTED DISTRIBUTION) ---
            # (Cluster Country Count / Total World Countries) * Total Quantity
            proportional_share = float(self.country_count) / float(total_countries_in_world)
            self.auction_quantity = total_auction_quantity * proportional_share
        
        # Automatically calculate and store batches based on this new quantity
        self._calculate_and_store_batches(seller)
    
    def _calculate_and_store_batches(self, seller: Country = None) -> None:
        """
        Internal method to calculate and store batch quantities.
        Divides auction_quantity into n-1 batches where n = number of *potential bidders*.
        """
        if self.auction_quantity is None or self.auction_quantity == 0:
            self.auction_batches = {}
            return
        
        # --- [THIS IS THE FIX] ---
        # 'n' is the number of countries, *excluding* the seller if they are in this cluster.
        n = self.country_count
        if seller and seller in self.countries:
            n -= 1 # Do not count the seller in 'n'
            
        # num_batches is (n-1), where n is potential bidders.
        # Use max(1, ...) to avoid num_batches = 0.
        num_batches = max(1, n - 1)
        
        if n <= 1:
            # Edge case: only 1 potential bidder (or 0), all quantity in batch 1
            self.auction_batches = {1: self.auction_quantity}
            return
        
        self.auction_batches = {}
        remaining_quantity = self.auction_quantity
        
        for batch_num in range(1, num_batches + 1):
            if batch_num == num_batches:
                # Last batch gets all remaining quantity
                self.auction_batches[batch_num] = remaining_quantity
                remaining_quantity = 0.0
            else:
                # Current batch gets half of remaining
                batch_quantity = remaining_quantity / 2.0
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
        
        # Avoid division by zero if total_quantity is 0
        total_qty_safe = self.auction_quantity if self.auction_quantity > 0 else 1.0
        
        return {
            "cluster_name": self.name,
            "total_quantity": self.auction_quantity,
            "num_countries": self.country_count,
            "num_batches": len(self.auction_batches),
            "batches": self.auction_batches.copy(),
            "batch_percentages": {
                batch_num: (qty / total_qty_safe) * 100
                for batch_num, qty in self.auction_batches.items()
            }
        }
