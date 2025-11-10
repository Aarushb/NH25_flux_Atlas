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
    def laplace(base_price: float, supply: float, demand: float, quantity:float, min_b:int=1 , min_w:int=0.0001, k:int=0.1):
        """
        Calculates a country's max acceptable bid (v_value) for a given quantity.
        This is the "AI brain" for competitor bidders.
        """
        # 1. Handle invalid base price
        if base_price <= 0:
            raise ValueError("Base price must be > 0")
    
        # 2. Avoid division by zero
        if supply <= 0:
            # If no internal supply, max_increase is 1 (willing to pay up to 2x base)
            max_increase = 1.0 
        else:
            # If demand > supply, calculate increase. If supply > demand, cap at 0 (no increase).
            max_increase = max(0.0, min(1.0, (demand / supply) - 1.0))
         
        # 3. Compute b (sensitivity), ensure it never hits zero
        b = max(abs(demand) * k, float(min_b))
    
        # 4. Distance from ideal offer (demand)
        distance = abs(quantity - demand)
    
        # 5. Laplace decay weight
        w = math.exp(- distance / b)
    
        # 6. Compute final adjusted value (v_value)
        multiplier = 1.0 + max_increase * w
        v = base_price * multiplier
    
        # 7. Threshold accept/reject (must be at least base price)
        if v < base_price:
            return v, False
            
        return v, True

# --- MAIN SIMULATION LOGIC ---

