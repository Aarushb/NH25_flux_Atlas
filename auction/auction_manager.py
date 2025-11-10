import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math
import csv
import random
from models.country import Country
from models.cluster import ClusterInfo  
from models.cluster_enums import CountryClusters
from models.resourcess import Resource
from datetime import datetime
from auction import AuctionStatus, Bid, Auction 
import io
import time

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
    def laplace(base_price: float, supply: float, demand: float, quantity:float, min_b:int=1 , min_w:int=0.0001, k:int=0.4):
        """
        Calculates a country's max acceptable bid (v_value) for a given quantity.
        This is the "AI brain" for competitor bidders.
        """
        if base_price <= 0:
            raise ValueError("Base price must be > 0")
    
        if supply <= 0:
            max_increase = 1.0 
        else:
            max_increase = max(0.0, min(1.0, (demand / supply) - 1.0))
         
        b = max(abs(demand) * k, float(min_b))
    
        distance = abs(quantity - demand)
    
        w = math.exp(- distance / b)
    
        multiplier = 1.0 + max_increase * w
        v = base_price * multiplier
    
        if v < base_price:
            return v, False
            
        return v, True


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
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    print(f"  Total countries in all clusters: {total_countries_in_world}")
    print(f"  Distributing {total_quantity} units proportionally.")

    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world, seller=seller)
    
    print("\n[Phase 2: Verifying batch assignments...]")
    total_planned_quantity = 0.0
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
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
        
        sorted_batch_nums = sorted(cluster_info.auction_batches.keys())
        if not sorted_batch_nums:
            print("  No batches to process for this cluster.")
            continue

        for batch_num in sorted_batch_nums:
            quantity = cluster_info.get_batch_quantity(batch_num)
            
            if quantity is None or quantity == 0:
                continue 
            
            print(f"\n  --- Batch {batch_num} | Quantity: {quantity:.2f} {resource_unit} ---")

            epsilon = 1e-9
            if live_auction_stock < (quantity - epsilon):
                print(f"  SELLER STOCK LOW: Not enough auction stock for this batch (Needs: {quantity:.2f}, Has: {live_auction_stock:.2f}).")
                print(f"  AUCTION FOR {cluster_info.name} ENDED.")
                break 
            
            bids = [] 
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
                    print(f"    {country.name:<13}: Bid ACCEPTED (v_value: ${v_value:.4f}B)")
                    bids.append((v_value, country))
                else:
                    print(f"    {country.name:<13}: Bid REJECTED (v_value: ${v_value:.4f}B)")
            
            if not bids:
                print("    RESULT: No bids for this batch.")
                continue 
                
            bids.sort(key=lambda x: x[0], reverse=True)
            
            winner_bid_v_value, winner = bids[0]
            
            price_per_unit = 0.0
            
            if len(bids) == 1:
                print(f"    RESULT: Only one bidder ({winner.name}).")
                price_per_unit = base_price
                print(f"    Winner pays reserve (base) price.")
            else:
                second_highest_v_value = bids[1][0]
                price_per_unit = second_highest_v_value
                print(f"    RESULT: {len(bids)} bidders.")
                print(f"    Winner: {winner.name:<13} (Bid Value: ${winner_bid_v_value:.4f}B)")
                print(f"    Winner Pays (2nd Price): ${price_per_unit:.4f}B per unit")
            
            total_cost = price_per_unit * quantity
            
            if winner.budget < total_cost:
                print(f"    WINNER {winner.name} FAILED: Insufficient budget.")
                print(f"      Budget: ${winner.budget:.2f}B, Cost: ${total_cost:.2f}B")
                continue 
                
            print(f"    TRANSACTION:")
            print(f"      {winner.name:<13} pays ${total_cost:.2f}B")
            print(f"      {seller.name:<13} receives ${total_cost:.2f}B")

            winner.budget -= total_cost
            seller.budget += total_cost
            
            seller_resource.amount -= quantity
            live_auction_stock -= quantity 
            
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
                break 
        
        if live_auction_stock < epsilon:
            break # Stop 

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
    
    bidder_cluster = None
    for cluster_enum in CountryClusters:
        if bidder_country in cluster_enum.value.countries:
            bidder_cluster = cluster_enum.value
            break
    
    if not bidder_cluster:
        print(f"\nERROR: {bidder_country.name} not found in any cluster.")
        return
    
    print(f"Your Cluster: {bidder_cluster.name}")
    
    seller_resource = seller_country.get_resource(resource_name)
    if not seller_resource:
        print(f"\nERROR: Seller doesn't have {resource_name}")
        return
    
    resource_unit = seller_resource.unit
    
    your_demand_res = bidder_country.get_demand(resource_name)
    if not your_demand_res:
        print(f"\nWARNING: You have no demand for {resource_name}")
        your_demand = 0.0
    else:
        your_demand = your_demand_res.amount
        print(f"Your Demand: {your_demand:.2f} {resource_unit}")
    
    your_supply_res = bidder_country.get_resource(resource_name)
    your_supply = your_supply_res.amount if your_supply_res else 0.0
    print(f"Your Supply: {your_supply:.2f} {resource_unit}")
    
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world, seller=seller_country)
    
    print("\n" + "="*70)
    print("STARTING BIDDING ROUNDS")
    print("="*70)
    
    continue_bidding = True
    winning_prices_summary = {}
    your_wins = []
    
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
        
        print(f"\nOther bidders in your cluster:")
        all_other_bids = []
        
        for country in bidder_cluster.countries:
            if country.name == seller_country.name:
                continue  
            
            if country.name == bidder_country.name:
                continue  
            
            demand_res = country.get_demand(resource_name)
            if not demand_res or demand_res.amount <= 0:
                print(f"  {country.name:<15}: No demand, skipping")
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
                print(f"  {country.name:<15}: Bid ${v_value:.4f}B per unit (ACCEPTED)")
                all_other_bids.append((v_value, country))
            else:
                print(f"  {country.name:<15}: Bid ${v_value:.4f}B per unit (REJECTED)")
        
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
        
        my_bid_price = 0.0
        my_accepted = False
        
        try:
            my_bid_price_str = input(f"\nEnter your bid for Batch {batch_num} (per unit in $B, or 'pass' to skip): ").strip()
            
            if my_bid_price_str.lower() == 'pass':
                print(f"You passed on Batch {batch_num}.")
                my_accepted = False
                winning_prices_summary[f"Batch {batch_num}"] = "You PASSED"
            else:
                my_bid_price = float(my_bid_price_str)
                
                if my_bid_price < base_price:
                    print(f" Your bid ${my_bid_price:.4f}B is BELOW base price (${base_price:.4f}B). Bid REJECTED.")
                    my_accepted = False
                    winning_prices_summary[f"Batch {batch_num}"] = "Your bid REJECTED (too low)"
                else:
                    total_cost = my_bid_price * quantity
                    if bidder_country.budget < total_cost:
                        print(f" Insufficient budget! Need ${total_cost:.2f}B, Have ${bidder_country.budget:.2f}B. Bid REJECTED.")
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
            print(f"(Input not available, using suggested bid: ${your_laplace_bid:.4f}B)")
            my_bid_price = your_laplace_bid
            my_accepted = your_laplace_accepted
            if my_accepted:
                 print(f"✓ Your bid: ${my_bid_price:.4f}B per unit SUBMITTED.")
            else:
                 print(f" Your suggested bid was REJECTED.")

        
        all_bids = all_other_bids.copy()
        if my_accepted:
            all_bids.append((my_bid_price, bidder_country))
        
        if not all_bids:
            print(f"\n RESULT: No valid bids for Batch {batch_num}. Batch not sold.")
            winning_prices_summary[f"Batch {batch_num}"] = "No bids"
            continue
        
        all_bids.sort(key=lambda x: x[0], reverse=True)
        
        winner_v_value, winner = all_bids[0]
        
        if len(all_bids) == 1:
            price_per_unit = base_price
        else:
            price_per_unit = all_bids[1][0]  
        
        total_payment = price_per_unit * quantity
        winning_prices_summary[f"Batch {batch_num}"] = f"${price_per_unit:.4f}B per unit"
        
        print(f"\n{'='*70}")
        if winner.name == bidder_country.name:
            print(f" YOU WON BATCH {batch_num}! ")
            print(f"{'='*70}")
            print(f"Your Bid: ${my_bid_price:.4f}B per unit")
            print(f"You Pay (2nd price): ${price_per_unit:.4f}B per unit")
            print(f"Total Payment: ${total_payment:.2f}B")
            print(f"Quantity Received: {quantity:.2f} {resource_unit}")
            print(f"Budget After: ${bidder_country.budget - total_payment:.2f}B") 
            
            your_wins.append({
                'batch': batch_num,
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'total_payment': total_payment
            })
            
            try:
                choice = input(f"\nPress Enter to continue to next batch, or type 'exit' to stop: ").strip().lower()
                if choice == 'exit':
                    continue_bidding = False
                    print(f"You chose to exit. Skipping remaining batches.")
            except (EOFError, KeyboardInterrupt, RuntimeError):
                print(f"(Auto-continuing to next batch...)")
        else:
            print(f" YOU LOST BATCH {batch_num}")
            print(f"{'='*70}")
            print(f"Winner: {winner.name}")
            print(f"Winning Bid: ${winner_v_value:.4f}B per unit")
            print(f"Price Paid: ${price_per_unit:.4f}B per unit")
            if my_accepted:
                print(f"Your Bid: ${my_bid_price:.4f}B per unit")
                print(f"You were outbid!")
    
    print("\n" + "="*70)
    print(f"BIDDING SIMULATION COMPLETE - {bidder_country.name.upper()}")
    print("="*70)
    
    print(f"\nFinal Prices for All Batches:")
    for batch_name, price in winning_prices_summary.items():
        print(f"  {batch_name}: {price}")
    
    if your_wins:
        print(f"\n YOUR WINS:")
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
        print(f"\n You did not win any batches.")
    
    print("="*70)


