import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math

# --- Models & Data ---
from models.resourcess import Resource
from models.country import Country
from models.cluster import ClusterInfo  
from models.cluster_enums import CountryClusters

# --- Auction Primitives (Not used in this sim) ---
from auction import AuctionStatus, Bid, Auction 

@dataclass
class AuctionManager:
    """
    Holds the state of auctions for a specific cluster.
    The main simulation logic is outside this class, but the
    laplace method is a static helper used by the simulation.
    """
    cluster: ClusterInfo
    auctions: List[Auction] = field(default_factory=list)
    
    @staticmethod
    def laplace(base_price: float, supply: float, demand: float, quantity:float, min_b:int=1 , min_w:int=0.0001, k:int=0.3) -> (float, bool):
        """
        Calculates a country's valuation (v_value) for a resource.
        This is the "bidder's brain" to decide its max bid.
        
        Returns:
            (v_value, accepted) - A tuple of the calculated max price and a
                                 boolean indicating if the bid is acceptable.
        """
        # 1. Handle invalid base price
        if base_price <= 0:
            raise ValueError("Base price must be > 0")
    
        # 2. Avoid division by zero
        if supply <= 0:
            max_increase = 1.0
        else:
            # Note: This logic might be flawed if demand < supply
            max_increase = min(1.0, (demand / supply) - 1.0)
            if max_increase < 0: # Handle cases where supply > demand
                max_increase = 0.0
         
        # 3. Compute b, ensure it never hits zero
        b = max(abs(demand) * k, float(min_b))
    
        # 4. Distance from ideal offer
        distance = abs(quantity - demand)
    
        # 5. Laplace decay weight
        w = math.exp(-distance / b)
    
        # 6. Compute final adjusted value (v_value)
        multiplier = 1.0 + max_increase * w
        v_value = base_price * multiplier
    
        # 7. Threshold accept/reject
        if w < min_w or v_value < base_price:
            return v_value, False
        return v_value, True

# --- MAIN SIMULATION LOGIC ---