def run_simulation(seller: Country, resource_name: str, total_quantity: float, base_price: float):
    """
    Runs the full Vickrey (second-price) auction simulation.
    
    This function uses helper methods from all other files:
    - `cluster_enums.py`: To loop through `CountryClusters`.
    - `cluster.py`: To call `assign_auction_quantity` which calculates batches (n-1 rule).
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
    # Use helper from cluster.py (country_count)
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    print(f"  Total countries in all clusters: {total_countries_in_world}")
    print(f"  Distributing {total_quantity} units proportionally.")

    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        # Use helper from cluster.py
        # --- [THIS IS THE FIX] ---
        # Pass the seller to the batch calculator
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world, seller=seller)
    
    print("\n[Phase 2: Verifying batch assignments...]")
    total_planned_quantity = 0.0
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        # Use helper from cluster.py (get_num_batches)
        print(f"  {cluster_info.name:<28}: Assigned {cluster_info.auction_quantity:6.2f} units (Batches: {cluster_info.get_num_batches()})")
        total_planned_quantity += cluster_info.auction_quantity
    print(f"  {'-'*28}: {'-'*6}")
    print(f"  {'Total Planned Quantity':<28}: {total_planned_quantity:6.2f} (Should match {total_quantity})")


    print("\n" + "="*70)
    print("STARTING BATCH AUCTIONS")
    print("="*70)

    live_auction_stock = total_quantity

    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        print(f"\n--- Processing Cluster: {cluster_info.name} ---")
        
        # Use helper from cluster.py (which uses n-1 rule)
        sorted_batch_nums = sorted(cluster_info.auction_batches.keys())
        if not sorted_batch_nums:
            print("  No batches to process for this cluster.")
            continue

        for batch_num in sorted_batch_nums:
            quantity = cluster_info.get_batch_quantity(batch_num)
            
            if quantity is None or quantity == 0:
                continue # Skip empty/invalid batches
            
            print(f"\n  --- Batch {batch_num} | Quantity: {quantity:.2f} {resource_unit} ---")

            # Use an epsilon for float comparison
            epsilon = 1e-9
            if live_auction_stock < (quantity - epsilon):
                print(f"  SELLER STOCK LOW: Not enough auction stock for this batch (Needs: {quantity:.2f}, Has: {live_auction_stock:.2f}).")
                print(f"  AUCTION FOR {cluster_info.name} ENDED.")
                break # Stop processing batches for this cluster
            
            bids = [] # List to store (v_value, country)
            for country in cluster_info.countries:
            
                if country.name == seller.name:
                    continue
                    
                # Use helper from country.py
                demand_res = country.get_demand(resource_name)
                if not demand_res or demand_res.amount <= 0:
                    continue
                    
                # Use helper from country.py
                supply_res = country.get_resource(resource_name)
                supply = supply_res.amount if supply_res else 0.0
                demand = demand_res.amount
                
                # Use local static method
                v_value, accepted = AuctionManager.laplace(
                    base_price=base_price,
                    supply=supply,
                    demand=demand,
                    quantity=quantity
                )
                
                if accepted:
                    print(f"    {country.name:<13}: Bid ACCEPTED (v_value: ${v_value:.4f}B)")
                    bids.append((v_value, country))
                else:
                    print(f"    {country.name:<13}: Bid REJECTED (v_value: ${v_value:.4f}B)")
            
            if not bids:
                print("    RESULT: No bids for this batch.")
                continue # Move to next batch
                
            bids.sort(key=lambda x: x[0], reverse=True)
            
            winner_bid_v_value, winner = bids[0]
            
            price_per_unit = 0.0
            
            if len(bids) == 1:
                print(f"    RESULT: Only one bidder ({winner.name}).")
                price_per_unit = base_price
                print(f"    Winner pays reserve (base) price.")
            else:
                # Vickrey: Winner pays second-highest bid
                second_highest_v_value = bids[1][0]
                price_per_unit = second_highest_v_value
                print(f"    RESULT: {len(bids)} bidders.")
                print(f"    Winner: {winner.name:<13} (Bid Value: ${winner_bid_v_value:.4f}B)")
                print(f"    Winner Pays (2nd Price): ${price_per_unit:.4f}B per unit")
            
            total_cost = price_per_unit * quantity
            
            # Updates directly reflect in the Country object
            if winner.budget < total_cost:
                print(f"    WINNER {winner.name} FAILED: Insufficient budget.")
                print(f"      Budget: ${winner.budget:.2f}B, Cost: ${total_cost:.2f}B")
                continue # Skip to next batch
                
            print(f"    TRANSACTION:")
            print(f"      {winner.name:<13} pays ${total_cost:.2f}B")
            print(f"      {seller.name:<13} receives ${total_cost:.2f}B")

            winner.budget -= total_cost
            seller.budget += total_cost
            
            seller_resource.amount -= quantity
            live_auction_stock -= quantity # Decrement live tracker
            
            winner_resource = winner.get_resource(resource_name)
            if winner_resource:
                winner_resource.amount += quantity
            else:
                winner.resources[resource_name] = Resource(amount=quantity, unit=resource_unit)
            
            print(f"    New Balances:")
            print(f"      {winner.name:<13}: Budget ${winner.budget:6.2f}B, {resource_name}: {winner.get_resource(resource_name).amount:.2f}")
            print(f"      {seller.name:<13}: Budget ${seller.budget:6.2f}B, {resource_name}: {seller_resource.amount:.2f}")
            print(f"      (Auction Stock Remaining: {live_auction_stock:.2f})")
            
            if live_auction_stock < epsilon:
                print(f"\n*** AUCTION ENDED: Total planned quantity ({total_quantity}) has been sold. ***")
                break # Stop processing batches
        
        if live_auction_stock < epsilon:
            break # Stop processing clusters

    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)


def run_bidding_simulation(
    bidder_country: Country,
    seller_country: Country,
    resource_name: str,
    total_quantity: float,
    base_price: float
):
    """
    Interactive bidding simulation where YOU are the bidder.
    This is a "dry run" and does not affect the simulation state.
    """
    
    print("\n" + "="*70)
    print(f"INTERACTIVE BIDDING SIMULATION - YOU ARE {bidder_country.name.upper()}")
    print("="*70)
    print(f"Seller: {seller_country.name}")
    print(f"Resource: {resource_name}")
    print(f"Total Quantity: {total_quantity}")
    print(f"Base Price: ${base_price:.4f}B per unit")
    print(f"Your Budget: ${bidder_country.budget:.2f}B")
    
    # Find which cluster the bidder is in
    bidder_cluster = None
    for cluster_enum in CountryClusters:
        if bidder_country in cluster_enum.value.countries:
            bidder_cluster = cluster_enum.value
            break
    
    if not bidder_cluster:
        print(f"\nERROR: {bidder_country.name} not found in any cluster.")
        return
    
    print(f"Your Cluster: {bidder_cluster.name}")
    
    # Get seller resource
    seller_resource = seller_country.get_resource(resource_name)
    if not seller_resource:
        print(f"\nERROR: Seller doesn't have {resource_name}")
        return
    
    resource_unit = seller_resource.unit
    
    # Get your demand
    your_demand_res = bidder_country.get_demand(resource_name)
    if not your_demand_res:
        print(f"\nWARNING: You have no demand for {resource_name}")
        your_demand = 0.0
    else:
        your_demand = your_demand_res.amount
        print(f"Your Demand: {your_demand:.2f} {resource_unit}")
    
    # Get your supply
    your_supply_res = bidder_country.get_resource(resource_name)
    your_supply = your_supply_res.amount if your_supply_res else 0.0
    print(f"Your Supply: {your_supply:.2f} {resource_unit}")
    
    # Calculate proportional distribution
    # This is a "dry run" so we re-calculate without affecting the "real" state
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        # --- [THIS IS THE FIX] ---
        # Pass the seller to the batch calculator
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world, seller=seller_country)
    
    print("\n" + "="*70)
    print("STARTING BIDDING ROUNDS")
    print("="*70)
    
    continue_bidding = True
    winning_prices_summary = {}
    your_wins = []
    
    # Process only batches in YOUR cluster
    # This correctly uses the n-1 rule from cluster.py
    sorted_batch_nums = sorted(bidder_cluster.auction_batches.keys())
    
    for batch_num in sorted_batch_nums:
        if not continue_bidding:
            print(f"\nYou chose to stop bidding. Remaining batches will be skipped.")
            break
        
        quantity = bidder_cluster.get_batch_quantity(batch_num)
        
        if quantity is None or quantity == 0:
            continue
        
        print(f"\n{'='*70}")
        print(f"ROUND {batch_num} - Batch Quantity: {quantity:.2f} {resource_unit}")
        print(f"{'='*70}")
        
        # Calculate Laplace bids for OTHER countries in your cluster
        print(f"\nOther bidders in your cluster:")
        all_other_bids = []
        
        for country in bidder_cluster.countries:
            if country.name == seller_country.name:
                continue  # Seller can't bid
            
            if country.name == bidder_country.name:
                continue  # Skip yourself, you'll bid manually
            
            demand_res = country.get_demand(resource_name)
            if not demand_res or demand_res.amount <= 0:
                print(f"  {country.name:<15}: No demand, skipping")
                continue
            
            supply_res = country.get_resource(resource_name)
            supply = supply_res.amount if supply_res else 0.0
            demand = demand_res.amount
            
            # Calculate Laplace bid
            v_value, accepted = AuctionManager.laplace(
                base_price=base_price,
                supply=supply,
                demand=demand,
                quantity=quantity
            )
            
            if accepted:
                print(f"  {country.name:<15}: Bid ${v_value:.4f}B per unit (ACCEPTED)")
                all_other_bids.append((v_value, country))
            else:
                print(f"  {country.name:<15}: Bid ${v_value:.4f}B per unit (REJECTED)")
        
        # Calculate YOUR suggested Laplace bid (for reference)
        your_laplace_bid, your_laplace_accepted = AuctionManager.laplace(
            base_price=base_price,
            supply=your_supply,
            demand=your_demand,
            quantity=quantity
        )
        
        print(f"\n{'='*70}")
        print(f"YOUR TURN TO BID")
        print(f"{'='*70}")
        print(f"Batch {batch_num} Details:")
        print(f"  Quantity: {quantity:.2f} {resource_unit}")
        print(f"  Base Price: ${base_price:.4f}B per unit")
        print(f"  Total Cost (if you pay base): ${base_price * quantity:.2f}B")
        print(f"  Your Budget: ${bidder_country.budget:.2f}B")
        print(f"  Your Suggested Bid (Laplace): ${your_laplace_bid:.4f}B per unit")
        if your_laplace_accepted:
            print(f"    (This bid would be ACCEPTED)")
        else:
            print(f"    (This bid would be REJECTED - below base price)")
        
        # Get YOUR manual bid
        my_bid_price = 0.0
        my_accepted = False
        
        try:
            # --- THIS IS THE INTERACTIVE PART ---
            # This will work on your local machine
            my_bid_price_str = input(f"\nEnter your bid for Batch {batch_num} (per unit in $B, or 'pass' to skip): ").strip()
            
            if my_bid_price_str.lower() == 'pass':
                print(f"You passed on Batch {batch_num}.")
                my_accepted = False
                winning_prices_summary[f"Batch {batch_num}"] = "You PASSED"
            else:
                my_bid_price = float(my_bid_price_str)
                
                if my_bid_price < base_price:
                    print(f"❌ Your bid ${my_bid_price:.4f}B is BELOW base price (${base_price:.4f}B). Bid REJECTED.")
                    my_accepted = False
                    winning_prices_summary[f"Batch {batch_num}"] = "Your bid REJECTED (too low)"
                else:
                    total_cost = my_bid_price * quantity
                    if bidder_country.budget < total_cost:
                        print(f"❌ Insufficient budget! Need ${total_cost:.2f}B, Have ${bidder_country.budget:.2f}B. Bid REJECTED.")
                        my_accepted = False
                        winning_prices_summary[f"Batch {batch_num}"] = "Your bid REJECTED (insufficient budget)"
                    else:
                        print(f"✓ Your bid: ${my_bid_price:.4f}B per unit SUBMITTED.")
                        my_accepted = True
        
        except ValueError:
            print(f"Invalid input. Assuming you 'pass' on Batch {batch_num}.")
            my_accepted = False
            winning_prices_summary[f"Batch {batch_num}"] = "Invalid input - PASSED"
        except (EOFError, KeyboardInterrupt, RuntimeError):
            # Fallback for non-interactive environments
            print(f"(Input not available, using suggested bid: ${your_laplace_bid:.4f}B)")
            my_bid_price = your_laplace_bid
            my_accepted = your_laplace_accepted
            if my_accepted:
                 print(f"✓ Your bid: ${my_bid_price:.4f}B per unit SUBMITTED.")
            else:
                 print(f"❌ Your suggested bid was REJECTED.")

        
        # Combine all bids
        all_bids = all_other_bids.copy()
        if my_accepted:
            all_bids.append((my_bid_price, bidder_country))
        
        # Run Vickrey auction
        if not all_bids:
            print(f"\n❌ RESULT: No valid bids for Batch {batch_num}. Batch not sold.")
            winning_prices_summary[f"Batch {batch_num}"] = "No bids"
            continue
        
        # Sort bids (highest first)
        all_bids.sort(key=lambda x: x[0], reverse=True)
        
        winner_v_value, winner = all_bids[0]
        
        # Determine price (Vickrey: 2nd price or base)
        if len(all_bids) == 1:
            price_per_unit = base_price
        else:
            price_per_unit = all_bids[1][0]  # 2nd highest
        
        total_payment = price_per_unit * quantity
        
        # Store winning price
        winning_prices_summary[f"Batch {batch_num}"] = f"${price_per_unit:.4f}B per unit"
        
        # Show result
        print(f"\n{'='*70}")
        if winner.name == bidder_country.name:
            print(f"🏆 YOU WON BATCH {batch_num}! 🏆")
            print(f"{'='*70}")
            print(f"Your Bid: ${my_bid_price:.4f}B per unit")
            print(f"You Pay (2nd price): ${price_per_unit:.4f}B per unit")
            print(f"Total Payment: ${total_payment:.2f}B")
            print(f"Quantity Received: {quantity:.2f} {resource_unit}")
            # Note: This is a dry run, so we don't change the "real" budget
            print(f"Budget After: ${bidder_country.budget - total_payment:.2f}B") 
            
            your_wins.append({
                'batch': batch_num,
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'total_payment': total_payment
            })
            
            # Ask if they want to continue
            try:
                choice = input(f"\nPress Enter to continue to next batch, or type 'exit' to stop: ").strip().lower()
                if choice == 'exit':
                    continue_bidding = False
                    print(f"You chose to exit. Skipping remaining batches.")
            except (EOFError, KeyboardInterrupt, RuntimeError):
                print(f"(Auto-continuing to next batch...)")
        else:
            print(f"❌ YOU LOST BATCH {batch_num}")
            print(f"{'='*70}")
            print(f"Winner: {winner.name}")
            print(f"Winning Bid: ${winner_v_value:.4f}B per unit")
            print(f"Price Paid: ${price_per_unit:.4f}B per unit")
            if my_accepted:
                print(f"Your Bid: ${my_bid_price:.4f}B per unit")
                print(f"You were outbid!")
    
    # Final Summary
    print("\n" + "="*70)
    print(f"BIDDING SIMULATION COMPLETE - {bidder_country.name.upper()}")
    print("="*70)
    
    print(f"\nFinal Prices for All Batches:")
    for batch_name, price in winning_prices_summary.items():
        print(f"  {batch_name}: {price}")
    
    if your_wins:
        print(f"\n🏆 YOUR WINS:")
        total_spent = 0.0
        total_quantity_won = 0.0
        for win in your_wins:
            print(f"  Batch {win['batch']}: {win['quantity']:.2f} {resource_unit} for ${win['total_payment']:.2f}B")
            total_spent += win['total_payment']
            total_quantity_won += win['quantity']
        print(f"\n  Total Won: {total_quantity_won:.2f} {resource_unit}")
        print(f"  Total Spent: ${total_spent:.2f}B")
        if total_quantity_won > 0:
             print(f"  Average Price: ${total_spent / total_quantity_won:.4f}B per unit")
    else:
        print(f"\n❌ You did not win any batches.")
    
    print("="*70)


# -----------------------------------------------------------------
# --- MAIN EXECUTION BLOCK ---
# -----------------------------------------------------------------
if __name__ == "__main__":
    
    # --- Setup: Find the 'live' Seller Country object ---
    # We must get the actual object from the enum, not a new instance
    seller_country = None
    # We find Russia in *any* cluster, just in case
    for cluster_enum in CountryClusters:
        for country in cluster_enum.value.countries:
             if country.name == "Russia":
                seller_country = country
                break
        if seller_country:
            break
    
    if not seller_country:
        print("Error: Seller country 'Russia' not found in any cluster.")
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
    
    # --- Run Simulation 1: The Seller's View ---
    TOTAL_AUCTION_QUANTITY = 50.0
    BASE_PRICE = 0.5
    run_simulation(
        seller=seller_country,
        resource_name="PETROLEUM",
        total_quantity=TOTAL_AUCTION_QUANTITY,
        base_price=BASE_PRICE
    )

    # --- Print Post-Seller-Sim State ---
    print("\n" + "="*70)
    print("POST-SIMULATION (SELLER'S VIEW) STATE")
    print("="*70)
    
    final_seller_budget = seller_country.budget
    # --- [BUG FIX 2: Was checking COAL] ---
    final_seller_resource = seller_country.get_resource('PETROLEUM') 
    final_seller_resource_amount = final_seller_resource.amount if final_seller_resource else 0.0
    
    print(f"--- Summary for Seller: {seller_country.name} ---")
    print(f"  Budget Change: ${initial_seller_budget:.2f}B  ->  ${final_seller_budget:.2f}B  (+${final_seller_budget - initial_seller_budget:.2f}B)")
    print(f"  PETROLEUM Change: {initial_seller_resource_amount:.2f}  ->  {final_seller_resource_amount:.2f}  (-{initial_seller_resource_amount - final_seller_resource_amount:.2f})")
    
    print("\n--- Final State for All Participants ---")
    for cluster_enum in CountryClusters:
        print(f"\n--- {cluster_enum.name} ---")
        # --- [BUG FIX 1: Was .values] ---
        for country in cluster_enum.value.countries:
            petrol = country.get_resource('PETROLEUM')
            petrol_amount = petrol.amount if petrol else 0.0
            print(f"  {country.name:<13} | Budget: ${country.budget:6.2f}B | PETROLEUM: {petrol_amount:.2f}")

    # --- Find a Bidder (Japan) for the new simulation ---
    bidder_country = None
    for cluster_enum in CountryClusters:
        for country in cluster_enum.value.countries:
            if country.name == "Japan":
                bidder_country = country
                break
        if bidder_country:
            break

    if bidder_country:
        # --- Run Simulation 2: The Bidder's View (Interactive) ---
        print("\n\n")
        print("="*70)
        print("NOW STARTING INTERACTIVE BIDDING SIMULATION")
        print("="*70)
        
        run_bidding_simulation(
            bidder_country=bidder_country,
            seller_country=seller_country,
            resource_name="PETROLEUM",
            total_quantity=TOTAL_AUCTION_QUANTITY,
            base_price=BASE_PRICE
        )

    print("\n--- SIMULATION SCRIPT END ---")
