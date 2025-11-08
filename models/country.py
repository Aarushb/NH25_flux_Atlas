from dataclasses import dataclass, field
from typing import Dict, Optional
from resource import Resource


@dataclass
class Country:
    """Represents a country with its name, PPP value, budget, and resources."""
    name: str
    ppp: int
    budget: float = 0.0
    resources: Dict[str, Resource] = field(default_factory=dict)
    
    def __post_init__(self):
        """After initialization, load resources for this country from country_data."""
        from country_data import country_resources
        
        # Get resources for this country and assign them
        if self.name in country_resources:
            self.resources = country_resources[self.name].copy()
    
    def get_resource(self, resource_name: str) -> Optional[Resource]:
        """Get a specific resource by name."""
        return self.resources.get(resource_name)
    
    def has_resource(self, resource_name: str) -> bool:
        """Check if country has a specific resource."""
        return resource_name in self.resources
    
    def __repr__(self) -> str:
        return f"Country(name='{self.name}', ppp={self.ppp}, budget=${self.budget:.2f}B, resources={len(self.resources)})"



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