def get_country_state(country: Country, resource_name: str) -> Dict:
    """Helper to capture the full state of a country for logging."""
    supply_res = country.get_resource(resource_name)
    demand_res = country.get_demand(resource_name)
    return {
        "name": country.name,
        "budget": country.budget,
        "supply": supply_res.amount if supply_res else 0.0,
        "demand": demand_res.amount if demand_res else 0.0
    }


def random_auction_loop_with_logging(
    logged_in_country_name: str = "Japan", 
    base_price: float = 0.5,
    log_file: str = "auction_simulation_log.csv"
):
    """
    Infinite loop that randomly picks countries to auction their resources.
    Logs all auction data to a CSV file instead of printing to terminal.
    
    Args:
        logged_in_country_name: Name of the country that's logged in (will be skipped)
        base_price: Base price for all auctions (default: 0.5B per unit)
        log_file: Path to the CSV log file (default: "auction_simulation_log.csv")
    """
    
    all_countries = []
    for cluster_enum in CountryClusters:
        all_countries.extend(cluster_enum.value.countries)
    
    print("="*70)
    print("RANDOM AUCTION LOOP - INFINITE SIMULATION WITH CSV LOGGING")
    print("="*70)
    print(f"Logged in as: {logged_in_country_name}")
    print(f"Total countries in pool: {len(all_countries)}")
    print(f"Base price for all auctions: ${base_price}B per unit")
    print(f"Logging to: {log_file}")
    print("\nStarting infinite auction loop... (Press Ctrl+C to stop)\n")
    
    csv_headers = [
        "auction_id", "timestamp", "cluster_name", "batch_num", "quantity_sold", "resource_name",
        "seller_name", "winner_name", "winning_price_per_unit", "total_cost",
        "seller_budget_before", "seller_budget_after",
        "seller_supply_before", "seller_supply_after",
        "winner_budget_before", "winner_budget_after",
        "winner_supply_before", "winner_supply_after",
        "winner_demand_before", "winner_demand_after"
    ]
    
    try:
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()
        print(f"✓ CSV file created: {log_file}\n")
    except IOError as e:
        print(f"[ERROR] Could not create CSV file: {e}. Exiting.")
        return

    auction_count = 0
    
    try:
        while True:
            auction_count += 1
            
            random_country = random.choice(all_countries)
            
            if random_country.name == logged_in_country_name:
                continue
            
            exportable_resources = random_country.get_export_resources()
            
            if not exportable_resources:
                continue
            
            random_resource_name = random.choice(exportable_resources)
            random_resource = random_country.get_resource(random_resource_name)
            print(random_resource)
            
            sell_percentage = random.uniform(0.09, 0.11)
            sell_quantity = random_resource.amount * sell_percentage
            
            if sell_quantity < 0.01:
                continue
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Auction #{auction_count}: {random_country.name} selling {sell_quantity:.2f} {random_resource.unit} of {random_resource_name}")
            
            transaction_rows = run_auction_and_capture_data(
                auction_id=auction_count,
                seller=random_country,
                resource_name=random_resource_name,
                total_quantity=sell_quantity,
                base_price=base_price
            )
            
            if transaction_rows:
                try:
                    with open(log_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=csv_headers)
                        writer.writerows(transaction_rows)
                    
                    total_profit = sum(row['total_cost'] for row in transaction_rows)
                    print(f"  → Profit: ${total_profit:.2f}B | Transactions: {len(transaction_rows)} | Logged to CSV\n")
                except IOError as e:
                    print(f"  → [ERROR] Could not write to CSV: {e}\n")

            time.sleep(1)  
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("SIMULATION STOPPED BY USER")
        print("="*70)
        print(f"Total auctions created: {auction_count}")
        print(f"Log saved to: {log_file}")


