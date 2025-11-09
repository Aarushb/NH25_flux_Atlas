import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import math  # <-- FIX 1: Import math
from models.cluster_enums import CountryClusters
from models.resourcess import Resource
from models.country import Country
from models.cluster import ClusterInfo  
from auction import AuctionStatus, Bid, Auction 



@dataclass
# class AuctionManager(Enum):     # <-- FIX 4: This should not be an Enum
class AuctionManager:
    cluster: ClusterInfo
    auctions: List[Auction] = field(default_factory=list)
    
    # FIX 5: This should be a staticmethod to be called without an instance
    @staticmethod
    # FIX 6: The method signature was invalid. Use simple types.
    def laplace(base_price: float, supply: float, demand: float, quantity:float, min_b:int=1 , min_w:int=0.0001, k:int=0.1):
        # 1. Handle invalid base price
        if base_price <= 0:
            raise ValueError("Base price must be > 0")
    
        # 2. Avoid division by zero
        if supply <= 0:
            max_increase = 1
        else:
            # Note: This logic might be flawed if demand < supply
            max_increase = min(1, (demand/supply)-1)
         
        # 3. Compute b, ensure it never hits zero
        b = max(abs(demand) * k, float(min_b))
    
        # 4. Distance from ideal offer
        # FIX 7: 'market_offer' was undefined. I've added it to the method arguments.
        # NEW
        distance = abs(quantity - demand)
    
        # 5. Laplace decay weight
        w = math.exp(- distance / b)
    
        # 6. Compute final adjusted value
        multiplier = 1.0 + max_increase * w
        v = base_price * multiplier
    
        # 7. Threshold accept/reject
        if w < min_w or v < base_price:
            return v, False
        return v, True


    










if __name__ == "__main__":
    print("="*70)
    print("LAPLACE FOR ONE COUNTRY, ONE QUANTITY")
    print("="*70)
    
    # Get cluster
    cluster = CountryClusters.GROUP5.value
    
    # Assign auction quantity (batches auto-calculated)
    cluster.assign_auction_quantity(total_quantity=100.0, total_clusters=6)
    
    print(f"\n📦 Batches in cluster.auction_batches:")
    for batch_num, quantity in cluster.auction_batches.items():
        print(f"   Batch {batch_num}: {quantity:.2f} units")
    
    # --- START OF FIX ---
    
    # Get the BIDDER country (Japan)
    japan = next(c for c in cluster.countries if c.name == "Japan")
    
    # Get Japan's internal supply (which is 0)
    japan_supply_res = japan.get_resource("PETROLEUM")
    supply = japan_supply_res.amount if japan_supply_res else 0.0
    
    # Get Japan's internal demand (which is 100)
    japan_demand_res = japan.get_demand("PETROLEUM")
    demand = japan_demand_res.amount if japan_demand_res else 0.0
    
    if demand == 0.0:
        print("Error: Japan has no demand data for PETROLEUM")
        sys.exit(1)

    # --- END OF FIX ---
    
    # Get one batch quantity
    batch_1_quantity = cluster.auction_batches[1]
    
    print(f"\n📊 Parameters (for Japan as Bidder):")
    print(f"   Supply (Japan's Internal):  {supply:.2f} billion barrels")
    print(f"   Demand (Japan's Internal):  {demand:.2f} billion barrels")
    print(f"   Quantity (Batch 1): {batch_1_quantity:.2f} billion barrels")
    print(f"   Base Price:       $0.5B per unit")
    
    # Create manager
    manager = AuctionManager(cluster)
    
    # Apply Laplace for one country, one quantity
    print("\n" + "="*70)
    print("APPLYING LAPLACE")
    print("="*70)
    
    adjusted_price, accepted = manager.laplace(
        base_price=0.5,
        supply=supply,
        demand=demand,
        quantity=batch_1_quantity  # From cluster.auction_batches
        # market_offer=0 <-- REMOVED
    )
    
    print(f"\n💰 Result:")
    print(f"   Adjusted Price:  ${adjusted_price:.4f}B per unit")
    print(f"   Multiplier:      {adjusted_price / 0.5:.4f}x")
    print(f"   Status:          {'✓ ACCEPTED' if accepted else '✗ REJECTED'}")
    
    # Try with different batch
    print("\n" + "="*70)
    print("TRYING WITH BATCH 3")
    print("="*70)
    
    batch_3_quantity = cluster.auction_batches[4]
    print(f"   Quantity (Batch 3): {batch_3_quantity:.2f} billion barrels")
    
    adjusted_price_3, accepted_3 = manager.laplace(
        base_price=0.5,
        supply=supply,
        demand=demand,
        quantity=batch_3_quantity,  # Different batch quantity
        # market_offer=0 <-- REMOVED
    )
    
    print(f"\n💰 Result:")
    print(f"   Adjusted Price:  ${adjusted_price_3:.4f}B per unit")
    print(f"   Multiplier:      {adjusted_price_3 / 0.5:.4f}x")
    print(f"   Status:          {'✓ ACCEPTED' if accepted_3 else '✗ REJECTED'}")
