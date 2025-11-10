from dataclasses import dataclass, field
from typing import Dict, Optional
import sys
try:
    from .resourcess import Resource
    from .country_data import country_resources, country_demands
# Fall back to direct imports for when running this file as a script
except ImportError:
    from resourcess import Resource
    from country_data import country_resources, country_demands
import requests
import json




@dataclass
class Country:
    """Represents a country with its name, PPP value, budget, and resources."""
    name: str
    ppp: int
    budget: float = 0.0
    id: str|None=None
    resources: Dict[str, Resource] = field(default_factory=dict) #supply
    demand: Dict[str,Resource] = field(default_factory=dict) #demand
    
    def __post_init__(self):
        """After initialization, load resources and budget from API."""
        # Get country ID from API
        self.get_country_id()
        
        # Load resources and demands from API instead of hardcoded data
        if self.id:
            self._load_resources_from_api()
            self._load_budget_from_api()
        else:
            print(f"Warning: Could not load data for {self.name} - ID not found")
    def get_country_id(self, api_base_url: str = "http://localhost:8000") -> Optional[str]:
        """Fetch country ID from API by matching country name."""
        if self.id:
            return self.id
            
        endpoint = f"{api_base_url}/countries"
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            
            countries_list = response.json()
            for country_data in countries_list:
                # Match by 'cname' field
                if country_data.get('cname', '').lower() == self.name.lower():
                    found_id = country_data.get('id')
                    if found_id:
                        self.id = found_id
                        return self.id
            
            print(f"Country '{self.name}' not found in API.", file=sys.stderr)
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching country ID for '{self.name}': {e}", file=sys.stderr)
            return None
    def _load_budget_from_api(self, api_base_url: str = "http://localhost:8000") -> None:
        """Load country budget from API using carbon_budget field."""
        try:
            response = requests.get(f"{api_base_url}/countries/{self.id}")
            response.raise_for_status()
            
            country_data = response.json()
            # Use carbon_budget from API as the country's budget
            self.budget = country_data.get('carbon_budget', 0.0) or 0.0
            
        except requests.RequestException as e:
            print(f"Error loading budget for {self.name}: {e}", file=sys.stderr)
            self.budget = 0.0

    def _load_resources_from_api(self, api_base_url: str = "http://localhost:8000") -> None:
        """Load country resources (supply and demand) from API."""
        try:
            response = requests.get(f"{api_base_url}/countries/{self.id}/resources")
            response.raise_for_status()
            
            country_resources_list = response.json()
            
            for cr in country_resources_list:
                resource_id = cr.get('resource_id')
                supply = cr.get('supply', 0)
                demand = cr.get('demand', 0)
                quantity = cr.get('quantity', 0.0)
                unit = cr.get('unit', 'units')
                
                # Get resource name from resource_id
                resource_name = self._get_resource_name(resource_id, api_base_url)
                if not resource_name:
                    continue
                
                # Add to supply resources if supply > 0
                if supply and supply > 0:
                    self.resources[resource_name] = Resource(float(quantity), unit)
                
                # Add to demand resources if demand > 0
                if demand and demand > 0:
                    self.demand[resource_name] = Resource(float(demand), unit)
                    
        except requests.RequestException as e:
            print(f"Error loading resources for {self.name}: {e}", file=sys.stderr)

    def _get_resource_name(self, resource_id: str, api_base_url: str = "http://localhost:8000") -> Optional[str]:
        """Get resource name from resource ID."""
        try:
            response = requests.get(f"{api_base_url}/resources/{resource_id}")
            response.raise_for_status()
            resource_data = response.json()
            return resource_data.get('rname')
        except requests.RequestException:
            return None
    def get_resource(self, resource_name: str) -> Optional[Resource]:
        """Get a specific resource by name."""
        return self.resources.get(resource_name)        
        
    def has_resource(self, resource_name: str) -> bool:
        """Check if country has a specific resource."""
        return resource_name in self.resources

    def get_demand(self, resource_name: str) -> Optional[Resource]:
        """Get demand for a specific resource."""
        return self.demand.get(resource_name)

    def has_demand(self, resource_name: str) -> bool:
        """Check if country has demand for a specific resource."""
        return resource_name in self.demand

    def get_supply_demand_gap(self, resource_name: str) -> Dict:
        """
        Calculate supply vs demand gap for a specific resource.
        
        Returns:
            Dictionary with supply, demand, gap, and status
        """
        supply = self.resources.get(resource_name)
        demand = self.demand.get(resource_name)
        
        supply_amount = supply.amount if supply else 0.0
        demand_amount = demand.amount if demand else 0.0
        
        gap = supply_amount - demand_amount
        
        status = ""
        
        # --- START OF BUG FIX ---
        # The logic must check for surplus/deficit *first*
        # to correctly identify export/import opportunities.
        
        if gap > 0:
            status = "SURPLUS"  # Can export (e.g., Supply=80, Demand=0)
        elif gap < 0:
            status = "DEFICIT"  # Needs to import (e.g., Supply=0, Demand=50)
        else: # gap == 0
            status = "BALANCED" # Supply == Demand (or both are 0)
        
        # --- END OF BUG FIX ---
        
        return {
            "resource": resource_name,
            "supply": supply_amount,
            "demand": demand_amount,
            "gap": gap,
            "status": status,
            "unit": supply.unit if supply else (demand.unit if demand else "unknown")
        }

    def get_all_supply_demand_analysis(self) -> Dict[str, Dict]:
        """Get supply/demand analysis for all resources this country has or needs."""
        all_resources = set(self.resources.keys()) | set(self.demand.keys())
        
        analysis = {}
        for resource_name in all_resources:
            analysis[resource_name] = self.get_supply_demand_gap(resource_name)
        
        return analysis

    def get_export_resources(self) -> list[str]:
        """Get list of resources this country can export (surplus)."""
        return [res for res, data in self.get_all_supply_demand_analysis().items() 
                if data["status"] == "SURPLUS"]

    def get_import_needs(self) -> list[str]:
        """Get list of resources this country needs to import (deficit)."""
        return [res for res, data in self.get_all_supply_demand_analysis().items() 
                if data["status"] == "DEFICIT"]

    def __repr__(self) -> str:
        return f"Country(name='{self.name}', ppp={self.ppp}, budget=${self.budget:.2f}B, resources={len(self.resources)}, demand={len(self.demand)})"