def run_auction_and_capture_data(auction_id: int, seller: Country, resource_name: str, total_quantity: float, base_price: float) -> List[Dict]:
    """
    Runs the auction simulation and captures detailed "before/after" data
    for every successful transaction. Suppresses console output.
    Returns a list of dictionaries, ready for the CSV writer.
    """
    
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    transaction_log_rows = []
    
    seller_resource = seller.get_resource(resource_name)
    
    if not seller_resource or seller_resource.amount < total_quantity:
        sys.stdout = old_stdout 
        return [] 
    
    resource_unit = seller_resource.unit
    
    
    total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
    
    for cluster_enum in CountryClusters:
        cluster_info = cluster_enum.value
        cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world, seller=seller)
    
    live_auction_stock = total_quantity
    epsilon = 1e-9
    
    try:
        for cluster_enum in CountryClusters:
            cluster_info = cluster_enum.value
            
            sorted_batch_nums = sorted(cluster_info.auction_batches.keys())
            if not sorted_batch_nums:
                continue
            
            for batch_num in sorted_batch_nums:
                quantity = cluster_info.get_batch_quantity(batch_num)
                
                if quantity is None or quantity == 0:
                    continue
                                
                if live_auction_stock < (quantity - epsilon):
                    break
                
                bids = []
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
                    
                    noise = random.uniform(0.97, 1.03)
                    v_value = v_value * noise
                    
                    if accepted:
                        bids.append((v_value, country))
                
                if not bids:
                    continue
                
                bids.sort(key=lambda x: x[0], reverse=True)
                winner_bid_v_value, winner = bids[0]
                
                price_per_unit = base_price if len(bids) == 1 else bids[1][0]
                total_cost = price_per_unit * quantity
                
                if winner.budget < total_cost:
                    continue
                
                seller_state_before = get_country_state(seller, resource_name)
                winner_state_before = get_country_state(winner, resource_name)

                winner.budget -= total_cost
                seller.budget += total_cost
                
                seller_resource.amount -= quantity
                live_auction_stock -= quantity
                
                winner_resource = winner.get_resource(resource_name)
                if winner_resource:
                    winner_resource.amount += quantity
                else:
                    winner.resources[resource_name] = Resource(amount=quantity, unit=resource_unit)
                
                winner_demand = winner.get_demand(resource_name)
                if winner_demand:
                    winner_demand.amount *= 0.5
                
                seller_state_after = get_country_state(seller, resource_name)
                winner_state_after = get_country_state(winner, resource_name)

                csv_row = {
                    "auction_id": auction_id,
                    "timestamp": datetime.now().isoformat(),
                    "cluster_name": cluster_info.name,
                    "batch_num": batch_num,
                    "quantity_sold": quantity,
                    "resource_name": resource_name,
                    "seller_name": seller.name,
                    "winner_name": winner.name,
                    "winning_price_per_unit": price_per_unit,
                    "total_cost": total_cost,
                    "seller_budget_before": seller_state_before['budget'],
                    "seller_budget_after": seller_state_after['budget'],
                    "seller_supply_before": seller_state_before['supply'],
                    "seller_supply_after": seller_state_after['supply'],
                    "winner_budget_before": winner_state_before['budget'],
                    "winner_budget_after": winner_state_after['budget'],
                    "winner_supply_before": winner_state_before['supply'],
                    "winner_supply_after": winner_state_after['supply'],
                    "winner_demand_before": winner_state_before['demand'],
                    "winner_demand_after": winner_state_after['demand']
                }
                transaction_log_rows.append(csv_row)
                
                if live_auction_stock < epsilon:
                    break
            
            if live_auction_stock < epsilon:
                break
    
    finally:
        sys.stdout = old_stdout
    
    return transaction_log_rows


if __name__ == '__main__':
    random_auction_loop_with_logging()