def run_simulation(seller: Country, resource_name: str, total_quantity: float, base_price: float):
    """
    Runs the full Vickrey (second-price) auction simulation.
    
    This function uses helper methods from all other files:
    - `cluster_enums.py`: To loop through `CountryClusters`.
    - `cluster.py`: To call `assign_auction_quantity` which calculates batches.
    - `country.py`: To call `get_resource`/`get_demand` and update `budget`/`resources`.
    - `auction_manager.py`: To call `laplace` for bid decisions.
    """
    print(f"--- STARTING SIMULATION ---")
    print(f"  Seller: {seller.name}")
    print(f"  Resource: {resource_name}")
    print(f"  Total Quantity for Auction: {total_quantity}")
    print(f"  Base (Reserve) Price: ${base_price}B per unit")
    
    seller_resource = seller.get_resource(resource_name)

    if not seller_resource or seller_resource.amount < total_quantity:
        print(f"\nSIMULATION FAILED: Seller does not have enough {resource_name} to auction.")
        print(f"  Has: {seller_resource.amount if seller_resource else 0}, Needs: {total_quantity}")
        return

    resource_unit = seller_resource.unit
    
    print("\n[Phase 1: Calculating proportional distribution...]")
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    print(f"  Total countries in all clusters: {total_countries_in_world}")
    print(f"  Distributing {total_quantity} units proportionally.")

    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world)
    
    print("\n[Phase 2: Verifying batch assignments...]")
    total_planned_quantity = 0.0
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        print(f"  {cluster_info.name:<28}: Assigned {cluster_info.auction_quantity:6.2f} units")
        total_planned_quantity += cluster_info.auction_quantity
    print(f"  {'-'*28}: {'-'*6}")
    print(f"  {'Total Planned Quantity':<28}: {total_planned_quantity:6.2f} (Should match {total_quantity})")


    print("\n" + "="*70)
    print("STARTING BATCH AUCTIONS")
    print("="*70)

    live_auction_stock = total_quantity
    
    # Determine maximum number of batches across all clusters
    max_batches = max(len(cluster_enum.value.auction_batches) for cluster_enum in CountryClusters)
    
    print(f"\nTotal batches to process: {max_batches}")
    print("Processing all clusters batch-by-batch...\n")

    # NEW: Iterate batch-by-batch, then cluster-by-cluster within each batch
    for batch_num in range(1, max_batches + 1):
        print("\n" + "="*70)
        print(f"BATCH {batch_num} - PROCESSING ALL CLUSTERS")
        print("="*70)
        
        for cluster_enum in CountryClusters:
            cluster_info = cluster_enum.value
            
            # Check if this cluster has this batch number
            quantity = cluster_info.get_batch_quantity(batch_num)
            if quantity is None or quantity == 0:
                print(f"\n[{cluster_info.name}] - No Batch {batch_num}")
                continue
            
            print(f"\n--- {cluster_info.name} - Batch {batch_num} | Quantity: {quantity:.2f} {resource_unit} ---")

            if live_auction_stock < quantity:
                print(f"  SELLER STOCK LOW: Not enough auction stock for this batch (Needs: {quantity:.2f}, Has: {live_auction_stock:.2f}).")
                print(f"  AUCTION FOR {cluster_info.name} BATCH {batch_num} SKIPPED.")
                continue # Skip this cluster's batch and move to next cluster
            
            bids = [] # List to store (v_value, country)
            for country in cluster_info.countries:
            
                if country.name == seller.name:
                    continue
                    
                demand_res = country.get_demand(resource_name)
                if not demand_res or demand_res.amount <= 0:
                    continue
                    
                supply_res = country.get_resource(resource_name)
                supply = supply_res.amount if supply_res else 0.0
                demand = demand_res.amount
                
                v_value, accepted = AuctionManager.laplace(
                    base_price=base_price,
                    supply=supply,
                    demand=demand,
                    quantity=quantity
                )
                
                if accepted:
                    print(f"  {country.name:<13}: Bid ACCEPTED (v_value: ${v_value:.4f}B)")
                    bids.append((v_value, country))
                else:
                    print(f"  {country.name:<13}: Bid REJECTED (v_value: ${v_value:.4f}B)")
            
            if not bids:
                print("  RESULT: No bids for this batch.")
                continue # Move to next cluster
                
            bids.sort(key=lambda x: x[0], reverse=True)
            
            winner_bid_v_value, winner = bids[0]
            
            price_per_unit = 0.0
            
            if len(bids) == 1:
                print(f"  RESULT: Only one bidder ({winner.name}).")
                price_per_unit = base_price
                print(f"  Winner pays reserve (base) price.")
            else:
                # Vickrey: Winner pays second-highest bid
                second_highest_v_value = bids[1][0]
                price_per_unit = second_highest_v_value
                print(f"  RESULT: {len(bids)} bidders.")
                print(f"  Winner: {winner.name:<13} (Bid Value: ${winner_bid_v_value:.4f}B)")
                print(f"  Winner Pays (2nd Price): ${price_per_unit:.4f}B per unit")
            
            total_cost = price_per_unit * quantity
            
            # Updates directly reflect in the Country object
            if winner.budget < total_cost:
                print(f"  WINNER {winner.name} FAILED: Insufficient budget.")
                print(f"    Budget: ${winner.budget:.2f}B, Cost: ${total_cost:.2f}B")
                continue # Skip to next cluster
                
            print(f"  TRANSACTION:")
            print(f"    {winner.name:<13} pays ${total_cost:.2f}B")
            print(f"    {seller.name:<13} receives ${total_cost:.2f}B")

            winner.budget -= total_cost
            seller.budget += total_cost
            
            seller_resource.amount -= quantity
            live_auction_stock -= quantity # Decrement live tracker
            
            winner_resource = winner.get_resource(resource_name)
            if winner_resource:
                winner_resource.amount += quantity
            else:
                winner.resources[resource_name] = Resource(amount=quantity, unit=resource_unit)
            
            print(f"  New Balances:")
            print(f"    {winner.name:<13}: Budget ${winner.budget:6.2f}B, {resource_name}: {winner.get_resource(resource_name).amount:.2f}")
            print(f"    {seller.name:<13}: Budget ${seller.budget:6.2f}B, {resource_name}: {seller_resource.amount:.2f}")
            print(f"    (Auction Stock Remaining: {live_auction_stock:.2f})")

    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)


