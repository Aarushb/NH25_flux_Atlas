from dataclasses import dataclass, field
from typing import Dict, Optional
from resource import Resource
from country_data import country_resources, country_demands



@dataclass
class Country:
    """Represents a country with its name, PPP value, budget, and resources."""
    name: str
    ppp: int
    budget: float = 0.0
    resources: Dict[str, Resource] = field(default_factory=dict) #supply
    demand: Dict[str,Resource] = field(default_factory=dict) #demand
    
    def __post_init__(self):
        """After initialization, load resources for this country from country_data."""
                
        # Get resources for this country and assign them
        if self.name in country_resources:
            self.resources = country_resources[self.name].copy()

        if self.name in country_demands:
            self.demand = country_demands[self.name].copy()
    
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
        
        if demand_amount == 0:
            status = "NO_DEMAND"
        elif supply_amount == 0:
            status = "NO_SUPPLY"
        elif gap > 0:
            status = "SURPLUS"  # Can export
        elif gap < 0:
            status = "DEFICIT"  # Needs to import
        else:
            status = "BALANCED"
        
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
    russia = Country("Russia", 47405)
    print(russia)
    print(f"Has PETROLEUM: {russia.has_resource('PETROLEUM')}")
    print(f"PETROLEUM amount: {russia.get_resource('PETROLEUM')}")
    print(f"GOLD amount: {russia.get_resource('GOLD')}")
    print("\nAll Russia's resources:")
    for resource_name, resource in russia.resources.items():
        print(f"  {resource_name}: {resource}")
    
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

