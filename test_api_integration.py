from models.country import Country
from models.cluster import ClusterInfo
from auction.auction import Auction

# Test 1: Create country from API
print("=== Test 1: Country from API ===")
usa = Country("United States", ppp=0)  # PPP and resources loaded from API
print(f"USA ID: {usa.id}")
print(f"USA Budget: ${usa.budget}B")
print(f"USA Resources: {list(usa.resources.keys())}")
print(f"USA Demands: {list(usa.demand.keys())}")

# Test 2: Create cluster from group_id
print("\n=== Test 2: Cluster from API ===")
# First get a group_id from your API (use Swagger or PowerShell)
# Example: group_id = "your-uuid-here"
# cluster = ClusterInfo.from_group_id(group_id)
# print(f"Cluster: {cluster.name}")
# print(f"Countries in cluster: {[c.name for c in cluster.countries]}")

# Test 3: Create auction from country name
print("\n=== Test 3: Auction from API ===")
auction = Auction.from_country_name(
    seller_name="United States",
    resource_name="Lithium",
    quantity=100.0,
    asking_price_per_unit=250.0,
    current_market_price=200.0
)
print(f"Auction: {auction}")
print(f"Seller: {auction.seller.name} (ID: {auction.seller.id})")