# -----------------------------------------------------------------
# --- MAIN EXECUTION BLOCK ---
# -----------------------------------------------------------------
if __name__ == "__main__":
    
    # --- Setup: Find the 'live' Seller Country object ---
    # We must get the actual object from the enum, not a new instance
    seller_country = None
    for country in CountryClusters.GROUP5.value.countries:
        if country.name == "Russia":
            seller_country = country
            break
    
    if not seller_country:
        print("Error: Seller country 'Russia' not found in GROUP5.")
        sys.exit(1)
        
    # --- Print Initial State ---
    print("="*70)
    print("PRE-SIMULATION STATE")
    print("="*70)
    
    # Store initial state for summary
    initial_seller_budget = seller_country.budget
    seller_petroleum = seller_country.get_resource('PETROLEUM')
    initial_seller_resource_amount = seller_petroleum.amount if seller_petroleum else 0.0
    
    print(f"Seller: {seller_country.name}")
    print(f"  Initial Budget: ${initial_seller_budget:.2f}B")
    if seller_petroleum:
        print(f"  Initial PETROLEUM: {initial_seller_resource_amount:.2f} {seller_petroleum.unit}")
    else:
        print("  Initial PETROLEUM: 0.0 (Data not found)")

    print("\nPotential Bidders (from all clusters):")
    for cluster_enum in CountryClusters:
        for country in cluster_enum.value.countries:
            if country.name == seller_country.name:
                continue
            demand_info = country.get_demand('PETROLEUM')
            if demand_info and demand_info.amount > 0:
                print(f"  - {country.name:<13} (Cluster: {cluster_enum.name}): Budget ${country.budget:6.2f}B, Demand: {demand_info.amount}")
    
    # --- Run the Simulation ---
    TOTAL_AUCTION_QUANTITY = 50.0
    run_simulation(
        seller=seller_country,
        resource_name="COAL",
        total_quantity=TOTAL_AUCTION_QUANTITY,  # Selling 50 billion barrels
        base_price=0.05        # Base price is $0.5B per unit
    )

    # --- Print Final State ---
    print("\n" + "="*70)
    print("POST-SIMULATION STATE")
    print("="*70)
    
    final_seller_budget = seller_country.budget
    final_seller_resource = seller_country.get_resource('PETROLEUM')
    final_seller_resource_amount = final_seller_resource.amount if final_seller_resource else 0.0
    
    print(f"--- Summary for Seller: {seller_country.name} ---")
    print(f"  Budget Change: ${initial_seller_budget:.2f}B  ->  ${final_seller_budget:.2f}B  (+${final_seller_budget - initial_seller_budget:.2f}B)")
    print(f"  PETROLEUM Change: {initial_seller_resource_amount:.2f}  ->  {final_seller_resource_amount:.2f}  (-{initial_seller_resource_amount - final_seller_resource_amount:.2f})")
    
    print("\n--- Final State for All Participants ---")
    for cluster_enum in CountryClusters:
        print(f"\n--- {cluster_enum.name} ---")
        for country in cluster_enum.value.countries:
            petrol = country.get_resource('PETROLEUM')
            petrol_amount = petrol.amount if petrol else 0.0
            print(f"  {country.name:<13} | Budget: ${country.budget:6.2f}B | PETROLEUM: {petrol_amount:.2f}")

    print("\n--- SIMULATION SCRIPT END ---")