if __name__ == "__main__":
    # Test creating countries and their resources
    print("Testing Country class with automatic resource loading:\n")
    
    # Test Russia
    russia = Country("russia", 47405)
    print(russia.get_country_id())
    print(russia)
    print(f"Has PETROLEUM: {russia.has_resource('PETROLEUM')}")
    print(f"PETROLEUM amount: {russia.get_resource('PETROLEUM')}")
    print(f"GOLD amount: {russia.get_resource('GOLD')}")
    print("\nAll Russia's resources:")
    for resource_name, resource in russia.resources.items():
        print(f"  {resource_name}: {resource}")
        
    print("\n--- Testing Gap Analysis (Bug Fix) ---")
    russia_analysis = russia.get_all_supply_demand_analysis()
    print(f"  Russia PETROLEUM Gap: {russia_analysis.get('PETROLEUM')}")
    print(f"  Russia LITHIUM Gap: {russia_analysis.get('LITHIUM')}")
    print(f"  Russia Exports: {russia.get_export_resources()}")
    print(f"  Russia Imports: {russia.get_import_needs()}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Somalia
    somalia = Country("Somalia", 1601)
    print(somalia)
    print("\nSomalia's resources:")
    for resource_name, resource in somalia.resources.items():
        print(f"  {resource_name}: {resource}")
    
    print("\n" + "="*50 + "\n")
    
    # Test a country with no resources
    haiti = Country("Haiti", 3183)
    print(haiti)
    print(f"Haiti has resources: {len(haiti.resources) > 0}")
    print(f"  Haiti Imports: {haiti.get_import_needs()}")
